import json
import pandas as pd

# Load original data with ground truth labels
with open('conversas_whatsapp.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# Load analysis results
results_df = pd.read_csv('sentiment_analysis_results.csv')

# Create DataFrame from original data
original_df = pd.DataFrame(original_data)

# Merge by ID
merged = pd.merge(
    original_df,
    results_df,
    on='id',
    how='inner'
)

print("="*70)
print("      MODELO DE SENTIMENTO - ANÁLISE DE PERFORMANCE")
print("="*70)

print(f"\nTotal de conversas analisadas: {len(merged)}\n")

# Group by real sentiment and show statistics
print("--- SCORES MÉDIOS POR CATEGORIA REAL ---\n")
score_stats = merged.groupby('sentiment')['score'].agg(['mean', 'std', 'min', 'max', 'count'])
score_stats = score_stats.round(1)
score_stats.columns = ['Média', 'Desvio Padrão', 'Mínimo', 'Máximo', 'Quantidade']
print(score_stats)

print("\n" + "="*70)
print("--- DISTRIBUIÇÃO DAS CLASSIFICAÇÕES DO MODELO ---")
print("="*70 + "\n")

for sentiment in merged['sentiment'].unique():
    subset = merged[merged['sentiment'] == sentiment]
    print(f"\n📊 Categoria Real: {sentiment.upper()} ({len(subset)} mensagens)")
    print("-" * 70)
    
    # Show distribution of predicted labels
    dist = subset['sentiment_label'].value_counts()
    for label, count in dist.items():
        percentage = (count / len(subset)) * 100
        print(f"  • Classificado como {label}: {count} ({percentage:.1f}%)")
    
    # Show average score
    avg_score = subset['score'].mean()
    print(f"\n  📈 Score médio: {avg_score:.1f}/100")

# Confusion-like analysis
print("\n" + "="*70)
print("--- MATRIZ DE CONFUSÃO SIMPLIFICADA ---")
print("="*70 + "\n")

confusion = pd.crosstab(
    merged['sentiment'],
    merged['sentiment_label'],
    margins=True
)
print(confusion)

# Accuracy based on expected score ranges
print("\n" + "="*70)
print("--- MÉTRICAS DE ACURÁCIA POR FAIXA DE SCORE ---")
print("="*70 + "\n")

# Define expected score ranges (global for reuse)
ranges = {
    'very_negative': (0, 15),
    'negative': (15, 35),
    'slightly_negative': (35, 45),
    'neutral': (45, 55),
    'slightly_positive': (55, 70),
    'positive': (70, 85),
    'very_positive': (85, 100)
}

def check_score_in_range(row):
    score = row['score']
    sentiment = row['sentiment']
    
    if sentiment in ranges:
        min_score, max_score = ranges[sentiment]
        return min_score <= score <= max_score
    return False

merged['score_in_range'] = merged.apply(check_score_in_range, axis=1)
range_accuracy = (merged['score_in_range'].sum() / len(merged)) * 100

print(f"🎯 Acurácia por Faixa de Score: {range_accuracy:.1f}%")
print(f"  • Dentro da faixa esperada: {merged['score_in_range'].sum()}")
print(f"  • Fora da faixa esperada: {(~merged['score_in_range']).sum()}")

print("\n📊 Performance por Categoria:\n")
for sentiment in sorted(merged['sentiment'].unique()):
    subset = merged[merged['sentiment'] == sentiment]
    in_range = subset['score_in_range'].sum()
    total = len(subset)
    pct = (in_range / total) * 100 if total > 0 else 0
    avg_score = subset['score'].mean()
    # Add a placeholder for 'expected_score_range' if it doesn't exist, or calculate it
    expected_range_str = "N/A"
    if sentiment in ranges:
        min_s, max_s = ranges[sentiment]
        expected_range_str = f"({min_s}-{max_s})"
    
    print(f"  {sentiment:20} | Acurácia: {pct:5.1f}% ({in_range}/{total}) | Score médio: {avg_score:5.1f} | Esperado: {expected_range_str}")

# Show some examples of misclassifications
print("\n" + "="*70)
print("--- EXEMPLOS FORA DA FAIXA ESPERADA ---")
print("="*70 + "\n")

incorrect = merged[~merged['score_in_range']].head(10)
for _, row in incorrect.iterrows():
    print(f"ID {row['id']} | Real: {row['sentiment']} → Modelo: {row['sentiment_label']}")
    print(f"  Mensagem: {row['message'][:70]}...")
    print(f"  Score: {row['score']}\n")

# Export detailed results
merged.to_csv('validation_results.csv', index=False)
print("="*70)
print(f"✅ Resultados detalhados salvos em 'validation_results.csv'")
print("="*70)
