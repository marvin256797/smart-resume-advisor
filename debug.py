import os

os.environ["GROQ_API_KEY"] = "YOUR_GROQ_KEY_HERE"

from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_API_KEY"]
)

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",  # Changed this line
    messages=[{"role": "user", "content": "Say 'Hello, Groq setup works!'"}]
)

print(response.choices[0].message.content)
