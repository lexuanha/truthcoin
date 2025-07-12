import time
from datetime import datetime, timezone
from dateutil import parser as date_parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from groq import Groq

from truthbrush.api import Api

# Định nghĩa các hằng số
NUMBER_OF_POSTS_TO_FETCH = 1
SLEEP_TIME = 30  # giây

# Định nghĩa các biến
receiver_emails = ["hale0972718598@gmail.com", "huyhajhuoc2@gmail.com"]
client = Groq(
    api_key="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"
)

def translate_text(text):
    """Dịch văn bản sang tiếng Việt"""
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Translate the following text to Vietnamese: " + text,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def send_email(html_content):
    """Gửi email"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Bài viết của TRUMP trên Truth"
    msg["From"] = "halepython@gmail.com"
    msg["To"] = ", ".join(receiver_emails)

    # Đính kèm phần HTML
    msg.attach(MIMEText(html_content, "html"))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("halepython@gmail.com", "fict xpaw mrwr rrhj")
    server.send_message(msg)
    server.quit()

def fetch_posts(api, username, latest_post):
    """Lấy các bài viết mới nhất"""
    full_timeline = list(
        api.pull_statuses(username=username, replies=False, verbose=True, since_id=latest_post)
    )
    return full_timeline

def process_post(post):
    """Xử lý bài viết"""
    latest_at = date_parse.parse(post["created_at"]).replace(tzinfo=timezone.utc)
    media_attach = post["media_attachments"]
    list_url_media = ""
    if len(media_attach) > 0:
        for media in media_attach:
            if media["type"] == 'image':
                url = media["url"]
                list_url_media += f"<img src='{url}' width='500' height='300'><br>"

    msg = "<h3>" + post["created_at"] + "  TRUMP said:</h3>" + "".join(c for c in post["content"] if c.isascii())
    print(msg)
    if len(post["content"]) > 10:
        translated_msg = translate_text("Dịch câu sau sang tiếng Việt: " + msg + ".\n Bạn hãy đánh giá một cách ngắn gọn ảnh hưởng của bài viết của TRUMP này lên thị trường tiền điện tử như thế nào?")
        send_email(msg + list_url_media + "\n" + translated_msg)
    else:
        send_email(msg + list_url_media)

def main():
    api = Api()
    latest_post = "114837554019633896"
    while True:
        full_timeline = fetch_posts(api, "realDonaldTrump", latest_post)
        if len(full_timeline) > 0:
            latest_post = full_timeline[0]["id"]
            for post in reversed(full_timeline):
                process_post(post)
        else:
            print("Nothing new in last 30s")
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    main()