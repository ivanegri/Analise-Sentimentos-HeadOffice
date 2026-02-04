import requests
import os

# Configuration
#API_URL = 'http://216.22.5.204:5000/analyze'
API_URL = 'http://localhost:5000/analyze'

# List available PDFs
pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

if not pdf_files:
    print("No PDF files found in the current directory.")
else:
    print("Available PDFs:")
    for i, f in enumerate(pdf_files):
        print(f"  {i+1}. {f}")
    
    # Select the first one by default, or change index here
    selected_index = 0 
    filename = pdf_files[selected_index]
    
    print(f"\nAnalyzing file: {filename}")
    print(f"Sending to {API_URL}...")

    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                print("\nSuccess! Result:")
                print(response.json())
            else:
                print(f"\nError {response.status_code}:")
                print(response.text)
                
    except Exception as e:
        print(f"\nError: {e}")
