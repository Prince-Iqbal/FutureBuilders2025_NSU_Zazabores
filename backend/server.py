from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum
import json

# PostgreSQL imports
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.pool import StaticPool

# Google Generative AI SDK for direct Gemini integration
import google.generativeai as genai

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://healthuser:healthpass@localhost:5432/healthdb')

# Cloud SQL support via Unix socket
if '/cloudsql/' in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,   # Recycle connections after 1 hour
    )
else:
    engine = create_engine(DATABASE_URL)

logger.info(f"Database engine created")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Gemini Configuration via Google AI Studio
GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')
gemini_model = None
if GOOGLE_AI_API_KEY:
    genai.configure(api_key=GOOGLE_AI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Google Gemini client initialized successfully")
else:
    logger.warning("No GOOGLE_AI_API_KEY found, AI features will use fallback")

# ============== DATABASE MODELS ==============

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    location = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    consultations = relationship("ConsultationDB", back_populates="user")

class ConsultationDB(Base):
    __tablename__ = "consultations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    symptoms = Column(JSON, nullable=False)  # List of symptom IDs
    duration = Column(String(50), nullable=True)  # e.g., "1-2 days"
    severity_level = Column(String(20), nullable=False)  # emergency, moderate, mild
    ai_explanation = Column(Text, nullable=True)
    guidance_bangla = Column(Text, nullable=True)
    guidance_english = Column(Text, nullable=True)
    is_offline_result = Column(Boolean, default=False)
    synced = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserDB", back_populates="consultations")

class SyncQueueDB(Base):
    __tablename__ = "sync_queue"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(50), nullable=False)  # create_consultation, update_user, etc.
    payload = Column(JSON, nullable=False)
    status = Column(String(20), default="pending")  # pending, synced, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# ============== PYDANTIC MODELS ==============

class SeverityLevel(str, Enum):
    EMERGENCY = "emergency"
    MODERATE = "moderate"
    MILD = "mild"

class SymptomInput(BaseModel):
    id: str
    name_en: str
    name_bn: str
    duration: Optional[str] = None

class UserCreate(BaseModel):
    age: int
    gender: str
    location: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    age: int
    gender: str
    location: Optional[str] = None
    created_at: datetime

class TriageRequest(BaseModel):
    user_id: str
    symptoms: List[SymptomInput]
    duration: Optional[str] = None

class TriageResponse(BaseModel):
    id: str
    severity_level: str
    ai_explanation: str
    guidance_bangla: str
    guidance_english: str
    is_offline_result: bool
    created_at: datetime

class ConsultationResponse(BaseModel):
    id: str
    symptoms: List[dict]
    duration: Optional[str]
    severity_level: str
    ai_explanation: Optional[str]
    guidance_bangla: Optional[str]
    guidance_english: Optional[str]
    is_offline_result: bool
    created_at: datetime

class SyncItem(BaseModel):
    action: str
    payload: dict

class SyncRequest(BaseModel):
    items: List[SyncItem]

# ============== MASTER SYMPTOM DATA ==============

