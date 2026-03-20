import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ScaleDownClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("SCALEDOWN_API_KEY")
        self.url = "https://api.scaledown.xyz/compress/raw/"
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def compress_context(self, context, prompt, model="gpt-4o", rate="auto"):
        """
        Compresses the context using the ScaleDown API.
        Returns (result_dict, error_string)
        """
        payload = {
            "context": context,
            "prompt": prompt,
            "model": model,
            "scaledown": {
                "rate": rate
            }
        }
        
        try:
            response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                return None, result["error"]
            return result, None
        except Exception as e:
            return None, str(e)

    def get_compressed_content(self, context, prompt):
        """
        Legacy helper maintained for compatibility.
        """
        return self.compress_context(context, prompt)
