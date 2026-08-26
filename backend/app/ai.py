from openai import OpenAI
from dotenv import load_dotenv
import os
from .explorer import (
    build_context,
    find_relevant_symbols,
    get_called_function_context,
)

from pathlib import Path
from .scanner import scan_directory
import json
from .search import search_index

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
        model="deepseek-ai/deepseek-v4-flash-0731sh-0731",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        top_p=1,
        max_tokens=1000,
        seed=42,
        timeout=15
    )
    return response.choices[0].message.content


def answer_question(project_index, question):
    return run_agent(project_index, question)


def get_symbol_context_tool(project_index, symbol):
    return build_context(project_index, symbol)


def test_tool_call():
    print("Starting tool test...")

    messages = [
        {
            "role": "user",
            "content": "How does the /scan endpoint ultimately build project_index?"
        }
    ]

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

    # FIRST LLM REQUEST
    response = client.chat.completions.create(
        model="deepseek-ai/deepseek-v4-flash-0731",
        messages=messages,
        tools=tools,
        temperature=0,
    )

    message = response.choices[0].message

    print("MODEL TOOL CALL:")
    print(message.tool_calls)

    # Add model's response to conversation
    messages.append(message)

    # Execute requested tools
    if message.tool_calls:

        for tool_call in message.tool_calls:

            if tool_call.function.name == "get_symbol_context":

                arguments = json.loads(tool_call.function.arguments)

                symbol = arguments["symbol"]

                print("MODEL REQUESTED SYMBOL:")
                print(symbol)

                # YOUR ACTUAL TOOL
                project = Path(".")
                project_index = scan_directory(project)

                result = build_context(project_index, symbol)

                print("TOOL RESULT:")
                print(result)

                # IMPORTANT:
                # Send tool result BACK to the model
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    }
                )

            elif tool_call.function.name == "search_index":

                arguments = json.loads(tool_call.function.arguments)
                query = arguments['query']
                result = search_code_tool(
                    project_index, query
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })

    # SECOND LLM REQUEST
    final_response = client.chat.completions.create(
        model="deepseek-ai/deepseek-v4-flash-0731",
        messages=messages,
        tools=tools,
        temperature=0,
    )

    answer = final_response.choices[0].message.content

    print("\nFINAL ANSWER:")
    print(answer)


def run_agent(project_index, question):

    if client is None:
        return "NVIDIA_API_KEY is not configured."

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_project",
                "description": (
                    "Search the project for relevant symbols, functions, "
                    "variables, imports, and references."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for in the project."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_symbol_context",
                "description": (
                    "Get detailed code context for a specific function. "
                    "Returns its definition, body, references, imports, "
                    "calls, and related functions."
                ),
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
        },
        {
            "type": "function",
            "function": {
                "name": "search_code",
                "description": (
                    "Search the project for code related to a query. "
                    "Use this when you do not know which function or symbol "
                    "contains the information needed to answer the question."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The code concept, symbol, or keyword to search for."
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": """
You are Antigravity, an AI code assistant.

Answer questions using the project's code.

You have two tools:

1. search_code
   Use this to discover relevant symbols, files, or code when you
   don't know where the answer is.

2. get_symbol_context
   Use this to inspect a specific function in detail, including its
   definition, body, references, imports, calls, variables, and
   called functions.

Use tools when necessary rather than guessing.

If a question mentions a function you already know, you may directly
use get_symbol_context.

If you don't know which part of the project is relevant, use
search_code first.

You may call multiple tools if necessary.

Do not invent behavior that is not supported by tool results.
"""
        },
        {
            "role": "user",
            "content": question
        }
    ]

    while True:

        response = client.chat.completions.create(
            model="deepseek-ai/deepseek-v4-flash-0731",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # Model has finished reasoning and produced an answer
        if not message.tool_calls:
            return message.content

        # Add model's tool request to conversation
        messages.append(message)

        # Execute every requested tool
        for tool_call in message.tool_calls:

            arguments = json.loads(
                tool_call.function.arguments
            )

            if tool_call.function.name in {"search_project", "search_code"}:

                query = arguments["query"]

                result = find_relevant_symbols(
                    project_index,
                    query
                )

            elif tool_call.function.name == "get_symbol_context":

                symbol = arguments["symbol"]

                result = get_symbol_context_tool(
                    project_index,
                    symbol
                )

            else:
                result = {
                    "error": f"Unknown tool: {tool_call.function.name}"
                }

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })


def get_symbol_context_tool(project_index, symbol):
    return build_context(project_index, symbol)


def get_called_function_context_tool(project_index, symbol):
    context = get_symbol_context_tool(project_index, symbol)

    if not context:
        return None

    calls = context.get("calls", [])
    return get_called_function_context(project_index, calls)


if __name__ == "__main__":
    project = Path(".")
    project_index = scan_directory(project)

    print("Starting tool test...")

    test_tool_call()

    print("Tool test finished.")


def search_code_tool(project_index, query):
    return search_index(project_index, query)


