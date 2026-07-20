# SIMPLE DEMO
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello!"}
    ])

print(response.content[0].text)