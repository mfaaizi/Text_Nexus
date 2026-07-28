import logging
import torch
import re
import difflib
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

logger = logging.getLogger(__name__)

class GrammarServiceVennify:
    """
    Grammar checking service using Vennify T5 model (vennify/t5-base-grammar-correction).
    Fully CPU compatible. Generates corrected text and detailed suggestions.
    """

    def __init__(self):
        self.model_name = "vennify/t5-base-grammar-correction"
        self.device = torch.device("cpu")
        self.model = None
        self.tokenizer = None
        self.is_ready = False

        try:
            logger.info(f"Loading grammar model: {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            self.is_ready = True
            logger.info("Grammar model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load grammar model: {str(e)}")
            self.is_ready = False

    def check_grammar(self, text: str) -> dict:
        """
        Check and correct grammar in the provided text.
        Returns original_text, corrected_text, errors_count, suggestions.
        """
        if not self.is_ready:
            return {
                "original_text": text,
                "corrected_text": text,
                "errors_count": 0,
                "suggestions": [],
                "error": "Grammar service not available"
            }

        if not text.strip():
            return {
                "original_text": text,
                "corrected_text": text,
                "errors_count": 0,
                "suggestions": []
            }

        try:
            # Add prefix for T5 grammar correction
            input_text = "correct grammar: " + text

            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=512,
                    num_beams=5,
                    early_stopping=True
                )

            corrected_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Apply simple rule-based fixes for tense with time words
            corrected_text = self._enforce_past_tense(corrected_text, text)

            # Generate word-level suggestions
            suggestions = self._generate_suggestions(text, corrected_text)

            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "errors_count": len(suggestions),
                "suggestions": suggestions
            }

        except Exception as e:
            logger.error(f"Grammar check failed: {str(e)}")
            return {
                "original_text": text,
                "corrected_text": text,
                "errors_count": 0,
                "suggestions": [],
                "error": str(e)
            }

    def _enforce_past_tense(self, corrected_text, original_text):
        """
        Simple heuristic: if the original text has time words like 'yesterday', 
        convert present tense verbs to past tense.
        """
        time_words = ["yesterday", "last week", "ago", "last night", "this morning"]
        if any(word in original_text.lower() for word in time_words):
            # Basic replacements for common present forms
            corrected_text = corrected_text.replace(" are looking", " looked")
            corrected_text = corrected_text.replace(" am going", " went")
            corrected_text = corrected_text.replace(" is going", " went")
            corrected_text = corrected_text.replace(" is ", " was ")
            corrected_text = corrected_text.replace(" have ", " had ")
        return corrected_text

    def _generate_suggestions(self, original, corrected):
        """
        Compare original and corrected text to generate a list of suggestions.
        Uses difflib to find word-level differences and maps them to offsets.
        """
        try:
            def tokenize_with_offsets(text):
                tokens = []
                for match in re.finditer(r'\S+', text):
                    tokens.append({
                        'text': match.group(),
                        'start': match.start(),
                        'end': match.end()
                    })
                return tokens

            orig_tokens = tokenize_with_offsets(original)
            corr_tokens = tokenize_with_offsets(corrected)

            orig_words = [t['text'] for t in orig_tokens]
            corr_words = [t['text'] for t in corr_tokens]

            matcher = difflib.SequenceMatcher(None, orig_words, corr_words)
            suggestions = []

            for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
                if opcode == 'equal':
                    continue

                start_offset = orig_tokens[i1]['start'] if i1 < len(orig_tokens) else len(original)
                end_offset = orig_tokens[i2 - 1]['end'] if i2 - 1 < len(orig_tokens) else len(original)

                if opcode == 'insert':
                    replacement = " ".join(corr_words[j1:j2])
                    start_offset = orig_tokens[i1 - 1]['end'] + 1 if i1 > 0 else 0
                    end_offset = start_offset
                elif opcode == 'delete':
                    replacement = ""
                elif opcode == 'replace':
                    replacement = " ".join(corr_words[j1:j2])

                suggestions.append({
                    "offset": start_offset,
                    "length": end_offset - start_offset,
                    "message": f"Change to '{replacement}'",
                    "replacements": [replacement],
                    "ruleId": "GRAMMAR_CORRECTION",
                    "category": "Grammar"
                })

            return suggestions
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
