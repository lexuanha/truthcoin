import os

from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def translate_text(text):
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


# print(translate_text("Hello, how are you? This is a test message."))