SYMPTOMS_MASTER = [
    # Head & General
    {"id": "fever", "name_en": "Fever", "name_bn": "জ্বর", "icon": "thermometer", "category": "general", "severity_weight": 2},
    {"id": "headache", "name_en": "Headache", "name_bn": "মাথাব্যথা", "icon": "head-outline", "category": "head", "severity_weight": 1},
    {"id": "dizziness", "name_en": "Dizziness", "name_bn": "মাথা ঘোরা", "icon": "sync", "category": "head", "severity_weight": 2},
    
    # Respiratory
    {"id": "cough", "name_en": "Cough", "name_bn": "কাশি", "icon": "lungs", "category": "respiratory", "severity_weight": 1},
    {"id": "breathing_difficulty", "name_en": "Difficulty Breathing", "name_bn": "শ্বাসকষ্ট", "icon": "air", "category": "respiratory", "severity_weight": 4},
    {"id": "chest_pain", "name_en": "Chest Pain", "name_bn": "বুকে ব্যথা", "icon": "heart-pulse", "category": "chest", "severity_weight": 5},
    {"id": "cold", "name_en": "Cold/Runny Nose", "name_bn": "সর্দি", "icon": "water-outline", "category": "respiratory", "severity_weight": 1},
    
    # Digestive
    {"id": "stomach_pain", "name_en": "Stomach Pain", "name_bn": "পেটে ব্যথা", "icon": "stomach", "category": "digestive", "severity_weight": 2},
    {"id": "vomiting", "name_en": "Vomiting", "name_bn": "বমি", "icon": "water", "category": "digestive", "severity_weight": 2},
    {"id": "diarrhea", "name_en": "Diarrhea", "name_bn": "ডায়রিয়া/পাতলা পায়খানা", "icon": "toilet", "category": "digestive", "severity_weight": 2},
    {"id": "nausea", "name_en": "Nausea", "name_bn": "বমি বমি ভাব", "icon": "emoticon-sick", "category": "digestive", "severity_weight": 1},
    
    # Pain & Body
    {"id": "body_pain", "name_en": "Body Pain", "name_bn": "শরীরে ব্যথা", "icon": "human", "category": "body", "severity_weight": 1},
    {"id": "joint_pain", "name_en": "Joint Pain", "name_bn": "জয়েন্টে ব্যথা", "icon": "bone", "category": "body", "severity_weight": 1},
    {"id": "back_pain", "name_en": "Back Pain", "name_bn": "পিঠে ব্যথা", "icon": "human-handsdown", "category": "body", "severity_weight": 1},
    
    # Skin
    {"id": "rash", "name_en": "Skin Rash", "name_bn": "ত্বকে ফুসকুড়ি", "icon": "hand-wave", "category": "skin", "severity_weight": 2},
    {"id": "itching", "name_en": "Itching", "name_bn": "চুলকানি", "icon": "hand-pointing-up", "category": "skin", "severity_weight": 1},
    
    # Emergency Signs
    {"id": "unconscious", "name_en": "Unconsciousness", "name_bn": "অজ্ঞান", "icon": "sleep", "category": "emergency", "severity_weight": 5},
    {"id": "severe_bleeding", "name_en": "Severe Bleeding", "name_bn": "অতিরিক্ত রক্তক্ষরণ", "icon": "water", "category": "emergency", "severity_weight": 5},
    {"id": "convulsion", "name_en": "Convulsion/Seizure", "name_bn": "খিঁচুনি", "icon": "lightning-bolt", "category": "emergency", "severity_weight": 5},
    
    # Other
    {"id": "fatigue", "name_en": "Fatigue/Weakness", "name_bn": "দুর্বলতা/ক্লান্তি", "icon": "battery-low", "category": "general", "severity_weight": 1},
    {"id": "loss_appetite", "name_en": "Loss of Appetite", "name_bn": "ক্ষুধামন্দা", "icon": "food-off", "category": "general", "severity_weight": 1},
    {"id": "sore_throat", "name_en": "Sore Throat", "name_bn": "গলা ব্যথা", "icon": "account-voice", "category": "respiratory", "severity_weight": 1},
]

# Emergency symptom IDs
EMERGENCY_SYMPTOMS = ["chest_pain", "breathing_difficulty", "unconscious", "severe_bleeding", "convulsion"]

# ============== AI TRIAGE LOGIC ==============

