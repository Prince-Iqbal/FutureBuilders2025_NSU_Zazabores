# স্বাস্থ্য সহায়ক (Health Assistant)

## 🏥 Offline-First Healthcare PWA for Rural Bangladesh

A mobile-first Progressive Web Application designed to help people in Bangladesh's rural and hill tract regions access basic medical guidance despite limited or intermittent internet connectivity.

![Health Assistant Screenshot](./assets/screenshot.png)

---

## 👥 Team Information

- **Team Name:** NSU_Zazabores
- **Members:** 
1. 
name: Iqbal Bahar Prince
email: iqbal.prince@northsouth.edu
phone number: 01794689278
2. 
name: Bhuyian Arshan Rashid Dibbo
email: bhuyian.dibbo.252@northsouth.edu
phone number: 01406617458
3. 
name: Md. Samin Yasir
email: saminyasir820@gmail.com
phone number: 01972659706
- **Hackathon:** Future Builders AI-Driven Cognitive Innovation Hackathon

---

## 📋 Problem Statement

Bangladesh's rural and hill tract regions face significant healthcare accessibility challenges:

- **Limited Internet Connectivity:** Many areas have intermittent or no internet access
- **Healthcare Worker Shortage:** Few trained medical professionals in remote areas
- **Language Barriers:** Medical information often unavailable in simple Bangla
- **Delayed Treatment:** Lack of triage knowledge leads to delayed emergency care

### Target Users
- Rural villagers with limited tech literacy
- Community health workers
- Family members seeking guidance for sick relatives

---

## 💡 Solution Overview

**স্বাস্থ্য সহায়ক (Health Assistant)** provides:

1. **AI-Powered Symptom Triage:** Classifies symptoms into Emergency/Moderate/Mild
2. **Bilingual Support:** Full Bangla + English interface with icons
3. **Offline Functionality:** Works without internet using rule-based fallback
4. **Sync Capability:** Queues data for sync when internet is available

### Key Features
- ✅ Icon-based symptom selection (accessible for low-literacy users)
- ✅ 22 common symptoms with Bangla translations
- ✅ AI explainability (shows why classification was made)
- ✅ Clear safety disclaimers in both languages
- ✅ Consultation history tracking
- ✅ User profile management (age, gender, location)

---

## 🧠 AI Architecture & Logic

### Primary: Google Gemini Integration
- **Model:** Gemini 2.0 Flash
- **Integration:** Via Emergent LLM Key (OpenAI-compatible)
- **Function:** Symptom classification and guidance generation

### Fallback: Rule-Based System
When AI is unavailable, a deterministic rule-based system provides triage:

```
Severity Weight System:
- Emergency symptoms (chest pain, breathing difficulty): 5 points
- Moderate symptoms (fever, vomiting): 2 points
- Mild symptoms (cold, headache): 1 point

Modifiers:
- Children < 5 years: +2 points
- Elderly > 60 years: +2 points
- Duration > 3 days: +2 points

Classification:
- Emergency symptom present → EMERGENCY
- Total weight ≥ 8 → MODERATE
- Total weight < 8 → MILD
```

### Explainability
Every result includes:
1. Why this classification was made
2. Contributing symptoms and risk factors
3. Clear action steps in simple language

---

## 🌐 Offline & Low-Internet Handling

### Architecture
```
┌─────────────────────────────────────────┐
│         Offline-First Strategy          │
├─────────────────────────────────────────┤
│ 1. LOCAL FIRST                          │
│    - All symptom data cached locally    │
│    - User profile stored in device      │
│    - History saved offline              │
│                                         │
│ 2. QUEUE SYSTEM                         │
│    - Pending syncs stored in queue      │
│    - Auto-retry when online             │
│    - Compressed JSON payloads           │
│                                         │
│ 3. NETWORK DETECTION                    │
│    - Auto-detect connectivity           │
│    - Switch between AI/Rule modes       │
│    - Clear offline indicators           │
└─────────────────────────────────────────┘
```

### Data Storage
| Data Type | Storage | Sync Strategy |
|-----------|---------|---------------|
| Symptoms Master | AsyncStorage | Pre-loaded |
| User Profile | AsyncStorage + Server | Sync on change |
| Consultations | AsyncStorage + Server | Queue for sync |

