# স্বাস্থ্য সহায়ক (Health Assistant)

## 🏥 Offline-First Healthcare PWA for Rural Bangladesh

A mobile-first Progressive Web Application designed to help people in Bangladesh's rural and hill tract regions access basic medical guidance despite limited or intermittent internet connectivity.

![Health Assistant Screenshot](./assets/screenshot.png)

---

## 👥 Team Information

- **Team Name:** NSU_Zazabores
- **Members:** Iqbal Bahar Prince, Bhuyian Arshan Rashid Dibbo, Md. Samin Yasir

- **Hackathon:** Future Builders AI Hackathon

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

