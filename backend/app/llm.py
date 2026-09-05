from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY is not configured.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

MODEL = "deepseek/deepseek-chat-v3-0324"


def generate(messages, tools=None):
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": 1,
        "top_p": 1,
        "max_tokens": 1000,
        "seed": 42,
        "timeout": 15,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)

    return response.choices[0].message
