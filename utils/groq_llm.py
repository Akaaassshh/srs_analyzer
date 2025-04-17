import requests
from utils.config import GROQ_API_KEY


def llama3_chat(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2048,
    }

    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        response = res.json()
        print(response)
        return response["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Error: {res.status_code}, {res.text}")