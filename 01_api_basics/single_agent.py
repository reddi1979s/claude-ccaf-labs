import os
import sys

import anthropic

# Agent instructions
SYSTEM_PROMPT = """
You are a helpful AI DevOps agent.

Your responsibilities:
1. Understand the user's request.
2. Analyze the problem.
3. Provide a clear solution.
4. Explain your reasoning at a high level.
5. Do not modify files or execute commands.
"""

MODEL = "claude-haiku-4-5"


def main():
    # Fail fast with a friendly message if the API key is missing
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            'Set it first, e.g.:  set ANTHROPIC_API_KEY=sk-ant-...'
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Get task from user
    user_task = input("\nEnter your task: ").strip()
    if not user_task:
        sys.exit("No task provided — exiting.")

    # Send task to Claude
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_task
            }
        ]
    )

    # Display response
    print("\n" + "=" * 60)
    print("SINGLE AGENT RESPONSE")
    print("=" * 60)

    for block in response.content:
        if block.type == "text":
            print(block.text)

    print("\n" + "=" * 60)
    print("API INFORMATION")
    print("=" * 60)

    print("Model:", response.model)
    print("Input tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Stop reason:", response.stop_reason)


if __name__ == "__main__":
    main()
