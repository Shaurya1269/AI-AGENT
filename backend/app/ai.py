from openai import OpenAI
from dotenv import load_dotenv
import os
from .explorer import build_context, find_relevant_symbols

from pathlib import Path
from .scanner import scan_directory
import json

load_dotenv()
api_key = os.getenv("NVIDIA_API_KEY")
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
) if api_key else None


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
    if client is None:
        return "NVIDIA_API_KEY is not configured."
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


def answer_question(project_index, question):
    symbols = find_relevant_symbols(project_index, question)

    if not symbols:
        return "I could not identify any relevant function in the project.Please try a different question."

    contexts = {}

    for symbol in symbols:
        context = build_context(project_index, symbol)

        if context:
            contexts[symbol] = context

    if not contexts:
        return "I found relevant symbols, but could not build context for them."

    prompt = build_prompt(question, contexts)
    return ask_llm(prompt)


def get_symbol_context_tool(project_index, symbol):
    return build_context(project_index, symbol)


def test_tool_call(project_index):

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_symbol_context",
                "description": "Get detailed information about a function in the project.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "The function name to inspect."
                        }
                    },
                    "required": ["symbol"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "What does scan_directory do?"
        }
    ]

    response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    print("MODEL TOOL CALL:")
    print(message.tool_calls)

    if not message.tool_calls:
        print("Model did not request a tool.")
        return

    tool_call = message.tool_calls[0]

    arguments = json.loads(tool_call.function.arguments)
    symbol = arguments["symbol"]

    print("\nMODEL REQUESTED:")
    print(symbol)

    # Add the assistant's tool-call message to the conversation
    messages.append(message)

    # Execute our actual Python function
    result = get_symbol_context_tool(project_index, symbol)

    # Give the result back to the model
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result)
    })

    print("\nSending tool result back to model...")

    final_response = client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=messages,
        tools=tools
    )

    final_message = final_response.choices[0].message

    print("\nFINAL ANSWER:")
    print(final_message.content)
    
    
        
if __name__ == "__main__":
    project = Path(".")
    project_index = scan_directory(project)

    print("Starting tool test...")

    test_tool_call(project_index)

    print("Tool test finished.")