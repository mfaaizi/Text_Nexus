# Paraphraser Module
import time
import os
import random
import re
import string
from pathlib import Path
import logging

# Initialize logger first
logger = logging.getLogger(__name__)

# Import torch
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.error("PyTorch not installed")

# Check transformers
TRANSFORMERS_AVAILABLE = True
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available")

# Check NLTK
NLTK_AVAILABLE = True
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import wordnet
    from nltk.tag import pos_tag
except ImportError:
    NLTK_AVAILABLE = False
    logger.warning("nltk not available")

# Check pandas
PANDAS_AVAILABLE = True
try:
    import pandas as pd
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available")

# Check sentence transformers
SENTENCE_TRANSFORMERS_AVAILABLE = True
try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence_transformers not available")


class T5ParaphrasingService:
    """Production paraphrasing service using T5 model"""
    
    def __init__(self):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required but not installed!")
            
        self.models_loaded = False
        self.device = torch.device("cpu")  # Force CPU-only operation
        self.t5_model = None
        self.t5_tokenizer = None
        self.sentence_model = None
        self.synonyms_df = None
        self.model_path = self._detect_model_path()
        self.model_load_error = None
        
        self.load_models()

    def load_models(self):
        """Load all available models"""
        try:
            logger.info("Loading paraphrasing models...")

            if TRANSFORMERS_AVAILABLE:
                logger.info(f"Using device: {self.device} (CPU-only mode)")
                self.load_t5_model()

            if NLTK_AVAILABLE:
                self.download_nltk_data()

            if SENTENCE_TRANSFORMERS_AVAILABLE:
                try:
                    self.sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                    logger.info("Sentence transformer loaded")
                except Exception as e:
                    logger.warning(f"Could not load sentence transformer: {e}")
                    self.sentence_model = None

            if PANDAS_AVAILABLE:
                self.load_synonyms_dataset()

            self.models_loaded = True
            logger.info("Service initialization complete")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            self.models_loaded = False

    def _detect_model_path(self):
        """Return a directory containing a valid T5 model (config.json present)."""
        candidates = [
            Path("model/t5_paraphraser_model"),
            Path("model"),
        ]
        for path in candidates:
            if (path / "config.json").exists() and (path / "tokenizer_config.json").exists():
                return path
        return Path("model/t5_paraphraser_model")

    def load_t5_model(self):
        """Load the specified T5 paraphrasing model (CPU-only)."""
        model_id = "humarin/chatgpt_paraphraser_on_T5_base"
        
        try:
            logger.info(f"Loading model: {model_id}")
            self.t5_tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.t5_model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
            self.t5_model.to(self.device)
            self.t5_model.eval()
            logger.info(f"T5 model loaded successfully from: {model_id}")
            self.model_load_error = None
        except Exception as e:
            self.model_load_error = str(e)
            logger.error(f"Failed to load T5 model from {model_id}: {e}")
            self.t5_model = None
            self.t5_tokenizer = None

    def download_nltk_data(self):
        """Download required NLTK datasets with correct resource paths"""
        if not NLTK_AVAILABLE:
            return
            
        resource_map = {
            'punkt': 'tokenizers/punkt',
            'wordnet': 'corpora/wordnet',
            'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
        }
        for dataset, resource_path in resource_map.items():
            try:
                nltk.data.find(resource_path)
            except LookupError:
                logger.info(f"Downloading NLTK dataset: {dataset}")
                try:
                    nltk.download(dataset, quiet=True)
                except Exception as e:
                    logger.warning(f"Could not download {dataset}: {e}")
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            try:
                nltk.download('averaged_perceptron_tagger_eng', quiet=True)
            except Exception:
                pass

    def load_synonyms_dataset(self):
        """Load synonyms CSV if available"""
        try:
            synonyms_path = Path("data/synonyms.csv")
            if synonyms_path.exists():
                self.synonyms_df = pd.read_csv(synonyms_path)
                logger.info("Synonyms dataset loaded")
            else:
                self.synonyms_df = None
        except Exception as e:
            logger.warning(f"Could not load synonyms dataset: {str(e)}")
            self.synonyms_df = None

    def _restore_original_formatting(self, original_text, paraphrased_text):
        """Restore the original formatting, capitalization, and structure"""
        try:
            if original_text.strip() == paraphrased_text.strip():
                return paraphrased_text
            
            cleaned_para = re.sub(r'\s+', ' ', paraphrased_text.strip())
            
            if original_text and original_text[0].isupper() and cleaned_para:
                cleaned_para = cleaned_para[0].upper() + cleaned_para[1:]
            
            cleaned_para = re.sub(r'([.!?]+\s*)([a-z])', lambda m: m.group(1) + m.group(2).upper(), cleaned_para)
            
            if original_text.rstrip()[-1:] in '.!?' and cleaned_para and cleaned_para.rstrip()[-1:] not in '.!?':
                cleaned_para = cleaned_para.rstrip() + original_text.rstrip()[-1]
            
            return cleaned_para
            
        except Exception as e:
            logger.warning(f"Formatting restoration failed: {e}")
            return paraphrased_text

    def t5_paraphrase(self, text, mode="standard"):
        """Use T5 model for paraphrasing with tone support"""
        if not self.t5_model or not self.t5_tokenizer:
            return self.simple_word_replacement(text, mode)

        try:
            # Try to use tone_engine if available
            try:
                from utils.tone_engine import ToneEngine
                tone_engine = ToneEngine(
                    model=self.t5_model,
                    tokenizer=self.t5_tokenizer,
                    device=self.device
                )
                
                tone_map = {
                    'formal': 'formal',
                    'informal': 'informal',
                    'creative': 'creative',
                    'standard': 'creative',
                    'shorten': 'creative',
                    'expand': 'creative'
                }
                tone = tone_map.get(mode, 'creative')
                
                paraphrased = tone_engine.paraphrase_long_text(text, tone)
                logger.info(f"Tone engine returned: {paraphrased[:100]}...")
                return paraphrased
            except ImportError:
                # Fallback if tone_engine not available
                logger.warning("tone_engine not available, using basic T5")
                input_text = f"paraphrase: {text}"
                inputs = self.t5_tokenizer(
                    input_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.t5_model.generate(
                        inputs.input_ids,
                        max_length=512,
                        num_beams=5,
                        early_stopping=True
                    )
                
                result = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
                return result

        except Exception as e:
            logger.error(f"T5 error: {str(e)}")
            return self.simple_word_replacement(text, mode)

    def _phrase_tweaks(self, text):
        """Apply simple phrase-level paraphrasing tweaks."""
        replacements = [
            (r"\bin order to\b", "to"),
            (r"\bsuch as\b", "like"),
            (r"\bis able to\b", "can"),
            (r"\butilize\b", "use"),
            (r"\bcommence\b", "begin"),
            (r"\bmoreover\b", "also"),
            (r"\btherefore\b", "so"),
        ]
        tweaked = text
        for pattern, repl in replacements:
            tweaked = re.sub(pattern, repl, tweaked, flags=re.IGNORECASE)
        tweaked = re.sub(r"\s+([,.;:!?])", r"\1", tweaked)
        return tweaked

    def simple_word_replacement(self, text, mode="standard"):
        """Fallback paraphrasing using word replacements"""
        if not NLTK_AVAILABLE:
            return text
            
        try:
            working_text = self._phrase_tweaks(text)

            def generate_once(source_text, rate, min_len):
                tokens = word_tokenize(source_text)
                tagged = pos_tag(tokens)
                new_tokens = []
                changed_any = False
                candidates_info = []

                for i, (tok, tag) in enumerate(tagged):
                    if tok.isalpha() and len(tok) >= min_len and random.random() < rate and tag[0] in {"J", "N", "V", "R"}:
                        syns = []
                        for syn in wordnet.synsets(tok):
                            for lemma in syn.lemmas():
                                s = lemma.name().replace("_", " ")
                                if s.lower() != tok.lower():
                                    syns.append(s)
                        if syns:
                            candidates_info.append((i, tok, syns))
                            replacement = random.choice(syns)
                            if tok.isupper():
                                replacement = replacement.upper()
                            elif tok[0].isupper():
                                replacement = replacement.capitalize()
                            new_tokens.append(replacement)
                            changed_any = True
                            continue
                    new_tokens.append(tok)

                if not changed_any and candidates_info:
                    i, tok, syns = max(candidates_info, key=lambda t: len(t[1]))
                    forced = random.choice(syns)
                    if tok.isupper():
                        forced = forced.upper()
                    elif tok[0].isupper():
                        forced = forced.capitalize()
                    new_tokens[i] = forced
                    changed_any = True

                result = " ".join(new_tokens)
                result = re.sub(r"\s+([,.;:!?])", r"\1", result)
                return result, changed_any

            configs = [
                ( {"standard": 0.35, "creative": 0.55, "formal": 0.25, "shorten": 0.25, "expand": 0.45}.get(mode, 0.35), 4 ),
                ( {"standard": 0.5,  "creative": 0.7,  "formal": 0.35, "shorten": 0.35, "expand": 0.55}.get(mode, 0.5), 3 ),
                ( {"standard": 0.7,  "creative": 0.85, "formal": 0.5,  "shorten": 0.5,  "expand": 0.7 }.get(mode, 0.7), 2 ),
            ]

            attempt = working_text
            changed = False
            for rate, min_len in configs:
                attempt, changed = generate_once(attempt, rate, min_len)
                if changed:
                    break

            result = self._restore_original_formatting(text, attempt)
            if result.strip() == text.strip():
                result = self._phrase_tweaks(result)
            return result
            
        except Exception as e:
            logger.error(f"Simple replacement error: {str(e)}")
            return text

    def paraphrase(self, text, mode="standard"):
        """Main paraphrasing entry point"""
        if not text.strip():
            return text

        if self.t5_model and self.t5_tokenizer:
            return self.t5_paraphrase(text, mode)
        else:
            return self.simple_word_replacement(text, mode)

    def get_paraphrases(self, text, modes=None):
        """Get paraphrases for multiple modes"""
        if modes is None:
            modes = ["standard", "creative", "formal"]
            
        results = {}
        for mode in modes:
            try:
                results[mode] = self.paraphrase(text, mode)
            except Exception as e:
                logger.error(f"Error in mode {mode}: {str(e)}")
                results[mode] = text
                
        return results

    def pick_best(self, original_text, candidates_dict):
        """Pick the best candidate using similarity if available, otherwise heuristic."""
        try:
            candidates = [v for v in candidates_dict.values() if isinstance(v, str) and v.strip()]
            if not candidates:
                return original_text

            try:
                from utils.humaniser import Humanizer
                humaniser = Humanizer()
                return humaniser.humanize(original_text, candidates)
            except Exception:
                pass

            if SENTENCE_TRANSFORMERS_AVAILABLE:
                if self.sentence_model is None:
                    try:
                        self.sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                    except Exception:
                        self.sentence_model = None
                if self.sentence_model is not None:
                    orig_emb = self.sentence_model.encode(original_text, convert_to_tensor=True)
                    cand_embs = self.sentence_model.encode(candidates, convert_to_tensor=True)
                    sims = util.pytorch_cos_sim(orig_emb, cand_embs)[0].cpu().tolist()
                    best_idx = max(range(len(sims)), key=lambda i: sims[i])
                    return candidates[best_idx]

            def change_ratio(a, b):
                return abs(len(a) - len(b)) / max(1, len(a))
            candidates_sorted = sorted(candidates, key=lambda c: change_ratio(original_text, c), reverse=True)
            return candidates_sorted[0]
        except Exception:
            return original_text