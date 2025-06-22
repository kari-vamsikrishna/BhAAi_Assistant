import requests

try:
    response = requests.post("http://localhost:4891/v1/chat/completions", json={
        "model": "DeepSeek-R1-Distill-Qwen-1.5B",  # replace with your actual model name
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ],
        "temperature": 0.7
    })

    print("Status Code:", response.status_code)
    print("Raw Text:", response.text)
    print("Parsed JSON:", response.json()["choices"][0]["message"]["content"])

except Exception as e:
    print("❌ Error:", e)
