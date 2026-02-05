from pysentimiento import create_analyzer
import numpy as np
import torch

# Limit threads to reduce memory overhead on CPU
torch.set_num_threads(1)

analyzer = create_analyzer(task="sentiment", lang="pt")


class SentimentAnalyzer:
    # 7-level sentiment labels ordered from most negative to most positive
    LEVELS = [
        'very_negative',
        'negative', 
        'slightly_negative',
        'neutral',
        'slightly_positive',
        'positive',
        'very_positive'
    ]
    
    LEVEL_LABELS = {
        'very_negative': 'Very Negative',
        'negative': 'Negative',
        'slightly_negative': 'Slightly Negative',
        'neutral': 'Neutral',
        'slightly_positive': 'Slightly Positive',
        'positive': 'Positive',
        'very_positive': 'Very Positive'
    }

    @staticmethod
    def analyze_conversation(conversation_data) -> dict:
        """
        Sentiment analysis v3.0 with:
        - Weighted scoring (emotional messages count more)
        - Real 7-level probability distribution
        - Neutral only when truly dominant
        """

        texts = []

        # Raw text (e.g. meeting transcription) - split into sentence windows
        if isinstance(conversation_data, str):
            sentences = [t.strip() for t in conversation_data.replace('!', '.').replace('?', '.').split('.') if len(t.strip()) > 10]
            # Group sentences into windows of 3
            window_size = 3
            for i in range(0, len(sentences), window_size):
                window = ' '.join(sentences[i:i + window_size])
                if len(window) > 20:
                    texts.append(window)
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
            return SentimentAnalyzer._build_neutral_response()

        chunk_results = []
        import gc

        processed_count = 0
        for text in texts:
            processed_count += 1
            # Truncate text to avoid OOM on very long sequences
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
            
            # Calculate weight: emotional messages count more (quadratic weight)
            # Weak neutrals (intensity < 0.25) get minimal weight
            if intensity < 0.25:
                weight = 0.1  # Weak signals barely count
            else:
                weight = intensity ** 2  # Quadratic: stronger emotions dominate

            chunk_results.append({
                'pos': p['POS'],
                'neg': p['NEG'],
                'neu': p['NEU'],
                'weight': weight
            })

        # Fallback if everything was weak
        if not chunk_results:
            return SentimentAnalyzer._build_neutral_response()

        # Weighted aggregation of raw probabilities
        total_weight = sum(c['weight'] for c in chunk_results)
        avg_pos = sum(c['pos'] * c['weight'] for c in chunk_results) / total_weight
        avg_neg = sum(c['neg'] * c['weight'] for c in chunk_results) / total_weight
        avg_neu = sum(c['neu'] * c['weight'] for c in chunk_results) / total_weight

        # Build 7-level probability distribution from the 3 raw probabilities
        level_scores = SentimentAnalyzer._compute_7_level_scores(avg_pos, avg_neg, avg_neu)
        
        # Find dominant level
        dominant_level = max(level_scores, key=level_scores.get)
        sentiment_label = SentimentAnalyzer.LEVEL_LABELS[dominant_level]
        
        # Calculate overall score (0-100)
        # Map from sentiment value [-1, 1] to [0, 100]
        sentiment_value = avg_pos - avg_neg
        score = round((sentiment_value + 1) / 2 * 100, 1)
        score = max(0, min(100, score))

        return {
            'score': score,
            'sentiment_label': sentiment_label,
            'level_scores': {k: round(v, 3) for k, v in level_scores.items()}
        }
    
    @staticmethod
    def _compute_7_level_scores(pos: float, neg: float, neu: float) -> dict:
        """
        Convert 3 raw probabilities (POS, NEG, NEU) into 7-level distribution.
        Uses intensity to split positive/negative into gradations.
        """
        # Intensity determines how extreme the sentiment is
        intensity = max(pos, neg)
        
        # Initialize all levels
        scores = {level: 0.0 for level in SentimentAnalyzer.LEVELS}
        
        # Distribute negative probability across negative levels
        if neg > 0.05:
            if neg > 0.7:  # Strong negative
                scores['very_negative'] = neg * 0.6
                scores['negative'] = neg * 0.3
                scores['slightly_negative'] = neg * 0.1
            elif neg > 0.4:  # Moderate negative
                scores['very_negative'] = neg * 0.2
                scores['negative'] = neg * 0.5
                scores['slightly_negative'] = neg * 0.3
            else:  # Weak negative
                scores['negative'] = neg * 0.3
                scores['slightly_negative'] = neg * 0.7
        
        # Distribute positive probability across positive levels
        if pos > 0.05:
            if pos > 0.7:  # Strong positive
                scores['very_positive'] = pos * 0.6
                scores['positive'] = pos * 0.3
                scores['slightly_positive'] = pos * 0.1
            elif pos > 0.4:  # Moderate positive
                scores['very_positive'] = pos * 0.2
                scores['positive'] = pos * 0.5
                scores['slightly_positive'] = pos * 0.3
            else:  # Weak positive
                scores['positive'] = pos * 0.3
                scores['slightly_positive'] = pos * 0.7
        
        # Neutral: only significant if truly dominant
        # Reduce neutral influence when there's clear sentiment
        if neu > 0.5 and intensity < 0.3:
            scores['neutral'] = neu * 0.8
        elif neu > 0.3:
            scores['neutral'] = neu * 0.4
        else:
            scores['neutral'] = neu * 0.2
        
        # Normalize to sum to 1
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            scores['neutral'] = 1.0
            
        return scores
    
    @staticmethod
    def _build_neutral_response() -> dict:
        """Build a neutral response when no valid text is found."""
        return {
            'score': 50.0,
            'sentiment_label': 'Neutral',
            'level_scores': {
                'very_negative': 0.0,
                'negative': 0.0,
                'slightly_negative': 0.0,
                'neutral': 1.0,
                'slightly_positive': 0.0,
                'positive': 0.0,
                'very_positive': 0.0
            }
        }
