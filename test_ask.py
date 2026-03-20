import requests
import json

url = "http://localhost:5000/ask"
payload1 = {
    "text": "The Legislative AI project was started in 2026. The main developer is Alice. The project aims to simplify legal documents.",
    "question": "Who is the main developer?",
    "language": "English"
}

payload2 = {
    "text": "The Legislative AI project was started in 2026. The main developer is Alice. The project aims to simplify legal documents.",
    "question": "What is the capital of France?",
    "language": "English"
}

try:
    print("Test 1: Asking a question that IS in the document...")
    r1 = requests.post(url, json=payload1)
    print("Response 1:", json.dumps(r1.json(), indent=2))
    
    print("\nTest 2: Asking a question that IS NOT in the document...")
    r2 = requests.post(url, json=payload2)
    print("Response 2:", json.dumps(r2.json(), indent=2))
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to localhost:5000. Is the server running?")
