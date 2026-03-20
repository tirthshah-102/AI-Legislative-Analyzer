import requests
import json

url = "http://localhost:5000/ask"

payload = {
    "text": "The Legislative AI project was started in 2026. The main developer is Alice.",
    "question": "What is the capital of France?",
    "language": "English"
}

r = requests.post(url, json=payload)
print(r.json())
