import os
import sys

import anthropic

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = """
You are a Kubernetes security and reliability review agent.

Your job is to:
1. Read the Kubernetes YAML file using the available tool.
2. Analyze only the information present in the file.
3. Identify security issues.
4. Identify reliability issues.
5. Identify best-practice recommendations.
6. Clearly distinguish facts from recommendations.
7. Do not claim something is missing if it exists in the YAML.
"""

# Tool definition
tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a local text file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to read"
                }
            },
            "required": ["filename"]
        }
    }
]


def read_file(filename):
    """Read a local file."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {e}"


# Map tool names → functions so dispatch stays data-driven
TOOL_REGISTRY = {
    "read_file": read_file,
}

# Safety cap only — the primary stop condition is stop_reason == "end_turn"
MAX_ITERATIONS = 10


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            'Set it first, e.g.:  set ANTHROPIC_API_KEY=sk-ant-...'
        )

    client = anthropic.Anthropic(api_key=api_key)

    user_task = input(
        "\nEnter your task "
        "(example: Review deployment.yaml): "
    ).strip()
    if not user_task:
        sys.exit("No task provided — exiting.")

    messages = [
        {
            "role": "user",
            "content": user_task
        }
    ]

    response = None
    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )

        # Agent is done when it stops asking for tools
        if response.stop_reason != "tool_use":
            break

        messages.append(
            {
                "role": "assistant",
                "content": response.content
            }
        )

        tool_results = []

        for block in response.content:

            if block.type == "tool_use":

                print(f"\nAgent requested tool: {block.name}")

                tool_fn = TOOL_REGISTRY.get(block.name)

                if tool_fn is None:
                    # Unknown tool — tell the model instead of silently
                    # skipping it (which would send an empty tool_results
                    # list and trigger an API error)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "is_error": True,
                            "content": (
                                f"Unknown tool '{block.name}'. "
                                f"Available tools: {sorted(TOOL_REGISTRY)}"
                            )
                        }
                    )
                    continue

                print(f"Tool input: {block.input}")
                result = tool_fn(**block.input)

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": tool_results
            }
        )
    else:
        print(f"\nWarning: hit safety cap of {MAX_ITERATIONS} iterations.")

    # Display final answer
    print("\n" + "=" * 70)
    print("SINGLE AGENT + FILE TOOL RESPONSE")
    print("=" * 70)

    for block in response.content:
        if block.type == "text":
            print(block.text)

    print("\n" + "=" * 70)
    print("API INFORMATION")
    print("=" * 70)

    print("Model:", response.model)
    print("Input tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Stop reason:", response.stop_reason)


if __name__ == "__main__":
    main()
