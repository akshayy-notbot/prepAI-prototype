# In main.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import models

# --- Pydantic Models (for request/response validation) ---
class InterviewCreate(BaseModel):
    role: str
    seniority: str
    skills: List[str]

# --- App Initialization ---
app = FastAPI()
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