def get_rule_based_triage(symptoms: List[SymptomInput], age: int, gender: str, duration: str) -> dict:
    """Fallback rule-based triage when AI is unavailable"""
    
    symptom_ids = [s.id for s in symptoms]
    symptom_data = {s['id']: s for s in SYMPTOMS_MASTER}
    
    # Check for emergency symptoms
    for sid in symptom_ids:
        if sid in EMERGENCY_SYMPTOMS:
            return {
                "severity_level": "emergency",
                "ai_explanation": f"জরুরি লক্ষণ সনাক্ত হয়েছে: {symptom_data.get(sid, {}).get('name_bn', sid)}। এটি গুরুতর হতে পারে।\n\nEmergency symptom detected: {symptom_data.get(sid, {}).get('name_en', sid)}. This could be serious.",
                "guidance_bangla": "⚠️ জরুরি অবস্থা!\n\n১. অবিলম্বে নিকটতম হাসপাতালে যান\n২. যদি সম্ভব হয় ৯৯৯ এ কল করুন\n৩. রোগীকে একা রাখবেন না\n৪. শান্ত থাকুন এবং রোগীকে আশ্বস্ত করুন\n\n⛔ এটি চিকিৎসা পরামর্শ নয়। ডাক্তারের সাথে যোগাযোগ করুন।",
                "guidance_english": "⚠️ EMERGENCY!\n\n1. Go to the nearest hospital immediately\n2. Call 999 if possible\n3. Do not leave the patient alone\n4. Stay calm and reassure the patient\n\n⛔ This is not medical advice. Please consult a doctor.",
                "is_offline_result": True
            }
    
    # Calculate severity score
    total_weight = sum(symptom_data.get(sid, {}).get('severity_weight', 1) for sid in symptom_ids)
    
    # Age factor
    if age < 5 or age > 60:
        total_weight += 2
    
    # Duration factor
    if duration in ["more_than_week", "more_than_3_days"]:
        total_weight += 2
    
    # Determine severity
    if total_weight >= 8:
        severity = "moderate"
        guidance_bn = "⚡ মাঝারি অবস্থা\n\n১. আজকেই বা আগামীকাল ডাক্তার দেখান\n২. পর্যাপ্ত বিশ্রাম নিন\n৩. প্রচুর পানি পান করুন\n৪. লক্ষণ খারাপ হলে হাসপাতালে যান\n\n⛔ এটি চিকিৎসা পরামর্শ নয়।"
        guidance_en = "⚡ Moderate Condition\n\n1. Visit a doctor today or tomorrow\n2. Get adequate rest\n3. Drink plenty of water\n4. Go to hospital if symptoms worsen\n\n⛔ This is not medical advice."
        explanation = "একাধিক লক্ষণ বা দীর্ঘ সময়কাল সনাক্ত হয়েছে। ডাক্তারের পরামর্শ নেওয়া উচিত।\n\nMultiple symptoms or prolonged duration detected. Medical consultation recommended."
    else:
        severity = "mild"
        guidance_bn = "✅ হালকা অবস্থা\n\n১. ঘরে বিশ্রাম নিন\n২. প্রচুর পানি ও তরল খাবার খান\n৩. প্যারাসিটামল নিতে পারেন (প্রাপ্তবয়স্কদের জন্য)\n৪. ২-৩ দিনে ভালো না হলে ডাক্তার দেখান\n\n⛔ এটি চিকিৎসা পরামর্শ নয়।"
        guidance_en = "✅ Mild Condition\n\n1. Rest at home\n2. Drink plenty of water and fluids\n3. Can take Paracetamol (for adults)\n4. See a doctor if not better in 2-3 days\n\n⛔ This is not medical advice."
        explanation = "হালকা লক্ষণ সনাক্ত হয়েছে। ঘরোয়া যত্নে ভালো হওয়া সম্ভব।\n\nMild symptoms detected. May improve with home care."
    
    return {
        "severity_level": severity,
        "ai_explanation": explanation,
        "guidance_bangla": guidance_bn,
        "guidance_english": guidance_en,
        "is_offline_result": True
    }

