from sentiment import SentimentAnalyzer

# Test with simple message format
test_messages = [
    {"id": 1, "message": "Você é um incompetente! Equipe de lixo!"},
    {"id": 2, "message": "VOCÊS SÃO GÊNIOS! Resultado SENSACIONAL! ⭐⭐⭐⭐⭐"},
    {"id": 3, "message": "Bom dia, poderia informar o status do pedido?"},
]

print("Testing local sentiment analyzer with new format:\n")
for msg in test_messages:
    result = SentimentAnalyzer.analyze_conversation(msg)
    print(f"Message: {msg['message'][:50]}...")
    print(f"Result: {result['sentiment_label']} (Score: {result['score']})")
    print("-" * 60)
