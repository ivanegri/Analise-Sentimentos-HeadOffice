import unittest
from sentiment import SentimentAnalyzer
import json

class TestSentiment(unittest.TestCase):
    def test_positive(self):
        data = {
            'Full Conversation': [
                {'sender': '', 'message': 'Eu adorei esse atendimento, muito obrigado!'}
            ]
        }
        result = SentimentAnalyzer.analyze_conversation(data)
        print(f"Positive Test Result: {result}")
        self.assertGreater(result['score'], 60)
        self.assertEqual(result['sentiment_label'], 'Positive')

    def test_negative(self):
        data = {
            'Full Conversation': [
                {'sender': '', 'message': 'Isso é um lixo, odeio vocês.'}
            ]
        }
        result = SentimentAnalyzer.analyze_conversation(data)
        print(f"Negative Test Result: {result}")
        self.assertLess(result['score'], 40)
        self.assertEqual(result['sentiment_label'], 'Negative')

    def test_neutral_empty(self):
        data = {
           'Full Conversation': [] 
        }
        result = SentimentAnalyzer.analyze_conversation(data)
        print(f"Empty Test Result: {result}")
        self.assertEqual(result['score'], 50.0)
        self.assertEqual(result['sentiment_label'], 'Neutral')

if __name__ == '__main__':
    unittest.main()