async def get_ai_triage(symptoms: List[SymptomInput], age: int, gender: str, duration: str) -> dict:
    """Get AI-powered triage using Gemini via Google AI Studio"""

    if not gemini_model:
        return get_rule_based_triage(symptoms, age, gender, duration)

    symptom_names_en = [s.name_en for s in symptoms]
    symptom_names_bn = [s.name_bn for s in symptoms]

    # Combine system instruction + user prompt (Gemini doesn't use message roles)
    full_prompt = f"""You are a medical triage assistant for rural Bangladesh. Analyze these symptoms and provide guidance.

Patient Info:
- Age: {age} years
- Gender: {gender}
- Duration: {duration or 'Not specified'}
- Symptoms (English): {', '.join(symptom_names_en)}
- Symptoms (Bangla): {', '.join(symptom_names_bn)}

Provide your response in this exact JSON format:
{{
    "severity_level": "emergency" or "moderate" or "mild",
    "ai_explanation": "Brief explanation in both Bangla and English about why this classification was made. Include which symptoms contributed to this decision.",
    "guidance_bangla": "Clear, simple guidance in Bangla using bullet points. Include: 1) What to do immediately 2) Warning signs to watch 3) When to seek hospital care. End with disclaimer: এটি চিকিৎসা পরামর্শ নয়।",
    "guidance_english": "Same guidance in simple English. End with disclaimer: This is not medical advice."
}}

IMPORTANT RULES:
1. For chest pain, breathing difficulty, unconsciousness, severe bleeding, or seizures -> ALWAYS classify as "emergency"
2. For children under 5 or elderly over 60, be more cautious
3. Use very simple language that village people can understand
4. NEVER provide diagnosis or prescribe specific medicines
5. Always recommend hospital for emergency cases

Respond ONLY with valid JSON, no markdown."""

    try:
        generation_config = genai.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1000,
        )

        response = gemini_model.generate_content(
            full_prompt,
            generation_config=generation_config
        )

        result_text = response.text.strip()

        # Clean up response - remove markdown if present
        if result_text.startswith('```'):
            result_text = result_text.split('```')[1]
            if result_text.startswith('json'):
                result_text = result_text[4:]
        result_text = result_text.strip()

        result = json.loads(result_text)
        result["is_offline_result"] = False
        return result

    except Exception as e:
        logger.error(f"AI triage error: {e}")
        return get_rule_based_triage(symptoms, age, gender, duration)

# ============== DATABASE DEPENDENCY ==============

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============== FASTAPI APP ==============

