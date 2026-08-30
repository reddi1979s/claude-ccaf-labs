import os
import anthropic

# Create Anthropic client
client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

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

# Get task from user
user_task = input("\nEnter your task: ")

# Send task to Claude
response = client.messages.create(
    model="claude-haiku-4-5",
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