import os

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def format_task(task):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""You are a professional corporate assistant writing daily work reports for JadeQuest.

Convert the user's rough notes into:
1. Task Type — short professional title (3–8 words)
2. Professional Update — full sentence(s) describing work done, like:
   "I worked on ..." or "Today I have ..."

Rules:
- Use clear, professional English. Fix grammar.
- Task Type goes in the "Task type" column; the update goes in the "Task" column.
- Match tone of corporate daily reports.
- Output ONLY in this exact format (two lines):

Task Type: <short title>
Professional Update: <full professional description>

User notes:
{task}
"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "temperature": 0.3,
        "messages": [{"role": "user", "content": prompt}],
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    return data["choices"][0]["message"]["content"]


def parse_ai_response(ai_response):
    task_type = ""
    professional_update = ""

    for line in ai_response.split("\n"):
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("task type:"):
            task_type = line.split(":", 1)[1].strip()
        elif lower.startswith("professional update:"):
            professional_update = line.split(":", 1)[1].strip()

    if not task_type or not professional_update:
        raise ValueError("AI response missing Task Type or Professional Update")

    return task_type, professional_update
