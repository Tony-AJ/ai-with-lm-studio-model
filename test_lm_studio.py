import os
import requests
from dotenv import load_dotenv
import sys

load_dotenv()

def test_lm_studio():
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("OPENAI_API_BASE not found in .env")
        return

    print(f"Testing connectivity to: {api_base}")
    sys.stdout.flush()
    
    try:
        # Test /v1/models as requested by user
        # Adding a timeout to avoid hanging indefinitely
        url = f"{api_base}/models"
        print(f"Requesting {url}...")
        sys.stdout.flush()
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("Successfully connected to LM Studio API!")
            print("Available models:")
            models = response.json()
            for model in models.get('data', []):
                print(f" - {model.get('id')}")
        else:
            print(f"Failed to connect. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.Timeout:
        print("Error: Connection timed out. Is the LM Studio server running and reachable?")
    except requests.exceptions.ConnectionError:
        print(f"Error: Connection refused. Check if the IP {api_base} is correct and LM Studio is listening.")
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_lm_studio()
