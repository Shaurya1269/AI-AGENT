from openai import OpenAI
from dotenv import load_dotenv
import os
from .explorer import build_context

from pathlib import Path
from .scanner import scan_directory

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)


def build_prompt(question, context):
    prompt = f"""
You are Antigravity, an AI code assistant and expert Python software engineer.

Answer the user's question using ONLY the provided code context.

IMPORTANT RULES:
- Do not assume or invent behavior that is not explicitly supported by the code.
- Base every claim about the code on the provided function body, definitions, references, or imports.
- If something cannot be determined from the provided context, explicitly say that it cannot be determined.
- Do not describe what the code "should" do. Describe what the code actually does.
- Pay close attention to variable types, return values, conditions, loops, and function calls and explain them with full clarity and precision when asked about them.
- If the code contains something unusual or potentially incorrect, mention what the code actually does rather than silently correcting it.
-Most importantly, do not hallucinate or make up information about the code. Only describe what is present in the provided context.

Question:
{question}

Code Context:
{context}

When answering:
- Explain the actual purpose of the function.
- Explain important parameters based on the function definition.
- Explain the return value based on the actual return statement.
- Explain important control flow when relevant.
- Mention where the function is defined and used if references are available.
- If imports are relevant, mention them.
- Keep the explanation concise unless the user asks for more detail.
- Never say that information cannot be determined if that information is explicitly present anywhere in the provided context.
- Before claiming something is unknown, check the function body, definitions, references, imports, and calls carefully.
"""
    return prompt


def ask_llm(prompt):  # send prompt to llm using openai api
    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        top_p=1,
        max_tokens=1000,
        seed=42,
        timeout=15
    )
    return response.choices[0].message.content


def answer_question(project_index, symbol, question):
    context = build_context(project_index, symbol)
    if not context:
        return "No context found for the given symbol."
    print(context)  # temporary
    prompt = build_prompt(question, context)
    answer = ask_llm(prompt)
    return answer


if __name__ == "__main__":
    project = Path(".")
    project_index = scan_directory(project)

    answer = answer_question(project_index, "scan_directory",
                             "what directories are ignored in this function?")
    
    print(answer)
    
    
@tool    