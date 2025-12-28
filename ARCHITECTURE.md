# স্বাস্থ্য সহায়ক (Health Assistant) - System Architecture

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

## 1. Problem Statement

### Context
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

## 2. Solution Overview

**স্বাস্থ্য সহায়ক (Health Assistant)** is an offline-first Progressive Web Application (PWA) that provides:

1. **AI-Powered Symptom Triage:** Classifies symptoms into Emergency/Moderate/Mild categories
2. **Bilingual Support:** Full Bangla + English interface
3. **Offline Functionality:** Works without internet using rule-based fallback
4. **Sync Capability:** Queues data for sync when internet is available

### Key Features
- Icon-based symptom selection (accessible for low-literacy users)
- AI explainability (shows why classification was made)
- Clear safety disclaimers
- Consultation history tracking
- User profile management

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT (Expo PWA)                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   UI Layer   │  │ Offline Logic│  │   Sync Service       │   │
│  │  (React)     │  │ (AsyncStorage│  │   (Queue Manager)    │   │
│  │              │  │  + Rules)    │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│         │                 │                    │                │
│         └─────────────────┼────────────────────┘                │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │  API Client │                              │
│                    └──────┬──────┘                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTPS (when available)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVER (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  API Routes  │  │  AI Service  │  │   Database Layer     │   │
│  │  /api/*      │  │  (Gemini)    │  │   (PostgreSQL)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│         │                 │                    │                │
│         └─────────────────┼────────────────────┘                │
│                           │                                     │
│                    ┌──────┴──────┐                              │
│                    │Rule-Based   │                              │
│                    │Fallback     │                              │
│                    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. AI Architecture & Logic

### 4.1 Primary AI: Google Gemini

**Model:** Gemini 2.0 Flash  
**Integration:** Via Emergent LLM Key (unified API key)

**Input Processing:**
```python
Input = {
    "symptoms": ["fever", "cough", "headache"],
    "age": 45,
    "gender": "male",
    "duration": "3_days"
}
```

**Output Classification:**
- 🔴 **Emergency:** Immediate hospital visit required
- 🟡 **Moderate:** See doctor within 24-48 hours
- 🟢 **Mild:** Home care with monitoring

### 4.2 Offline Fallback: Rule-Based System

When AI is unavailable, a deterministic rule-based system takes over:

```python
# Severity Weight System
Symptom Weights:
- Emergency symptoms (chest_pain, breathing_difficulty): 5
- Moderate symptoms (fever, vomiting): 2
- Mild symptoms (cold, headache): 1

# Age Modifiers
- Children < 5 years: +2 weight
- Elderly > 60 years: +2 weight

# Duration Modifiers
- > 3 days: +2 weight

# Classification Thresholds
- Total Weight >= 5 + Emergency Symptom → EMERGENCY
- Total Weight >= 8 → MODERATE
- Total Weight < 8 → MILD
```

### 4.3 Explainability

Every triage result includes:
1. **Why this classification?** - Lists contributing symptoms
2. **Risk factors considered** - Age, duration, combinations
3. **Clear action steps** - What to do next

---

## 5. Offline & Low-Internet Handling

### 5.1 Offline-First Architecture

```
┌─────────────────────────────────────────┐
│           Offline Strategy              │
├─────────────────────────────────────────┤
│                                         │
│  1. LOCAL FIRST                         │
│     - All symptom data cached locally   │
│     - User profile stored in device     │
│     - History saved offline             │
│                                         │
│  2. QUEUE SYSTEM                        │
│     - Pending syncs stored in queue     │
│     - Auto-retry when online            │
│     - Compressed JSON payloads          │
│                                         │
│  3. NETWORK DETECTION                   │
│     - Auto-detect connectivity          │
│     - Switch between AI/Rule modes      │
│     - Clear offline indicators          │
│                                         │
└─────────────────────────────────────────┘
```

### 5.2 Data Storage Strategy

| Data Type | Storage | Sync Strategy |
|-----------|---------|---------------|
| Symptoms Master | AsyncStorage | Pre-loaded, rarely updated |
| User Profile | AsyncStorage | Sync on change |
| Consultations | AsyncStorage + Server | Queue for sync |
| Pending Queue | AsyncStorage | Auto-sync when online |

### 5.3 Network Status Handling

```javascript
// Network states
ONLINE → Use AI API
OFFLINE → Use Rule-Based Fallback
SLOW → Timeout after 10s, fallback to rules
```

---

## 6. Technology Stack

### Frontend
| Technology | Purpose |
|------------|----------|
| React Native (Expo) | Cross-platform mobile app |
| TypeScript | Type safety |
| AsyncStorage | Local data persistence |
| Expo Router | Navigation |
| @expo/vector-icons | Icon system |

### Backend
| Technology | Purpose |
|------------|----------|
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM |
| Google Gemini | AI triage |

### Infrastructure
| Technology | Purpose |
|------------|----------|
| Kubernetes | Container orchestration |
| Emergent LLM Key | Unified AI API key |

---

## 7. API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/symptoms` | GET | Get all symptoms with translations |
| `/api/users` | POST | Create user profile |
| `/api/users/{id}` | GET/PUT | Get/Update user |
| `/api/triage` | POST | AI-powered triage |
| `/api/triage/offline` | POST | Rule-based fallback |
| `/api/consultations/{user_id}` | GET | Get history |
| `/api/sync` | POST | Sync offline data |

---

## 8. AI Tools Disclosure

### AI Technologies Used

1. **Google Gemini 2.0 Flash**
   - Purpose: Symptom classification and guidance generation
   - Integration: Via Emergent LLM unified API
   - Fallback: Rule-based system when unavailable

2. **Development Assistance**
   - Code generation assistance was used in development
   - All AI-generated code was reviewed and tested

### Ethical Considerations
- ⚠️ **Not a diagnostic tool** - Clearly communicated to users
- ⚠️ **No specific prescriptions** - Only general guidance
- ⚠️ **Emergency emphasis** - Always recommends hospital for serious symptoms
- ⚠️ **Disclaimer present** - "This is not medical advice"

---

## 9. Safety & Compliance

### Medical Safety Measures

1. **No Diagnosis Claims**
   - App never diagnoses conditions
   - Only provides triage guidance

2. **Emergency Prioritization**
   - Emergency symptoms ALWAYS trigger red alert
   - Hospital recommendation is prominent

3. **Clear Disclaimers**
   - Shown on every result screen
   - In both Bangla and English

4. **Conservative Classification**
   - When uncertain, defaults to higher severity
   - "Better safe than sorry" approach

### Data Privacy
- No personally identifiable information required
- Local-first storage minimizes data exposure
- No data sold or shared with third parties

---

## 10. Limitations & Future Work

### Current Limitations

1. **Not a replacement for doctors** - Triage only
2. **Limited symptom library** - 22 common symptoms
3. **No image analysis** - Text/selection only
4. **Single language pair** - Bangla + English only

### Future Improvements

1. **Expand symptom database** - Include more conditions
2. **Add voice input** - For illiterate users
3. **Community health worker mode** - Multi-patient tracking
4. **Integration with telemedicine** - Connect to real doctors
5. **SMS fallback** - For feature phones
6. **Regional dialects** - Support Sylheti, Chittagonian

---

## 11. Running the Application

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

### Environment Variables
```
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/healthdb
EMERGENT_LLM_KEY=your_key_here

# Frontend
EXPO_PUBLIC_BACKEND_URL=https://your-domain.com
```

---

## 12. Conclusion

**স্বাস্থ্য সহায়ক** addresses a critical gap in rural Bangladesh's healthcare accessibility. By combining:

- ✅ **Offline-first design** for poor connectivity
- ✅ **AI-powered triage** for intelligent guidance
- ✅ **Bilingual interface** for accessibility
- ✅ **Rule-based fallback** for reliability

We provide a practical, deployable solution that can save lives by helping people make informed decisions about seeking medical care.

---

*Built with ❤️ for Bangladesh's rural communities*