app = FastAPI(
    title="স্বাস্থ্য সহায়ক / Health Assistant",
    description="Offline-first healthcare triage for rural Bangladesh",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

# ============== API ENDPOINTS ==============

@api_router.get("/")
async def root():
    return {
        "message": "স্বাস্থ্য সহায়ক API / Health Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

# Symptoms endpoints
@api_router.get("/symptoms")
async def get_symptoms():
    """Get all available symptoms for selection"""
    return {"symptoms": SYMPTOMS_MASTER}

@api_router.get("/symptoms/category/{category}")
async def get_symptoms_by_category(category: str):
    """Get symptoms filtered by category"""
    filtered = [s for s in SYMPTOMS_MASTER if s['category'] == category]
    return {"symptoms": filtered}

# User endpoints
@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user profile"""
    db_user = UserDB(
        id=str(uuid.uuid4()),
        age=user.age,
        gender=user.gender,
        location=user.location
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse(
        id=db_user.id,
        age=db_user.age,
        gender=db_user.gender,
        location=db_user.location,
        created_at=db_user.created_at
    )

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id,
        age=user.age,
        gender=user.gender,
        location=user.location,
        created_at=user.created_at
    )

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate, db: Session = Depends(get_db)):
    """Update user profile"""
    db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.age = user.age
    db_user.gender = user.gender
    db_user.location = user.location
    db_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_user)
    return UserResponse(
        id=db_user.id,
        age=db_user.age,
        gender=db_user.gender,
        location=db_user.location,
        created_at=db_user.created_at
    )

# Triage endpoints
@api_router.post("/triage", response_model=TriageResponse)
async def perform_triage(request: TriageRequest, db: Session = Depends(get_db)):
    """Perform AI-powered symptom triage"""
    
    # Get user info
    user = db.query(UserDB).filter(UserDB.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get AI triage result
    result = await get_ai_triage(
        symptoms=request.symptoms,
        age=user.age,
        gender=user.gender,
        duration=request.duration or "not_specified"
    )
    
    # Save consultation
    consultation = ConsultationDB(
        id=str(uuid.uuid4()),
        user_id=user.id,
        symptoms=[{"id": s.id, "name_en": s.name_en, "name_bn": s.name_bn} for s in request.symptoms],
        duration=request.duration,
        severity_level=result["severity_level"],
        ai_explanation=result["ai_explanation"],
        guidance_bangla=result["guidance_bangla"],
        guidance_english=result["guidance_english"],
        is_offline_result=result["is_offline_result"],
        synced=True
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    return TriageResponse(
        id=consultation.id,
        severity_level=consultation.severity_level,
        ai_explanation=consultation.ai_explanation,
        guidance_bangla=consultation.guidance_bangla,
        guidance_english=consultation.guidance_english,
        is_offline_result=consultation.is_offline_result,
        created_at=consultation.created_at
    )

# Consultation history
@api_router.get("/consultations/{user_id}", response_model=List[ConsultationResponse])
async def get_user_consultations(user_id: str, db: Session = Depends(get_db)):
    """Get consultation history for a user"""
    consultations = db.query(ConsultationDB).filter(
        ConsultationDB.user_id == user_id
    ).order_by(ConsultationDB.created_at.desc()).all()
    
    return [
        ConsultationResponse(
            id=c.id,
            symptoms=c.symptoms,
            duration=c.duration,
            severity_level=c.severity_level,
            ai_explanation=c.ai_explanation,
            guidance_bangla=c.guidance_bangla,
            guidance_english=c.guidance_english,
            is_offline_result=c.is_offline_result,
            created_at=c.created_at
        )
        for c in consultations
    ]

# Sync endpoints for offline data
@api_router.post("/sync")
async def sync_offline_data(sync_request: SyncRequest, db: Session = Depends(get_db)):
    """Sync offline data to server"""
    results = []
    
    for item in sync_request.items:
        try:
            if item.action == "create_consultation":
                payload = item.payload
                consultation = ConsultationDB(
                    id=payload.get("id", str(uuid.uuid4())),
                    user_id=payload["user_id"],
                    symptoms=payload["symptoms"],
                    duration=payload.get("duration"),
                    severity_level=payload["severity_level"],
                    ai_explanation=payload.get("ai_explanation"),
                    guidance_bangla=payload.get("guidance_bangla"),
                    guidance_english=payload.get("guidance_english"),
                    is_offline_result=True,
                    synced=True,
                    created_at=datetime.fromisoformat(payload.get("created_at", datetime.utcnow().isoformat()))
                )
                db.add(consultation)
                results.append({"action": item.action, "status": "success", "id": consultation.id})
            
            elif item.action == "create_user":
                payload = item.payload
                user = UserDB(
                    id=payload.get("id", str(uuid.uuid4())),
                    age=payload["age"],
                    gender=payload["gender"],
                    location=payload.get("location")
                )
                db.add(user)
                results.append({"action": item.action, "status": "success", "id": user.id})
                
        except Exception as e:
            logger.error(f"Sync error: {e}")
            results.append({"action": item.action, "status": "failed", "error": str(e)})
    
    db.commit()
    return {"synced": len([r for r in results if r["status"] == "success"]), "results": results}

# Offline fallback endpoint
@api_router.post("/triage/offline")
async def offline_triage(request: TriageRequest):
    """Rule-based triage for offline mode - no database required"""
    result = get_rule_based_triage(
        symptoms=request.symptoms,
        age=30,  # Default age if user not found
        gender="unknown",
        duration=request.duration or "not_specified"
    )
    
    return {
        "id": str(uuid.uuid4()),
        "severity_level": result["severity_level"],
        "ai_explanation": result["ai_explanation"],
        "guidance_bangla": result["guidance_bangla"],
        "guidance_english": result["guidance_english"],
        "is_offline_result": True,
        "created_at": datetime.utcnow().isoformat()
    }

# Mount static files for frontend BEFORE API router
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    logger.info(f"Mounting static files from: {static_dir}")
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    app.mount("/_expo", StaticFiles(directory=str(static_dir / "_expo")), name="expo")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend index.html"""
        return FileResponse(str(static_dir / "index.html"))

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve SPA routes"""
        file_path = static_dir / f"{path}.html"
        if file_path.exists():
            return FileResponse(file_path)
        # For other static files
        file_path = static_dir / path
        if file_path.exists():
            return FileResponse(file_path)
        # Fallback to index for SPA routing
        return FileResponse(str(static_dir / "index.html"))
else:
    logger.warning(f"Static directory not found: {static_dir}")

# Include API router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown():
    pass
