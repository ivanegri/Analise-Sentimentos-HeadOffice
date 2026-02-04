from pysentimiento import create_analyzer

# Global analyzer instance to avoid reloading on every request
# 'pysentimiento/bertweet-pt-sentiment' is the specific model for PT tweets/short text
analyzer = create_analyzer(task="sentiment", lang="pt")

class SentimentAnalyzer:
    @staticmethod
    def analyze_conversation(conversation_data: dict) -> dict:
        """
        Analyzes the sentiment of a conversation using BERTweet-pt.
        """
        texts = []
        
        # Handle raw text input (e.g. from files)
        if isinstance(conversation_data, str):
            texts.append(conversation_data)
        else:
            # Handle JSON structure
            messages = conversation_data.get('Full Conversation', [])
            
            for m in messages:
                # Filter user messages similar to before
                if not m.get('sender'):
                    msg = m.get('message', '').strip()
                    if msg:
                        texts.append(msg)
                    
        if not texts:
            return {'score': 50.0, 'sentiment_label': 'Neutral'}

        # Join texts. 
        # Note: BERT has a token limit (usually 512). 
        # For a simple integration, we join them. If it's too long, the library usually truncates or we might want to handle it.
        # Given this is for WhatsApp chats, they are usually short enough or we capture the essence.
        text = ' '.join(texts)
        
        # Predict
        prediction = analyzer.predict(text)
        probas = prediction.probas
        
        score = (probas['POS'] - probas['NEG'] + 1) / 2 * 100
        score = max(0, min(100, score))
        
        # Custom Logic: Bias against Neutral
        # The model tends to be conservative (Neutral). 
        # We lower the bar for Positive/Negative to make it more sensitive.
        threshold = 0.20  # If POS or NEG > 35%, we pick them over Neutral
        
        output_label = prediction.output
        if output_label == 'NEU':
            if probas['NEG'] > threshold:
                output_label = 'NEG'
            elif probas['POS'] > threshold:
                output_label = 'POS'
        
        # If both are high (rare), prefer Negative if it's a CRM (usually catching complaints is priority)? 
        # Or stick to simple comparison:
        if output_label != prediction.output:
            # Re-check between POS and NEG if we overrode NEU
            if probas['NEG'] > probas['POS']:
                output_label = 'NEG'
            else:
                output_label = 'POS'

        label_map = {
            'POS': 'Positive',
            'NEG': 'Negative',
            'NEU': 'Neutral'
        }
        sentiment_label = label_map.get(output_label, 'Neutral')
            
        return {'score': round(score, 1), 'sentiment_label': sentiment_label}
