import openai

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

print("Testing Ollama connection...")
try:
    response = client.chat.completions.create(
        model="gemma3:12b",
        messages=[
            {"role": "user", "content": "Hello, are you working?"}
        ]
    )
    print(f"SUCCESS: Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: {e}")
