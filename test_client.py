import requests
import json

url = 'http://216.22.5.204:5000/analyze'
file_path = 'headoffice_ai_exported_data_2026-01-29T12_42_59.262Z.json'

print(f"Loading data from {file_path}...")
with open(file_path, 'r', encoding='utf-8') as f:
    payload = json.load(f)

# If the file is very large, we might want to test just the first item
# payload = payload[:1] # Uncomment to test only the first conversation
    

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("\nSuccess!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"\nError: {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("\nError: Could not connect to the API. Make sure 'run_api.sh' is running in another terminal.")
