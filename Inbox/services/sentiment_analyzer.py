import re

class SentimentAnalyzer:
    def __init__(self):
        self.positive_words = {
            'thank', 'thanks', 'great', 'awesome', 'perfect', 'resolved', 'love', 
            'satisfied', 'happy', 'excellent', 'good', 'solved', 'appreciate', 
            'helpful', 'amazing', 'glad', 'wonderful', 'fantastic', 'superb'
        }
        
        self.negative_words = {
            'refund', 'broken', 'angry', 'bad', 'worst', 'fail', 'error', 'useless', 
            'charge', 'cancel', 'disappointed', 'slow', 'poor', 'frustrated', 
            'annoyed', 'hate', 'terrible', 'broken', 'defect', 'issue', 'complaint'
        }

    def clean_text(self, text: str) -> list[str]:
        if not text:
            return []
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def analyze(self, text: str) -> str:
        words = self.clean_text(text)
        if not words:
            return 'Neutral'

        pos_count = sum(1 for word in words if word in self.positive_words)
        neg_count = sum(1 for word in words if word in self.negative_words)

        if pos_count > neg_count:
            return 'Positive'
        elif neg_count > pos_count:
            return 'Negative'
        else:
            return 'Neutral'

sentiment_analyzer = SentimentAnalyzer()
