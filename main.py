import time
from datetime import datetime, timezone
from dateutil import parser as date_parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from groq_api import translate_text
import re
import html


from truthbrush.api import Api
import requests
import logging

from dateutil import parser as date_parse
from datetime import timezone

from deep_translator import GoogleTranslator

def translate_google(text, source="en", target="vi"):
    return GoogleTranslator(source=source, target=target).translate(text)

# print(translate_google("The future is bright."))


logging.getLogger().handlers.clear()
logger = logging.getLogger("TRUMP")
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler("Running.DEBUG", mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Format log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Thêm handler vào logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Định nghĩa các hằng số
NUMBER_OF_POSTS_TO_FETCH = 1
SLEEP_TIME = 30  # giây

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

receiver_emails = os.getenv('RECEIVER_EMAILS', '').split(',') if os.getenv('RECEIVER_EMAILS') else []


def translate_libre(text, source="en", target="vi", api_url="https://libretranslate.de/translate"):
    try:
        response = requests.post(api_url, json={
            "q": text,
            "source": source,
            "target": target,
            "format": "text"
        }, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("translatedText", "")
    except requests.RequestException as e:
        return f"[Lỗi kết nối: {e}]"
    except Exception as e:
        return f"[Lỗi: {e}]"


def send_email(html_content):
    """Gửi email"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Bài viết của TRUMP trên Truth"
    msg["From"] = "halepython@gmail.com"
    msg["To"] = ", ".join(receiver_emails)

    msg.attach(MIMEText(html_content, "html"))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(os.getenv('SMTP_EMAIL'), os.getenv('SMTP_PASSWORD'))
    server.send_message(msg)
    server.quit()

def fetch_posts(api, username, latest_post):
    """Lấy các bài viết mới nhất"""
    full_timeline = list(
        api.pull_statuses(username=username, replies=False, verbose=True, since_id=latest_post)
    )
    return full_timeline
# def clean_html_for_telegram(text):
#     text = re.sub(r'</?(h[1-6]|p|div|span|strong)>', '', text)
#     text = re.sub(r'<br\s*/?>', '\n', text)
#     return text
def clean_html_for_telegram(text):
    if not text:
        return ""

    # 1. Loại bỏ một số thẻ không được Telegram hỗ trợ
    text = re.sub(r'</?(h[1-6]|p|div|span|strong|em|blockquote|section|article|header|footer)[^>]*>', '', text, flags=re.IGNORECASE)

    # 2. Thay <br> bằng xuống dòng
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # 3. Giải mã các entity HTML như &amp; &lt; ...
    text = html.unescape(text)

    # 4. Xóa các tag còn lại không mong muốn (tùy chọn)
    text = re.sub(r'<[^>]+>', '', text)  # Xóa bất kỳ thẻ HTML còn sót lại

    return text.strip()
def send_telegram(text):
    check = text.lower()
    if "congress" in check:
        return
    text=clean_html_for_telegram(text)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.debug("Gửi tin nhắn Telegram thành công.")
    except Exception as e:
        logger.debug(f"Lỗi gửi Telegram: {e}")
        logger.debug(f"Phản hồi: {response.text}")

def send_photos(photo_urls):
    photo_urls=clean_html_for_telegram(photo_urls)
    if not photo_urls:
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
    media = [{"type": "photo", "media": u} for u in photo_urls[:10]]  # 10pic/1times

    payload = {
        "chat_id": CHAT_ID,
        "media": str(media).replace("'", '"')
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.debug("Gửi nhiều ảnh thành công.")
    except Exception as e:
        logger.debug(f"Lỗi gửi ảnh: {e}")
        logger.debug(f"Phản hồi: {response.text}")

def send_video(video_url, caption=None):
    video_url=clean_html_for_telegram(video_url)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    payload = {
        "chat_id": CHAT_ID,
        "video": video_url,
        "caption": caption or "",
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.debug("Gửi video thành công.")
    except Exception as e:
        logger.debug(f"Lỗi gửi video: {e}")
        logger.debug(f"Phản hồi: {response.text}")
def process_post(post):
    """Xử lý bài viết, gửi Telegram và email"""

    # Parse thời gian
    latest_at = date_parse.parse(post["created_at"]).replace(tzinfo=timezone.utc)

    # --- TÁCH MEDIA dùng cho TELEGRAM ---
    media_attach = post.get("media_attachments", [])
    list_url_media_telegram = ""
    image_urls = []
    first_video_url = None

    for media in media_attach:
        media_type = media.get("type")
        url = media.get("url")

        if media_type == "image":
            image_urls.append(url)
            list_url_media_telegram += f'<a href="{url}">[Xem ảnh]</a>\n'
        elif media_type in ("video", "gifv"):
            if not first_video_url:
                first_video_url = url
            else:
                list_url_media_telegram += f'<a href="{url}">[Xem video]</a>\n'

    # --- TÁCH MEDIA dùng riêng cho EMAIL (giữ <img>) ---
    list_url_media_email = ""
    for media in media_attach:
        if media.get("type") == "image":
            url = media.get("url")
            list_url_media_email += f"<img src='{url}' width='500' height='300'><br>"
        elif media.get("type") in ("video", "gifv"):
            url = media.get("url")
            list_url_media_email += f'<a href="{url}">[Video]</a><br>'

    # Nội dung chính
    content_ascii = "".join(c for c in post.get("content", "") if c.isascii())
    if not content_ascii:
        return
    msg_plain = f"{post['created_at']}  TRUMP said:\n{content_ascii}"
    msg_html = f"📢 <b>{post['created_at']} - TRUMP said:</b>\n{content_ascii}"

    logger.debug(msg_plain)

    # Nếu dài → dịch
    if len(post["content"]) > 10:
        # prompt = (
        #     "Dịch câu sau sang tiếng Việt: " + msg_plain +
        #     "Bạn hãy đánh giá ngắn gọn ảnh hưởng của bài viết này lên thị trường tiền điện tử." +
        #     "Tách phần dịch và phần đánh giá"
        # )
        translated_msg = translate_text(msg_plain)

        telegram_msg = f"{msg_html}\n{list_url_media_telegram}\n<i>{translated_msg}</i>"
        email_msg = (
            f"<h3>{post['created_at']}  TRUMP said:</h3>"
            f"{content_ascii}<br>{list_url_media_email}"
            f"<hr><i>{translated_msg}</i>"
        )

    else:
        telegram_msg = f"{msg_html}\n{list_url_media_telegram}"
        email_msg = f"<h3>{post['created_at']}  TRUMP said:</h3>{content_ascii}<br>{list_url_media_email}"

    # Gửi telegram
    send_telegram(telegram_msg)

    # Gửi ảnh và video (hiển thị trực tiếp)
    if len(image_urls) >= 2:
        send_photos(image_urls)
    if first_video_url:
        send_telegram(f'<b>Video mới:</b>\n<a href="{first_video_url}">Xem video</a>')
        send_video(first_video_url, caption=msg_html)

    # Gửi email giữ nguyên định dạng
    try:
        send_email(email_msg)
    except Exception as e:
        logger.debug(f"Lỗi gửi email: {e}")
def main():
    api = Api()
    with open("post.txt", "r", encoding="utf-8") as f:
        for line in f:
            latest_post=str(line.strip())
            logger.info(f'Latest post st: {latest_post}')
    while True:
        full_timeline = fetch_posts(api, "realDonaldTrump", latest_post)
        if len(full_timeline) > 0:
            latest_post = full_timeline[0]["id"]
            with open("post.txt", "w", encoding="utf-8") as f:
                f.write(f"{latest_post}")
            logger.info(f'Save latest post: ==> {latest_post}')
            for post in reversed(full_timeline):
                process_post(post)
        time.sleep(SLEEP_TIME)
        logger.debug(f'Delay 30s')

if __name__ == "__main__":
    main()