import os
import re
from difflib import SequenceMatcher

try:
    import easyocr
    import cv2
    from transformers import pipeline
    import torch
except Exception:
    # Lazy imports: heavy deps may not be available at startup
    easyocr = None
    cv2 = None
    pipeline = None
    torch = None

# ======================================================
# Utilities
# ======================================================

def is_similar(a, b, threshold=0.6):
    """Checks if two strings are more than `threshold` similar."""
    return SequenceMatcher(None, a, b).ratio() > threshold


def clean_ocr_text(text):
    """Removes common OCR garbage and noisy symbols."""
    text = re.sub(r'[^a-zA-Z0-9\s.,\'\"-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ======================================================
# VideoTextProcessor (import-safe)
# ======================================================
class VideoTextProcessor:
    def __init__(self, video_path, reader=None, summarizer=None, device=None, upload_folder='temp_uploads'):
        self.video_path = video_path
        self.upload_folder = upload_folder

        # Allow caller to pass pre-initialized reader/summarizer to avoid heavy imports during app startup
        self.reader = reader
        self.summarizer = summarizer
        self.device = device

        # Lazily initialize if not provided and dependencies available
        if self.reader is None and easyocr is not None:
            gpu = (torch is not None and torch.cuda.is_available())
            self.reader = easyocr.Reader(['en'], gpu=gpu)

        if self.summarizer is None and pipeline is not None:
            dev = 0 if (torch is not None and torch.cuda.is_available()) else -1
            self.summarizer = pipeline("summarization", model="t5-small", device=dev)

    def extract_text(self):
        if cv2 is None or self.reader is None:
            raise RuntimeError("OpenCV or EasyOCR not available")

        cap = cv2.VideoCapture(self.video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            fps = 24

        extracted_lines = []
        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 1 second
            if frame_count % fps == 0:
                results = self.reader.readtext(frame)
                frame_text = " ".join([res[1] for res in results])
                clean_line = clean_ocr_text(frame_text)

                if clean_line and len(clean_line) > 5:
                    if not extracted_lines:
                        extracted_lines.append(clean_line)
                    else:
                        if not is_similar(clean_line, extracted_lines[-1]):
                            extracted_lines.append(clean_line)

            frame_count += 1

        cap.release()
        return extracted_lines

    def generate_summary(self, text, min_length=30, max_length=150):
        if not self.summarizer:
            raise RuntimeError("Summarizer not available")

        if len(text) < 50:
            return "Text too short to summarize."

        try:
            summary_output = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            return summary_output[0].get('summary_text', '')
        except Exception as e:
            return f"Error summarizing: {e}"


# Module exported symbols
__all__ = ["VideoTextProcessor"]