---

## 🛠 Technologies Used

### Frontend
| Technology | Purpose |
|------------|---------|
| React Native (Expo) | Cross-platform mobile app |
| TypeScript | Type safety |
| AsyncStorage | Local data persistence |
| Expo Router | Navigation |
| @expo/vector-icons | Icon system |
| Zustand | State management |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM |
| Google Generative AI SDK | Direct Gemini integration |
| Uvicorn | ASGI server |

### Cloud Infrastructure
| Technology | Purpose |
|------------|---------|
| Google Cloud Run | Serverless container hosting |
| Cloud SQL (PostgreSQL 15) | Managed database |
| Google AI Studio | Gemini 2.0 Flash API |
| Cloud Build | CI/CD pipeline |

### AI Integration
| Technology | Purpose |
|------------|---------|
| Google Gemini 2.0 Flash | AI-powered symptom triage |
| Rule-Based Fallback | Offline triage algorithm |

---

## 📱 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/symptoms` | GET | Get all symptoms |
| `/api/users` | POST | Create user profile |
| `/api/users/{id}` | GET/PUT | Get/Update user |
| `/api/triage` | POST | AI-powered triage |
| `/api/triage/offline` | POST | Rule-based triage |
| `/api/consultations/{user_id}` | GET | Get history |
| `/api/sync` | POST | Sync offline data |

---

## 🤖 AI Tools Disclosure (FutureBuilders 2025 Requirement)

### AI Technologies in Application
1. **Google Gemini 2.0 Flash** (via Google AI Studio API)
   - Primary AI for symptom classification and medical triage
   - Provides bilingual medical guidance (Bangla + English)
   - Classifies severity into: emergency/moderate/mild
   - Accessed directly through Google AI Studio API (no intermediaries)
   - Code Location: `backend/server.py` lines 243-305

2. **Google Gemini 2.5 Flash Native Audio Preview** (Voice Assistant)
   - Real-time Bangla voice conversation for symptom collection
   - Natural language understanding for health triage
   - Low-latency audio streaming via Gemini Live API
   - Code Location: `sustho-agent/services/geminiService.ts`

3. **Google Gemini 3 Flash Preview** (Voice Assistant)
   - Conversation history analysis and triage summarization
   - Structured JSON output for medical reports
   - Code Location: `sustho-agent/services/geminiService.ts`

4. **Google Gemini 2.5 Flash TTS** (Voice Assistant)
   - Text-to-speech for guidance audio playback
   - Natural Bangla pronunciation using 'Kore' voice
   - Code Location: `sustho-agent/services/geminiService.ts`

5. **Google Gemini 2.5 Flash with Google Maps Tool** (Voice Assistant)
   - Geolocation-based hospital suggestions
   - Real-time facility discovery using Maps grounding
   - Code Location: `sustho-agent/services/geminiService.ts`

6. **Rule-Based Fallback System**
   - Deterministic algorithm for offline operation
   - Weight-based severity classification using symptom severity scores
   - Age modifiers (children <5, elderly >60 get higher risk scores)
   - Duration modifiers (symptoms >3 days increase severity)
   - Ensures functionality in areas with zero internet connectivity

### AI Development Assistants Used
During the development of this project, we utilized the following AI coding assistants:
- **Claude 3.5 Sonnet** - Architecture design, code review, documentation, migration planning, deployment configuration
- **GitHub Copilot** - Code completion and suggestions for TypeScript/Python code
- **ChatGPT** - Research, problem-solving, algorithm design, Bangla translation assistance
- **Various AI Tools** - Voice assistant development, PDF generation logic, React component structure

**All AI-generated code was thoroughly reviewed, tested, and validated by the team members.**

### Ethical & Safety Considerations
- ⚠️ **Not a diagnostic tool** - Clearly stated in all outputs and disclaimers
- ⚠️ **No prescriptions** - Only provides general guidance, never prescribes medications
- ⚠️ **Emergency emphasis** - Always recommends hospital for serious symptoms
- ⚠️ **Disclaimers** - Present in both Bangla (এটি চিকিৎসা পরামর্শ নয়) and English ("This is not medical advice")
- ⚠️ **Human oversight recommended** - Not a replacement for medical professionals
- ⚠️ **Privacy-focused** - No patient data shared with third parties

