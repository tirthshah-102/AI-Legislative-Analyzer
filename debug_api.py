import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://api.scaledown.xyz/compress/raw/"
headers = {
    'x-api-key': os.getenv("SCALEDOWN_API_KEY"),
    'Content-Type': 'application/json'
}

payload = {
    "context": "The Public Health Act requires all citizens to wear masks in public places to prevent the spread of respiratory diseases. Failure to comply may result in a fine of 500 rupees.",
    "prompt": "Summarize this for a citizen.",
    "model": "gpt-4o",
    "scaledown": {
        "rate": "auto"
    }
}

print("Sending request to ScaleDown API...")
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(f"Status Code: {response.status_code}")
print("Response JSON:")
print(json.dumps(response.json(), indent=2))
