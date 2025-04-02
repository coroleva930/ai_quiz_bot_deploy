from openai import OpenAI
from config import PROXY_API_KEY, PROXY_API_URL

client = OpenAI(api_key=PROXY_API_KEY, base_url=PROXY_API_URL)

def ask_gpt(question_text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Ты эксперт по AI, объясняй просто. Дай подсказку"},
                  {"role": "user", "content": question_text}]
    )
    return response.choices[0].message.content
