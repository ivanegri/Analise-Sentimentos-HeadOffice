import unittest
from io import BytesIO
from file_parser import parse_pdf, parse_docx

class TestFileParser(unittest.TestCase):
    def test_txt_sentiment_logic(self):
        # We can't easily mock PDF/DOCX binary generation without heavy libs in test enviroment
        # But we can test the sentiment logic refactor with strings
        from sentiment import SentimentAnalyzer
        
        # Test string input (simulating extracted text)
        result = SentimentAnalyzer.analyze_conversation("Eu amo este serviço!")
        self.assertGreater(result['score'], 60)
        self.assertEqual(result['sentiment_label'], 'Positive')

        result_neg = SentimentAnalyzer.analyze_conversation("Isso é horrível.")
        self.assertLess(result_neg['score'], 40)
        self.assertEqual(result_neg['sentiment_label'], 'Negative')

if __name__ == '__main__':
    unittest.main()
