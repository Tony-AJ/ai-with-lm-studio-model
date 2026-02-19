import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_lm_studio():
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("OPENAI_API_BASE not found in .env")
        return

    print(f"Testing connectivity to: {api_base}")
    try:
        # Test /v1/models as requested by user
        response = requests.get(f"{api_base}/models")
        if response.status_code == 200:
            print("Successfully connected to LM Studio API!")
            print("Available models:")
            models = response.json()
            for model in models.get('data', []):
                print(f" - {model.get('id')}")
        else:
            print(f"Failed to connect. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_lm_studio()
