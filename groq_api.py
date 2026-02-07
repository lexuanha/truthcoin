import os
from dotenv import load_dotenv
load_dotenv()  # Load .env FIRST!

from groq import Groq

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("🚫 GROQ_API_KEY missing! Edit .env")
        _client = Groq(api_key=api_key)
    return _client

def translate_text(text):
    client = get_client()  # Lazy safe!
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