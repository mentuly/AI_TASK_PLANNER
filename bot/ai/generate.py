import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_plan(task: str):
    prompt = f"""
You are a planning assistant.

Break this task into steps.

Return ONLY valid JSON:
[
  {{
    "title": string,
    "description": string,
    "minutes": number
  }}
]

Task: {task}
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        return []