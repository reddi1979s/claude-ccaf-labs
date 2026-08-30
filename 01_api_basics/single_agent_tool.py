import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

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


user_task = input(
    "\nEnter your task "
    "(example: Review deployment.yaml): "
)

messages = [
    {
        "role": "user",
        "content": user_task
    }
]

# First request to Claude
response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=1500,
    system=SYSTEM_PROMPT,
    tools=tools,
    messages=messages
)

# Agent/tool loop
while response.stop_reason == "tool_use":

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

            if block.name == "read_file":

                filename = block.input["filename"]

                print(f"Reading file: {filename}")

                result = read_file(filename)

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

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages
    )


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