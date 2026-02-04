from pysentimiento import create_analyzer
import numpy as np
import torch

# Limit threads to reduce memory overhead on CPU
torch.set_num_threads(1)

analyzer = create_analyzer(task="sentiment", lang="pt")


class SentimentAnalyzer:
    @staticmethod
    def analyze_conversation(conversation_data) -> dict:
        """
        Improved sentiment analysis with better score distribution.
        Uses tanh compression to reduce extreme polarization.
        """

        texts = []

        # Raw text (e.g. meeting transcription)
        if isinstance(conversation_data, str):
            texts = [t.strip() for t in conversation_data.split('.') if len(t.strip()) > 20]

        else:
            # New format: simple object with direct 'message' field
            if 'message' in conversation_data and isinstance(conversation_data.get('message'), str):
                msg = conversation_data['message'].strip()
                if len(msg) > 5:
                    texts.append(msg)
            # Old format: 'Full Conversation' array
            else:
                messages = conversation_data.get('Full Conversation', [])
                for m in messages:
                    if not m.get('sender'):
                        msg = m.get('message', '').strip()
                        if len(msg) > 5:
                            texts.append(msg)

        if not texts:
            return {'score': 50.0, 'sentiment_label': 'Neutral'}

        chunk_results = []
        import gc

        processed_count = 0
        for text in texts:
            processed_count += 1
            # Truncate text to avoid OOM on very long sequences or tokenization issues
            if len(text) > 1024:
                text = text[:1024]

            try:
                with torch.no_grad():
                    pred = analyzer.predict(text)
            except Exception as e:
                print(f"Error analyzing chunk: {e}")
                continue
            
            # Periodic garbage collection to prevent memory buildup
            if processed_count % 50 == 0:
                gc.collect()

            p = pred.probas

            # Emotional intensity (how non-neutral it is)
            intensity = max(p['POS'], p['NEG'])

            # Ignore very weak signals (slightly increased threshold)
            if intensity < 0.20:
                continue

            # Convert to sentiment value [-1, 1]
            raw_sentiment = p['POS'] - p['NEG']
            
            # Apply tanh compression to reduce extreme polarization
            # This "squeezes" extreme values closer to center while preserving direction
            # compression_factor: higher = more compression (0.5-2.0 recommended)
            compression_factor = 1.2
            compressed_sentiment = np.tanh(raw_sentiment * compression_factor)

            chunk_results.append({
                'value': compressed_sentiment,
                'weight': intensity
            })

        # Fallback if everything was weak
        if not chunk_results:
            return {'score': 50.0, 'sentiment_label': 'Neutral'}

        # Weighted sentiment aggregation
        weighted_score = np.average(
            [c['value'] for c in chunk_results],
            weights=[c['weight'] for c in chunk_results]
        )

        # Convert to 0–100 score
        # Apply additional calibration to better spread the middle ranges
        score = (weighted_score + 1) / 2 * 100
        
        # Fine-tune the score with a non-linear transformation
        # This expands the 20-80 range while compressing extremes
        score = 50 + (score - 50) * 0.85
        
        score = round(max(0, min(100, score)), 1)

        # Updated label logic with better thresholds for 7 levels
        if score >= 85:
            sentiment_label = 'Very Positive'
        elif score >= 65:
            sentiment_label = 'Positive'
        elif score >= 52:
            sentiment_label = 'Slightly Positive'
        elif score >= 48:
            sentiment_label = 'Neutral'
        elif score >= 30:
            sentiment_label = 'Slightly Negative'
        elif score >= 10:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Very Negative'

        return {
            'score': score,
            'sentiment_label': sentiment_label
        }
