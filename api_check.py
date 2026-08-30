import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[
        {
            "role": "user",
            "content": "Explain what an AI agent is in simple terms."
        }
    ]
)

print("\nClaude response:")
print(response.content[0].text)