---

## ⚠️ Safety & Compliance

### Medical Safety
1. App never diagnoses conditions
2. Emergency symptoms ALWAYS trigger red alert
3. Disclaimers shown on every result
4. When uncertain, defaults to higher severity

### Disclaimers
**Bangla:** এটি চিকিৎসা পরামর্শ নয়। ডাক্তারের সাথে যোগাযোগ করুন।

**English:** This is not medical advice. Please consult a doctor.

---

## 🌐 Offline-First Architecture (Limited Internet Access)

This application is specifically designed for Bangladesh's rural areas and hill tracts with unreliable or no internet connectivity.

### How Offline Mode Works

**1. Local-First Storage**
- All symptoms cached in device storage (AsyncStorage)
- User profiles stored locally before syncing to server
- Consultation history accessible offline
- No internet required for basic functionality

**2. Smart AI Fallback**
```
Internet Available    → Google Gemini AI Triage (cloud-based, intelligent)
Internet Unavailable  → Rule-Based Triage (local, deterministic)
Slow Connection (>10s)→ Auto-fallback to local rules
```

**3. Sync Queue Mechanism**
- Offline consultations queued locally in device storage
- Auto-sync when internet connection restored
- Background sync without user intervention
- Conflict resolution: server data takes precedence

**4. Progressive Web App (PWA)**
- Installable on mobile home screen (no app store needed)
- Works like a native app
- Service worker caches static assets
- Runs on any device with a web browser

### Network Strategy
| Scenario | Behavior |
|----------|----------|
| **Online** | Cloud Run API + Gemini AI → Intelligent triage |
| **Offline** | Local rule-based algorithm → Basic triage |
| **Network restored** | Auto-sync queued data in background |
| **Weak signal** | Timeout after 10s, fallback to local |

### Why This Matters
- **Hill tracts**: Often no mobile signal for days
- **Rural villages**: Intermittent electricity = intermittent internet
- **Healthcare workers**: Can use app in the field without connectivity
- **Reliability**: App works 100% of the time, regardless of network

---

## 🚀 Deployment & Running the Application

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/healthdb
export EMERGENT_LLM_KEY=your_key_here

uvicorn server:app --reload --port 8001
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

### Environment Variables
```
# Backend (.env)
DATABASE_URL=postgresql://healthuser:healthpass@localhost:5432/healthdb


# Frontend (.env)
EXPO_PUBLIC_BACKEND_URL=https://your-domain.com
```

---

## 📊 Limitations & Future Work

### Current Limitations
1. Not a replacement for doctors - triage only
2. Limited symptom library - 22 common symptoms
3. No image/voice analysis
4. Single language pair - Bangla + English only

### Future Improvements
1. **Expand symptom database** - Include more conditions
2. **Add voice input** - For illiterate users
3. **Community health worker mode** - Multi-patient tracking
4. **Integration with telemedicine** - Connect to real doctors
5. **SMS fallback** - For feature phones
6. **Regional dialects** - Support Sylheti, Chittagonian

---

## 📁 Project Structure

```
/app
├── backend/
│   ├── server.py          # FastAPI application
│   ├── requirements.txt   # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── app/               # Expo Router screens
│   │   ├── _layout.tsx    # Tab navigation
│   │   ├── index.tsx      # Home screen
│   │   ├── symptoms.tsx   # Symptom selection
│   │   ├── result.tsx     # Triage result
│   │   ├── history.tsx    # Consultation history
│   │   └── profile.tsx    # User profile
│   ├── src/
│   │   ├── store/         # Zustand state management
│   │   ├── services/      # API & offline triage
│   │   └── constants/     # Translations
│   └── package.json
├── ARCHITECTURE.md        # System design document
└── README.md              # This file
```

---

## 📞 Emergency Contacts (Bangladesh)

- **National Emergency:** 999
- **Ambulance:** 199
- **Health Helpline:** 16263

---

## 📄 License

MIT License - Free to use and modify for healthcare initiatives.

---

*Built with ❤️ for Bangladesh's rural communities*

**স্বাস্থ্য সেবা সবার জন্য | Healthcare for Everyone**
