import logging
import torch
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

class SummarizerService:
    """
    Summarization service using T5 model (t5-small).
    CPU-optimized for efficient document summarization.
    """

    def __init__(self):
        self.model_name = "t5-small"
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cpu")
        self.is_ready = False

        try:
            logger.info(f"Loading summarizer model: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.is_ready = True
            logger.info("Summarizer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarizer model: {str(e)}")
            self.is_ready = False

    def summarize(self, text: str) -> dict:
        """
        Summarize the provided text.
        """
        if not self.is_ready or not self.model or not self.tokenizer:
            return {
                "original_text": text,
                "summary_text": "",
                "error": "Summarizer service not available"
            }

        if not text or not text.strip():
            return {
                "original_text": text,
                "summary_text": "",
                "error": "Input text is empty"
            }

        start_time = time.time()
        try:
            # T5 requires "summarize: " prefix
            input_text = "summarize: " + text
            
            inputs = self.tokenizer(
                input_text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1024
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=150,
                    min_length=30,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )

            summary_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            processing_time = round(time.time() - start_time, 2)
            
            return {
                "original_text": text,
                "summary_text": summary_text,
                "processing_time": processing_time
            }

        except Exception as e:
            logger.error(f"Summarization failed: {str(e)}")
            return {
                "original_text": text,
                "summary_text": "",
                "error": str(e)
            }
