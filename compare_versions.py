"""
Compara a versão original vs improved do sentiment analyzer
"""
import json
import pandas as pd

# Test with a small sample first
with open('conversas_whatsapp.json', 'r') as f:
    data = json.load(f)

# Take a representative sample from each category
sample_size = 10
sample_data = []

for sentiment in ['very_negative', 'negative', 'slightly_negative', 'neutral', 
                  'slightly_positive', 'positive', 'very_positive']:
    category_items = [item for item in data if item['sentiment'] == sentiment]
    sample_data.extend(category_items[:sample_size])

print(f"Testing with {len(sample_data)} messages...\n")

# Test Original
print("="*70)
print("TESTING ORIGINAL VERSION")
print("="*70)

from sentiment import SentimentAnalyzer as OriginalAnalyzer
original_results = []

for item in sample_data:
    result = OriginalAnalyzer.analyze_conversation(item)
    original_results.append({
        'id': item['id'],
        'sentiment': item['sentiment'],
        'score_original': result['score'],
        'label_original': result['sentiment_label'],
        'message': item['message']
    })

# Test Improved
print("\n" + "="*70)
print("TESTING IMPROVED VERSION")
print("="*70)

from sentiment_improved import SentimentAnalyzer as ImprovedAnalyzer
improved_results = []

for item in sample_data:
    result = ImprovedAnalyzer.analyze_conversation(item)
    improved_results.append({
        'id': item['id'],
        'score_improved': result['score'],
        'label_improved': result['sentiment_label']
    })

# Merge results
df_orig = pd.DataFrame(original_results)
df_impr = pd.DataFrame(improved_results)
comparison = pd.merge(df_orig, df_impr, on='id')

# Expected ranges
ranges = {
    'very_negative': (0, 15),
    'negative': (15, 35),
    'slightly_negative': (35, 45),
    'neutral': (45, 55),
    'slightly_positive': (55, 70),
    'positive': (70, 85),
    'very_positive': (85, 100)
}

# Check accuracy
def in_range(row, version='original'):
    score_col = f'score_{version}'
    score = row[score_col]
    sentiment = row['sentiment']
    if sentiment in ranges:
        min_s, max_s = ranges[sentiment]
        return min_s <= score <= max_s
    return False

comparison['original_correct'] = comparison.apply(lambda r: in_range(r, 'original'), axis=1)
comparison['improved_correct'] = comparison.apply(lambda r: in_range(r, 'improved'), axis=1)

# Summary
print("\n" + "="*70)
print("COMPARISON SUMMARY")
print("="*70 + "\n")

orig_acc = (comparison['original_correct'].sum() / len(comparison)) * 100
impr_acc = (comparison['improved_correct'].sum() / len(comparison)) * 100

print(f"Original Accuracy: {orig_acc:.1f}% ({comparison['original_correct'].sum()}/{len(comparison)})")
print(f"Improved Accuracy: {impr_acc:.1f}% ({comparison['improved_correct'].sum()}/{len(comparison)})")
print(f"Improvement: {impr_acc - orig_acc:+.1f} percentage points\n")

# Per category
print("Performance by Category:\n")
print(f"{'Category':<20} | {'Original':>8} | {'Improved':>8} | {'Avg Orig':>9} | {'Avg Impr':>9} | {'Expected':>12}")
print("-" * 95)

for sentiment in sorted(comparison['sentiment'].unique()):
    subset = comparison[comparison['sentiment'] == sentiment]
    orig_pct = (subset['original_correct'].sum() / len(subset)) * 100
    impr_pct = (subset['improved_correct'].sum() / len(subset)) * 100
    avg_orig = subset['score_original'].mean()
    avg_impr = subset['score_improved'].mean()
    expected = f"{ranges[sentiment][0]}-{ranges[sentiment][1]}"
    
    print(f"{sentiment:<20} | {orig_pct:>7.1f}% | {impr_pct:>7.1f}% | {avg_orig:>9.1f} | {avg_impr:>9.1f} | {expected:>12}")

# Show some examples where improved version fixed errors
print("\n" + "="*70)
print("EXAMPLES OF IMPROVEMENTS")
print("="*70 + "\n")

improved_fixes = comparison[(~comparison['original_correct']) & (comparison['improved_correct'])]
if len(improved_fixes) > 0:
    print(f"Found {len(improved_fixes)} cases where Improved version fixed Original errors:\n")
    for idx, row in improved_fixes.head(5).iterrows():
        expected_range = f"{ranges[row['sentiment']][0]}-{ranges[row['sentiment']][1]}"
        print(f"Category: {row['sentiment']}")
        print(f"  Message: {row['message'][:60]}...")
        print(f"  Original: {row['score_original']:.1f} ❌ | Improved: {row['score_improved']:.1f} ✅ | Expected: {expected_range}")
        print()
else:
    print("No improvements found in this sample.\n")

# Save detailed comparison
comparison.to_csv('sentiment_comparison.csv', index=False)
print("="*70)
print("✅ Detailed comparison saved to 'sentiment_comparison.csv'")
print("="*70)
