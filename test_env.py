from dotenv import load_dotenv
import os

load_dotenv()
required = [
    'GROQ_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
    'RECEIVER_EMAILS', 'SMTP_EMAIL', 'SMTP_PASSWORD'
]

all_ok = True
for key in required:
    value = os.getenv(key)
    status = "✅ Loaded" if value else "❌ Missing"
    length = f"(len {len(value)})" if value else ""
    print(f"{status} {key}: {length}")
    if not value:
        all_ok = False

emails = os.getenv('RECEIVER_EMAILS', '').split(',')
print(f"Emails count: {len([e for e in emails if e.strip()])}")

print("🎉 All OK - Run main.py!" if all_ok else "❌ Fix .env missing vars!")