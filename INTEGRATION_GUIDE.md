# AI Modules Integration Guide

This package contains the Python backend modules for the AI writing assistant features: Paraphraser, Grammar Checker, and Summarizer.

## 📦 content Structure

- **paraphraser/**: Contains the core paraphrasing logic using T5.
- **grammar/**: Contains the grammar checking service.
- **summarizer/**: Contains the document summarization service.
- **utils/**: Shared utility scripts (text processing, tone engine, etc.).
- **requirements.txt**: Python dependencies.

## 🚀 Setup & Installation

1. **Install Dependencies**
   Ensure Python 3.8+ is installed. Run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Model Download**
   The first time you initialize these services, they will attempt to download the necessary AI models (HuggingFace Transformers, NLTK data) automatically. Ensure you have an internet connection during the first run.

## 💻 Usage Examples

These modules are designed to be used in a Python backend (e.g., Flask, Django, FastAPI) that your mobile app communicates with via API.

### 1. Paraphraser

```python
from paraphraser.paraphraser import T5ParaphrasingService

# Initialize Service (Loads model - might take time)
paraphraser = T5ParaphrasingService()

text = "The quick brown fox jumps over the lazy dog."

# Modes: 'standard', 'formal', 'informal', 'creative', 'shorten', 'expand'
result = paraphraser.paraphrase(text, mode='formal')
print(result)
```

### 2. Grammar Checker

```python
from grammar.grammar_checker import GrammarServiceVennify

# Initialize Service
grammar = GrammarServiceVennify()

text = "I is going to the store."

# Returns dict with corrections and suggestions
result = grammar.check_grammar(text)
print(result['corrected_text']) # "I am going to the store."
print(result['suggestions'])    # List of specific errors and fixes
```

### 3. Summarizer

```python
from summarizer.summarizer import SummarizerService

# Initialize Service
summarizer = SummarizerService()

long_text = "Artificial intelligence (AI) is intelligence demonstrated by machines..."

# Returns dict with summary
result = summarizer.summarize(long_text)
print(result['summary_text'])
```

## 📱 Mobile App Integration Strategy

Since these are Python-based AI models:
1. **Backend API**: Host these modules on a server (AWS, GCP, etc.) using a framework like Flask or FastAPI.
2. **API Endpoints**: Create endpoints (e.g., `/api/paraphrase`, `/api/grammar`, `/api/summarize`) that your mobile app calls.
3. **JSON Communication**: Have the mobile app send JSON data (`{"text": "..."}`) and display the returned results.

**Note**: running these heavy Transformer models directly on a mobile device (client-side) is generally not recommended due to battery and memory constraints. Using this Python backend is the preferred approach.
