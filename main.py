import os
import json
from typing import List, Dict, Any

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
import google.generativeai as genai

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Middleware Configuration ---
# This allows your frontend to communicate with your backend
origins = [
    "https://akshayy-notbot.github.io",  # Your live GitHub Pages site
    "http://127.0.0.1:5500",            # For local testing with VS Code Live Server
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup ---
# This line creates the database tables if they don't exist when the app starts
models.create_tables()

# Pydantic model for request body validation
class InterviewCreate(BaseModel):
    role: str
    seniority: str
    skills: List[str]

# Dependency to get a database session for each request
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoints ---

@app.post("/api/interviews")
def create_interview(interview_data: InterviewCreate, db: Session = Depends(get_db)):
    """
    Creates a new interview record in the database and returns a set of questions.
    """
    new_interview = models.Interview(
        user_id=1,  # Hardcoded for now
        role=interview_data.role,
        seniority=interview_data.seniority,
        skills=interview_data.skills,
        status='in-progress'
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    # Query the database for questions that match the role and seniority
    questions_from_db = db.query(models.Question).filter(
        models.Question.role == interview_data.role,
        models.Question.seniority == interview_data.seniority
    ).limit(3).all()

    return {"interview_id": new_interview.id, "questions": questions_from_db}


@app.post("/api/interviews/{interview_id}/complete")
def complete_interview(interview_id: int, transcript_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Receives the interview transcript, runs the AI analysis synchronously,
    and returns the full report.
    """
    transcript = transcript_data.get('transcript')
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        return {"error": "Interview not found"}, 404

    try:
        # --- AI Analysis Logic ---
        # WARNING: Storing API keys in code is insecure. This is for local testing only.
        GOOGLE_API_KEY = "paste_your_google_api_key_here"
        genai.configure(api_key=GOOGLE_API_KEY)
        
        formatted_transcript = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in transcript])

        master_prompt = f"""
        You are an expert hiring manager at a FAANG company, specializing in Product Management. Your task is to analyze an interview transcript and provide a structured, objective evaluation based on a strict rubric. Do not be friendly or conversational; be an analytical evaluator.

        **INTERVIEW CONTEXT:**
        - Role: {interview.role}
        - Seniority: {interview.seniority}
        - Skills Tested: {', '.join(interview.skills)}

        **EVALUATION RUBRIC:**
        For each criterion below, provide a score from 1 (Poor) to 5 (Excellent) and a concise one-sentence justification for that score.
        1.  **Problem Framing:** Did the user clarify the goal and define a specific user segment?
        2.  **Solution Ideation:** Did the user generate multiple, creative ideas?
        3.  **Tradeoff Analysis:** Did the user discuss the pros and cons of their chosen solution?
        4.  **Metrics Definition:** Did the user define clear success metrics?

        **INTERVIEW TRANSCRIPT:**
        ---
        {formatted_transcript}
        ---

        **OUTPUT INSTRUCTIONS:**
        Your response MUST be a single, valid JSON object. Do not include any text before or after the JSON. The JSON object must follow this exact schema:
        {{
          "overall_summary": "A 2-3 sentence summary of the candidate's performance.",
          "scores": [
            {{"criterion": "Problem Framing", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Solution Ideation", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Tradeoff Analysis", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Metrics Definition", "score": <integer>, "justification": "<string>"}}
          ],
          "key_strengths": ["<A bullet point of a key strength>"],
          "areas_for_improvement": ["<A bullet point of a key area for improvement>"]
        }}
        """

        print(f"Calling Gemini API for interview_id: {interview_id}")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(master_prompt)
        json_response_text = response.text.strip().replace('```json', '').replace('```', '')
        report_data = json.loads(json_response_text)
        print("Successfully received report from Gemini.")
        
        # Update interview status
        interview.status = 'report-ready'
        db.commit()

        # Return the full report directly in the response
        return {"status": "report-ready", "data": report_data}

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return {"status": "error", "message": str(e)}, 500