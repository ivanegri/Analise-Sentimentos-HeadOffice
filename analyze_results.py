import requests
import json
import pandas as pd

# Configuration
#API_URL = 'http://216.22.5.204:5000/analyze'
API_URL = 'http://localhost:5000/analyze'
INPUT_FILE = 'headoffice_ai_exported_data_2026-01-29T12_57_37.700Z.json'

def main():
    print(f"1. Loading data from {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: File not found.")
        return

    print(f"2. Sending {len(data)} conversations to API (in batches)...")
    
    results = []
    batch_size = 50  # Send 50 items at a time to avoid timeout
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        print(f"   Processing batch {i//batch_size + 1} ({len(batch)} items)...", end='', flush=True)
        
        try:
            response = requests.post(API_URL, json=batch)
            if response.status_code == 200:
                results.extend(response.json())
                print(" Done.")
            else:
                print(f" Error: {response.status_code}")
                # Optional: continue or break? Let's continue to save partial results
        except Exception as e:
            print(f" Error: {e}")

    if not results:
        print("No results obtained.")
        return

    # 3. Generating DataFrame
    print("3. Generating Pandas DataFrame...")
    df = pd.DataFrame(results)

    # 4. Analysis
    print("\n" + "="*40)
    print("       SENTIMENT ANALYSIS REPORT       ")
    print("="*40)
    
    print(f"\nTotal Conversations: {len(df)}")
    
    print("\n--- Sentiment Distribution ---")
    dist = df['sentiment_label'].value_counts(normalize=True) * 100
    counts = df['sentiment_label'].value_counts()
    
    summary_df = pd.DataFrame({'Count': counts, 'Percentage (%)': dist.round(1)})
    print(summary_df)
    
    print("\n--- Score Statistics ---")
    print(df['score'].describe().round(1))
    
    # 5. Exporting
    output_filename = 'sentiment_analysis_results.csv'
    df.to_csv(output_filename, index=False)
    print(f"\n[Saved] Detailed results saved to '{output_filename}'")
    
    # Example Preview
    print("\n--- Low Score Examples (Negative) ---")
    negatives = df[df['sentiment_label'] == 'Negative']
    if not negatives.empty:
        print(negatives.head(3))
    else:
        print("No negative sentiments found.")

if __name__ == '__main__':
    main()
