from openai import OpenAI
from dotenv import load_dotenv
import os
from explorer import build_context

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


def build_prompt(question, context):
    prompt = f"""
You are Antigravity, an AI code assistant and expert Python software engineer.

Answer the user's question using ONLY the provided code context.
If the answer cannot be determined from the context, say so instead of guessing.

Question:
{question}

Code Context:
{context}

When answering:
- Explain the purpose clearly.
- Mention important parameters if relevant.
- Mention the return value if relevant.
- Mention where the function is used if references are available.
- Keep the explanation concise unless the user requests more detail.
"""
    return prompt


def ask_llm(prompt):  # send prompt to llm using openai api
    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        top_p=1,
        max_tokens=50,
        seed=42,
        timeout=15
    )
    return response.choices[0].message.content


def answer_question(project_index, symbol, question):
    context = build_context(project_index, symbol)
    if not context:
        return "No context found for the given symbol."
    prompt = build_prompt(question, context)
    answer = ask_llm(prompt)

    return answer


# if __name__ == "__main__":
#     answer = ask_llm("Explain  what is the meaning of the name shaurya")
#     print(answer)
