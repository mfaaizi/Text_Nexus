<div align="center">


# Text Nexus AI

### AI-Powered Text Processing Mobile Application

[![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.2-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗_HuggingFace-Transformers-FFD21E?style=for-the-badge)](https://huggingface.co)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

> **Final Year Project** — BS Artificial Intelligence (2022–2026)
> 
> Department of Computer Science, National Textile University, Faisalabad, Pakistan

[Features](#-features) • [Architecture](#️-architecture) • [Tech Stack](#️-tech-stack) • [Setup](#-setup--installation) • [API](#-api-reference) • [Developer](#-developer)

</div>

---

## 📌 Overview

**Text Nexus AI** is a full-stack mobile application that brings the power of state-of-the-art Natural Language Processing (NLP) to your fingertips. Built with Flutter for a seamless cross-platform mobile experience and powered by a Python Flask backend serving transformer-based AI models, Text Nexus AI provides six core text intelligence features through an intuitive, beautifully designed interface.

The application follows a **Client-Server Architecture** where the Flutter mobile app communicates with a local Python API server running HuggingFace transformer models for real-time AI inference.

---

## ✨ Features

| # | Feature | Model Used | Status |
|---|---------|------------|--------|
| 1 | 📝 **Grammar Correction** | `vennify/t5-base-grammar-correction` | ✅ Working |
| 2 | 🔄 **Text Paraphrasing** | `humarin/chatgpt_paraphraser_on_T5_base` | ✅ Working |
| 3 | 📄 **Text Summarization** | `t5-small` | ✅ Working |
| 4 | 🧑 **Text Humanization** | T5-based Custom Model | ✅ Working |
| 5 | 😊 **Emotion Analysis** | `bhadresh-savani/distilbert-base-uncased-emotion` | ✅ Working |
| 6 | 🎬 **Video Text Extraction** | — | ⚠️ Placeholder |

### 🔐 Authentication Features
- ✅ Email/Password Sign Up & Login
- ✅ Google Sign-In (OAuth 2.0)
- ✅ Persistent Login Sessions
- ✅ Secure Logout

### 📊 App Features
- ✅ Processing History (Firebase Firestore)
- ✅ User Profile Management
- ✅ Splash Screen with Animation
- ✅ Rich Maroon UI Theme

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE APPLICATION                       │
│                    (Flutter / Dart)                         │
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│   │  Auth    │  │  Home    │  │ Feature  │  │ History  │  │
│   │  Screen  │  │  Screen  │  │ Screens  │  │ Screen   │  │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                        │                                    │
│              ┌─────────┴──────────┐                        │
│              │    Services Layer  │                        │
│              │  NLPService        │                        │
│              │  GoogleAuthService │                        │
│              └─────────┬──────────┘                        │
└────────────────────────┼────────────────────────────────────┘
│ HTTP / WiFi
┌───────────────┼───────────────┐
│               │               │
▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Firebase  │  │ Flask API   │  │  Firestore  │
│    Auth     │  │   Server    │  │  Database   │
└─────────────┘  └──────┬──────┘  └─────────────┘
│
┌──────────────┼──────────────┐
│              │              │
▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Grammar  │  │Paraphrase│  │Summarize │
│  Model   │  │  Model   │  │  Model   │
└──────────┘  └──────────┘  └──────────┘

---

## 🛠️ Tech Stack

### 📱 Frontend (Mobile App)

| Technology | Version | Purpose |
|------------|---------|---------|
| Flutter | 3.x | Cross-platform UI Framework |
| Dart | 3.x | Programming Language |
| Firebase Auth | ^5.3.1 | User Authentication |
| Cloud Firestore | ^5.4.4 | Cloud Database |
| Google Sign-In | ^6.2.1 | OAuth Authentication |
| HTTP | ^1.2.0 | API Communication |

### 🐍 Backend (API Server)

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10 | Programming Language |
| Flask | 3.0.0 | Web API Framework |
| PyTorch | 2.1.2 | ML Framework |
| Transformers | 4.35.2 | NLP Models (HuggingFace) |
| NLTK | Latest | Text Preprocessing |
| NumPy | 1.23.5 | Numerical Computing |

### ☁️ Cloud & Infrastructure

| Service | Purpose |
|---------|---------|
| Firebase Authentication | User login & session management |
| Cloud Firestore | NoSQL database for history & user data |
| HuggingFace Hub | Pre-trained model repository |

---

## 📁 Project Structure
Text_Nexus/
│
├── 📱 frontend/                          # Flutter Mobile Application
│   ├── lib/
│   │   ├── main.dart                     # App entry point & auth wrapper
│   │   ├── screens/
│   │   │   ├── splash_screen.dart        # Animated splash screen
│   │   │   ├── login_signup_choice_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── signup_screen.dart
│   │   │   ├── home_screen.dart          # Main dashboard
│   │   │   ├── profile_screen.dart
│   │   │   ├── history_screen.dart
│   │   │   └── features/
│   │   │       ├── paraphrasing_screen.dart
│   │   │       ├── grammar_checker_screen.dart
│   │   │       ├── summarization_screen.dart
│   │   │       ├── humanize_text_screen.dart
│   │   │       ├── emotion_analyzer_screen.dart
│   │   │       └── video_text_extract_screen.dart
│   │   └── services/
│   │       ├── nlp_service.dart          # Python API communication
│   │       └── google_auth_service.dart  # Google Sign-In
│   ├── assets/
│   │   └── images/
│   │       └── logo.png
│   ├── android/
│   │   └── app/
│   │       └── build.gradle.kts
│   └── pubspec.yaml
│
├── 🐍 backend/                           # Python Flask API Server
│   ├── app.py                            # Main Flask server
│   ├── requirements.txt                  # Python dependencies
│   ├── grammar/
│   │   ├── init.py
│   │   └── grammar_checker.py            # T5 Grammar Model
│   ├── paraphraser/
│   │   ├── init.py
│   │   └── paraphraser.py                # T5 Paraphrasing Model
│   ├── summarizer/
│   │   ├── init.py
│   │   └── summarizer.py                 # T5 Summarization Model
│   ├── sentiment/
│   │   ├── init.py
│   │   └── sentiment_module.py           # DistilBERT Emotion Model
│   ├── Text_Humanizer/
│   │   └── use_model.py                  # Text Humanization
│   └── video_module/
│       └── video_module.py               # Video Processing (Placeholder)
│
├── .gitignore
└── README.md

---

## ⚙️ Setup & Installation

### Prerequisites
✅ Python 3.10 installed
✅ Flutter 3.x installed
✅ Android Studio / VS Code installed
✅ Android device with USB debugging enabled
✅ Firebase project configured
✅ Both devices on same WiFi network

---

### 🐍 Backend Setup

**1. Navigate to backend folder:**
```bash
cd backend
```

**2. Create virtual environment (recommended):**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Start the server:**
```bash
python app.py
```

**5. Note the Network IP from output:**
🔗 Network: http://YOUR_IP:5000   ← Copy this IP!
✅ Server ready! Waiting for requests...

---

### 📱 Frontend Setup

**1. Navigate to frontend folder:**
```bash
cd frontend
```

**2. Update server IP:**

Open `lib/services/nlp_service.dart`:
```dart
static const String _computerIP = 'YOUR_IP_HERE';  // ← Paste your IP
```

**3. Install Flutter dependencies:**
```bash
flutter pub get
```

**4. Connect Android device via USB and run:**
```bash
flutter run
```

**5. After app opens on phone, USB can be removed!**
   The app communicates with the server via WiFi.

---

### 🔥 Firebase Setup

1. Create project at [Firebase Console](https://console.firebase.google.com/)
2. Add Android app with package name: `com.example.Text_Nexus`
3. Enable **Email/Password** and **Google** authentication
4. Create **Firestore Database** (test mode)
5. Download `google-services.json` → place in `frontend/android/app/`
6. Add SHA-1 fingerprint for Google Sign-In:
```bash
cd frontend/android
gradlew signingReport
```

---

## 🌐 API Reference

Base URL: `http://YOUR_IP:5000`

| Endpoint | Method | Description | Body |
|----------|--------|-------------|------|
| `/health` | GET | Server health check | — |
| `/api/paraphrase` | POST | Paraphrase text | `{"text": "...", "mode": "standard"}` |
| `/api/grammar-check` | POST | Check grammar | `{"text": "..."}` |
| `/api/summarize` | POST | Summarize text | `{"text": "..."}` |
| `/api/humanize` | POST | Humanize AI text | `{"text": "..."}` |
| `/api/sentiment` | POST | Analyze emotions | `{"text": "..."}` |

### Example Request:
```bash
curl -X POST http://YOUR_IP:5000/api/paraphrase \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "mode": "standard"}'
```

### Example Response:
```json
{
  "success": true,
  "original_text": "Hello, how are you?",
  "paraphrased_text": "Hi, how are you doing?",
  "mode": "standard"
}
```

---

## 📋 Requirements

### Backend Dependencies
flask==3.0.0
flask-cors==4.0.0
torch==2.1.2
transformers==4.35.2
huggingface-hub==0.20.3
sentence-transformers==2.2.2
nltk==3.8.1
numpy==1.23.5
tensorflow==2.13.0

### Frontend Dependencies
```yaml
firebase_core: ^3.6.0
firebase_auth: ^5.3.1
cloud_firestore: ^5.4.4
google_sign_in: ^6.2.1
http: ^1.2.0
```

---

## 🧪 Testing

### Test Backend:
```bash
# Health check
curl http://YOUR_IP:5000/health

# Test paraphrasing
curl -X POST http://YOUR_IP:5000/api/paraphrase \
  -H "Content-Type: application/json" \
  -d '{"text": "The quick brown fox jumps over the lazy dog."}'
```

### Test Frontend:
1. Open app on phone
2. Login with email/password or Google
3. Navigate to any feature
4. Enter test text and submit
5. Verify result appears

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `No route to host` | Update IP in `nlp_service.dart` |
| `Connection refused` | Start Python server first |
| `Model not loading` | Check Python package versions |
| `Google Sign-In failed` | Verify SHA-1 in Firebase |
| `History not loading` | Create Firestore composite index |
| IP changes every time | Set static IP on your computer |

---

## 🚀 Future Enhancements

- [ ] Cloud deployment (AWS/GCP)
- [ ] iOS support
- [ ] Video text extraction implementation
- [ ] Multi-language support
- [ ] Offline mode with cached models
- [ ] Dark mode UI
- [ ] Export results as PDF/DOCX

---

## 👨‍💻 Developer

<div align="center">

**Muhammad Faaizi**

*BS Artificial Intelligence — National Textile University, Faisalabad*

[![GitHub](https://img.shields.io/badge/GitHub-mfaaizi-181717?style=for-the-badge&logo=github)](https://github.com/mfaaizi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-faaizi-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/faaizi)

</div>

---

## 📄 License
MIT License
Copyright (c) 2026 Muhammad Faaizi
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

---

<div align="center">

**⭐ If you found this project helpful, please give it a star!**

Made with ❤️ by [Muhammad Faaizi](https://github.com/mfaaizi)

*Text Nexus AI — Bringing AI to Your Fingertips*

</div>
