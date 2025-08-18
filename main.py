# In main.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import models
from fastapi.middleware.cors import CORSMiddleware
from tasks import analyze_interview_task
from typing import Dict, Any # Also add these

# --- Pydantic Models (for request/response validation) ---
class InterviewCreate(BaseModel):
    role: str
    seniority: str
    skills: List[str]

# --- App Initialization ---
app = FastAPI()
# This is the new CORS middleware
origins = [
    "https://akshayy-notbot.github.io", # Your live site
    "http://127.0.0.1:5500",           # For local testing with VS Code Live Server
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.create_tables()

# --- Dependency for getting a DB session ---
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
@app.post("/api/interviews")
def create_interview(interview_data: InterviewCreate, db: Session = Depends(get_db)):
    # Create a new interview record in the database
    new_interview = models.Interview(
        user_id=1, # Hardcoding user_id=1 for now
        role=interview_data.role,
        seniority=interview_data.seniority,
        skills=interview_data.skills,
        status='in-progress'
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    # --- THIS IS THE NEW LOGIC ---
    # Query the database for questions that match the criteria
    questions_from_db = db.query(models.Question).filter(
        models.Question.role == interview_data.role,
        models.Question.seniority == interview_data.seniority
    ).limit(3).all()
    # --- END OF NEW LOGIC ---

    return {"interview_id": new_interview.id, "questions": questions_from_db}

@app.post("/api/interviews/{interview_id}/complete")
def complete_interview(interview_id: int, transcript_data: Dict[str, Any]):
    transcript = transcript_data.get('transcript')
    
    # Trigger the background task
    analyze_interview_task.delay(interview_id, transcript)
    
    return {"status": "Report generation started."}


@app.get("/api/interviews/{interview_id}/report")
def get_report(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    
    if not interview:
        return {"status": "not_found"}
        
    if interview.status == 'report-ready':
        # In a real app, you would fetch the saved report from the 'reports' table.
        # For now, we'll just return a success status.
        dummy_report = {
            "overall_summary": "This is a placeholder report since we are not saving the real one yet.",
            "scores": [{"criterion": "Placeholder", "score": 5, "justification": "Good job!"}]
        }
        return {"status": "report-ready", "data": dummy_report}
    else:
        # Return the current status (e.g., 'generating-report')
        return {"status": interview.status}

    # Create a new interview record in the database
    new_interview = models.Interview(
        user_id=1, # Hardcoding user_id=1 for now
        role=interview_data.role,
        seniority=interview_data.seniority,
        skills=interview_data.skills,
        status='in-progress'
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    dummy_questions = [
        {"id": 1, "text": "Tell me about a product you love and why."},
        {"id": 2, "text": "How would you improve Google Maps?"},
        {"id": 3, "text": "Design a product for frequent travelers."}
    ]

    return {"interview_id": new_interview.id, "questions": dummy_questions}

# ... add the other endpoints later