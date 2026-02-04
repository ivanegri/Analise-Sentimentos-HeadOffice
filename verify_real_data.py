import json
from sentiment import SentimentAnalyzer

path = 'headoffice_ai_exported_data_2026-01-29T12_42_59.262Z.json'

print(f"Reading {path}...")
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Analyze first 5 conversations
    print("\nAnalyzing first 5 conversations:\n")
    for i, item in enumerate(data[:5]):
        result = SentimentAnalyzer.analyze_conversation(item)
        print(f"Conversation {i+1} ID: {item.get('_id')}")
        print(f"Score: {result['score']}")
        print(f"Label: {result['sentiment_label']}")
        print("-" * 30)
        
except FileNotFoundError:
    print(f"File {path} not found.")
except Exception as e:
    print(f"Error: {e}")
