import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('MISTRAL_API_KEY')
print(f"Testing Mistral AI connection...")
print(f"API Key present: {bool(api_key)}")

if api_key:
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-tiny",
                "messages": [{"role": "user", "content": "Say hello!"}]
            }
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Success! Response:")
            print(response.json()['choices'][0]['message']['content'])
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Network or exception error: {e}")
else:
    print("MISTRAL_API_KEY is missing from environment")
