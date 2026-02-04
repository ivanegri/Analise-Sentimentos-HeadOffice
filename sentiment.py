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
        Improved sentiment analysis for WhatsApp chats and meeting transcripts.
        Reduces Neutral dominance and improves score sensitivity.
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

            # Ignore very weak signals
            if intensity < 0.15:
                continue

            # Convert to sentiment value [-1, 1]
            sentiment_value = p['POS'] - p['NEG']

            chunk_results.append({
                'value': sentiment_value,
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
        score = (weighted_score + 1) / 2 * 100
        score = round(max(0, min(100, score)), 1)

        # Label logic (less Neutral bias)
        if score > 80:
            sentiment_label = 'Positive'
        elif score < 50:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'

        return {
            'score': score,
            'sentiment_label': sentiment_label
        }
