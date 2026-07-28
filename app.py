from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Global service variables
grammar_service = None
paraphrasing_service = None
summarizer_service = None
sentiment_service = None
humanizer_service = None
video_module_available = False

def initialize_services():
    """Initialize all ML services"""
    global grammar_service, paraphrasing_service, summarizer_service, sentiment_service, humanizer_service, video_service
    
    logger.info("=" * 60)
    logger.info("🚀 INITIALIZING TEXT NEXUS SERVICES")
    logger.info("=" * 60)
    
    # 1. Grammar Service
    try:
        logger.info("📝 Loading Grammar Service...")
        from grammar.grammar_checker import GrammarServiceVennify
        grammar_service = GrammarServiceVennify()
        logger.info(f"   ✅ Grammar Service: Ready={grammar_service.is_ready}")
    except Exception as e:
        logger.error(f"   ❌ Grammar Service Failed: {e}")
        grammar_service = None
    
    # 2. Paraphrasing Service
    try:
        logger.info("🔄 Loading Paraphrasing Service...")
        from paraphraser.paraphraser import T5ParaphrasingService
        paraphrasing_service = T5ParaphrasingService()
        logger.info(f"   ✅ Paraphrasing Service: Ready={paraphrasing_service.models_loaded}")
    except Exception as e:
        logger.error(f"   ❌ Paraphrasing Service Failed: {e}")
        paraphrasing_service = None
    
    # 3. Summarizer Service
    try:
        logger.info("📄 Loading Summarizer Service...")
        from summarizer.summarizer import SummarizerService
        summarizer_service = SummarizerService()
        logger.info(f"   ✅ Summarizer Service: Ready={summarizer_service.is_ready}")
    except Exception as e:
        logger.error(f"   ❌ Summarizer Service Failed: {e}")
        summarizer_service = None
    
    # 4. Sentiment Service
    try:
        logger.info("😊 Loading Sentiment Service...")
        from sentiment.sentiment_module import analyze_sentiment
        # Test it works
        test = analyze_sentiment("test")
        sentiment_service = True
        logger.info(f"   ✅ Sentiment Service: Ready")
    except Exception as e:
        logger.error(f"   ❌ Sentiment Service Failed: {e}")
        sentiment_service = None
        
    # 5. Humanizer Service (optional)
    try:
        logger.info("🧑‍🤝‍🧑 Loading Humanizer Service...")
        
        import sys
        import os
        
        humanizer_path = os.path.join(os.path.dirname(__file__), 'Text_Humanizer')
        if humanizer_path not in sys.path:
            sys.path.insert(0, humanizer_path)
        
        original_cwd = os.getcwd()
        os.chdir(humanizer_path)
        
        try:
            # Just use the paraphraser as humanizer
            if paraphrasing_service and paraphrasing_service.models_loaded:
                class HumanizerWrapper:
                    def humanize(self, text):
                        return paraphrasing_service.paraphrase(text, mode='creative')
                
                humanizer_service = HumanizerWrapper()
                logger.info(f"   ✅ Humanizer Service: Ready (using paraphraser)")
            else:
                raise Exception("Paraphraser not available")
        finally:
            os.chdir(original_cwd)
            
    except Exception as e:
        logger.warning(f"   ⚠️ Humanizer Service Not Available: {e}")
        humanizer_service = None

    # 6. Video Module (optional)
    try:
        logger.info("🎬 Loading Video Module...")
        from video_module.video_module import VideoTextProcessor
        video_service = True
        logger.info(f"   ✅ Video Module: Available")
    except Exception as e:
        logger.warning(f"   ⚠️ Video Module Not Available: {e}")
        video_service = None
    
    logger.info("=" * 60)
    logger.info("✅ SERVICE INITIALIZATION COMPLETE")
    logger.info("=" * 60)

# ==================== ENDPOINTS ====================

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        "app": "Text Nexus API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/health",
            "/api/paraphrase",
            "/api/grammar-check",
            "/api/summarize",
            "/api/humanize",
            "/api/sentiment"
        ]
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "services": {
            "grammar": grammar_service is not None,
            "paraphraser": paraphrasing_service is not None,
            "summarizer": summarizer_service is not None,
            "sentiment": sentiment_service is not None,
            "humanizer": humanizer_service is not None,
            "video": video_module_available
        }
    })

