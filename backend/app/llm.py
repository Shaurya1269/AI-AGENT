from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)if api_key else None

MODEL = "deepseek-ai/deepseek-v4-flash-0731"


def generate(messages, tools=None):
    if client is None:
        return None

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto" if tools else None,
        temperature=1,
        top_p=1,
        max_tokens=1000,
        seed=42,
        timeout=15
    )
    return response.choices[0].message
