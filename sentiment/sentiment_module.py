from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class EmotionAnalyzer:
    def __init__(self):
        logger.info("Loading emotion analysis model...")
        # Downloads model (approx 260MB)
        self.classifier = pipeline(
            "text-classification", 
            model="bhadresh-savani/distilbert-base-uncased-emotion", 
            top_k=None 
        )
        logger.info("Emotion analysis model loaded!")

    def get_sentiment_from_emotion(self, emotion_label):
        positive = ['joy', 'love', 'surprise']
        negative = ['anger', 'sadness', 'fear']
        
        if emotion_label in positive: return "POSITIVE"
        if emotion_label in negative: return "NEGATIVE"
        return "NEUTRAL"

    def analyze(self, text):
        if not text or not text.strip(): 
            return None
        
        results = self.classifier(text)[0]
        top_result = sorted(results, key=lambda x: x['score'], reverse=True)[0]
        
        # Get all emotions with scores
        emotions_dict = {}
        for result in results:
            emotions_dict[result['label'].capitalize()] = round(result['score'], 4)
        
        return {
            "emotion": top_result['label'],
            "sentiment": self.get_sentiment_from_emotion(top_result['label']),
            "confidence": round(top_result['score'], 4),
            "emotions": emotions_dict
        }


# Global analyzer instance (created on first use)
_GLOBAL_EMOTION_ANALYZER = None

def analyze_sentiment(text):
    """
    Main function called by the API.
    Returns dict with 'sentiment' and 'emotions'.
    """
    global _GLOBAL_EMOTION_ANALYZER
    
    if _GLOBAL_EMOTION_ANALYZER is None:
        _GLOBAL_EMOTION_ANALYZER = EmotionAnalyzer()

    result = _GLOBAL_EMOTION_ANALYZER.analyze(text)
    
    if not result:
        return {
            "sentiment": "Neutral",
            "emotions": {
                "Happy": 0.25,
                "Neutral": 0.25,
                "Sad": 0.15,
                "Angry": 0.15,
                "Fear": 0.10,
                "Surprise": 0.10
            }
        }

    return {
        "sentiment": result.get('sentiment', 'NEUTRAL'),
        "emotions": result.get('emotions', {}),
        "confidence": result.get('confidence', 0.0)
    }


# This runs ONLY when script is executed directly (not when imported!)
if __name__ == "__main__":
    # Test code - only runs when you execute this file directly
    analyzer = EmotionAnalyzer()
    
    print("="*50)
    print(" EMOTION ANALYZER TEST")
    print("="*50)

    while True:
        user_input = input("\n>> Enter text (or 'exit'): ")
        
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Exiting...")
            break
            
        result = analyzer.analyze(user_input)
        
        if result:
            print(f"   [Emotion]:   {result['emotion'].upper()}")
            print(f"   [Sentiment]: {result['sentiment']}")
            print(f"   [Score]:     {result['confidence'] * 100:.1f}%")