@app.route('/api/paraphrase', methods=['POST'])
def paraphrase():
    """Paraphrase text"""
    try:
        logger.info("📥 Received paraphrase request")
        
        if not paraphrasing_service:
            logger.error("Paraphrasing service not available")
            return jsonify({"error": "Paraphrasing service unavailable", "success": False}), 503
        
        data = request.get_json()
        text = data.get('text', '')
        mode = data.get('mode', 'standard')
        
        if not text or not text.strip():
            return jsonify({"error": "Text is required", "success": False}), 400
        
        logger.info(f"Processing: {text[:50]}... (mode={mode})")
        result = paraphrasing_service.paraphrase(text, mode)
        logger.info(f"✅ Result: {result[:50]}...")
        
        return jsonify({
            "original_text": text,
            "paraphrased_text": result,
            "mode": mode,
            "success": True
        })
    except Exception as e:
        logger.error(f"❌ Paraphrase error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/grammar-check', methods=['POST'])
def grammar_check():
    """Check grammar"""
    try:
        logger.info("📥 Received grammar check request")
        
        if not grammar_service:
            logger.error("Grammar service not available")
            return jsonify({"error": "Grammar service unavailable", "success": False}), 503
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({"error": "Text is required", "success": False}), 400
        
        logger.info(f"Checking: {text[:50]}...")
        result = grammar_service.check_grammar(text)
        logger.info(f"✅ Found {result.get('errors_count', 0)} issues")
        
        return jsonify({
            **result,
            "success": True
        })
    except Exception as e:
        logger.error(f"❌ Grammar error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """Summarize text"""
    try:
        logger.info("📥 Received summarize request")
        
        if not summarizer_service:
            logger.error("Summarizer service not available")
            return jsonify({"error": "Summarizer service unavailable", "success": False}), 503
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({"error": "Text is required", "success": False}), 400
        
        logger.info(f"Summarizing: {text[:50]}...")
        result = summarizer_service.summarize(text)
        logger.info(f"✅ Summary generated")
        
        return jsonify({
            **result,
            "success": True
        })
    except Exception as e:
        logger.error(f"❌ Summarize error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/humanize', methods=['POST'])
def humanize():
    """Humanize AI text"""
    try:
        logger.info("📥 Received humanize request")
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({"error": "Text is required", "success": False}), 400
        
        logger.info(f"Humanizing: {text[:50]}...")
        
        # Try humanizer first
        if humanizer_service:
            try:
                # Adjust this based on your actual humanizer method
                result = humanizer_service.humanize(text)
                return jsonify({
                    "original_text": text,
                    "humanized_text": result,
                    "success": True,
                    "method": "humanizer"
                })
            except Exception as e:
                logger.warning(f"Humanizer failed: {e}")
        
        # Fallback to paraphrasing if available
        if paraphrasing_service:
            result = paraphrasing_service.paraphrase(text, mode='creative')
            return jsonify({
                "original_text": text,
                "humanized_text": result,
                "success": True,
                "method": "paraphraser"
            })
        
        # If nothing works, return error
        return jsonify({
            "error": "Humanizer and paraphraser unavailable",
            "success": False
        }), 503
        
    except Exception as e:
        logger.error(f"❌ Humanize error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    """Analyze sentiment and emotions"""
    try:
        logger.info("📥 Received sentiment request")
        
        if not sentiment_service:
            # Return placeholder emotions if service not available
            logger.warning("Sentiment service not available, using placeholder")
            data = request.get_json()
            text = data.get('text', '')
            
            return jsonify({
                "original_text": text,
                "sentiment": "Neutral",
                "emotions": {
                    "Happy": 0.4,
                    "Neutral": 0.3,
                    "Sad": 0.15,
                    "Angry": 0.1,
                    "Surprised": 0.05
                },
                "success": True,
                "note": "Using placeholder emotions - sentiment module not fully loaded"
            })
        
        data = request.get_json()
        text = data.get('text', '')
        
        if not text or not text.strip():
            return jsonify({"error": "Text is required", "success": False}), 400
        
        logger.info(f"Analyzing sentiment: {text[:50]}...")
        
        # Try to call sentiment module
        try:
            from sentiment.sentiment_module import analyze_sentiment
            result = analyze_sentiment(text)
            
            return jsonify({
                "original_text": text,
                "sentiment": result.get('sentiment', 'Neutral'),
                "emotions": result.get('emotions', {}),
                "success": True
            })
        except Exception as sentiment_error:
            logger.warning(f"Sentiment analysis failed: {sentiment_error}")
            # Return placeholder
            return jsonify({
                "original_text": text,
                "sentiment": "Neutral",
                "emotions": {
                    "Happy": 0.4,
                    "Neutral": 0.3,
                    "Sad": 0.15,
                    "Angry": 0.1,
                    "Surprised": 0.05
                },
                "success": True,
                "note": "Using placeholder emotions"
            })
        
    except Exception as e:
        logger.error(f"❌ Sentiment error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500
    
@app.route('/api/video-extract', methods=['POST'])
def video_extract():
    """Extract text from video"""
    try:
        logger.info("📥 Received video extraction request")
        
        # For now, return placeholder
        # TODO: Implement actual video transcription when ready
        
        data = request.get_json()
        video_path = data.get('video_path', '')
        
        return jsonify({
            "extracted_text": "Video extraction feature is coming soon. This requires integration with a video transcription service like Google Speech-to-Text, AssemblyAI, or AWS Transcribe.",
            "summary": "To implement this feature, you'll need to: 1) Extract audio from video, 2) Transcribe audio to text, 3) Optionally summarize the transcript.",
            "success": True,
            "note": "Placeholder response - actual implementation pending"
        })
        
    except Exception as e:
        logger.error(f"❌ Video extraction error: {e}", exc_info=True)
        return jsonify({"error": str(e), "success": False}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 TEXT NEXUS API SERVER")
    print("=" * 70)
    print("📡 Local: http://127.0.0.1:5000")
    print("🔗 Network: http://10.13.47.39:5000")
    print("📝 Health: http://10.13.47.39:5000/health")
    print("=" * 70 + "\n")
    
    # Initialize all services
    initialize_services()
    
    print("\n" + "=" * 70)
    print("✅ Server ready! Waiting for requests...")
    print("=" * 70 + "\n")
    
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )