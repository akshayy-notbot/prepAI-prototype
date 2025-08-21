import os
import json
from typing import List, Dict, Any
from datetime import datetime
import time

# Load environment variables from .env file if it exists
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

import models
import google.generativeai as genai
import redis

# Import our new AI-powered interview components
from agents.interview_manager import create_interview_plan
from agents.persona import generate_ai_question

# Import Celery tasks from celery_app
from celery_app import my_test_task, orchestrate_next_turn

# WebSocket connection manager
active_connections: list[WebSocket] = []

# --- FastAPI App Initialization ---
app = FastAPI()

# --- CORS Middleware Configuration ---
# This allows your frontend to communicate with your backend
origins = [
    "https://akshayy-notbot.github.io",  # Your live GitHub Pages site
    "https://prepai-api.onrender.com",   # Your Render backend
    "http://127.0.0.1:5500",            # For local testing with VS Code Live Server
    "http://localhost:8000",
    "http://127.0.0.1:8000",            # Local backend
    "null",                              # For file:// protocol testing
    "*",                                 # Allow all origins for local development
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

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    """Health check endpoint for Render deployment"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PrepAI Backend"
    }

# --- Startup Event Handler ---
@app.on_event("startup")
async def startup_event():
    """Run startup checks when the FastAPI app starts"""
    print("🚀 PrepAI Backend Starting Up...")
    
    try:
        # Import startup script functions
        from startup import run_startup_checks
        
        # Run startup checks
        success = run_startup_checks()
        if success:
            print("✅ PrepAI Backend is ready to serve requests!")
        else:
            print("❌ PrepAI Backend startup failed - some features may not work")
            
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("⚠️  Service will continue but may have issues")

# Pydantic model for request body validation
class InterviewCreate(BaseModel):
    role: str
    seniority: str
    skills: List[str]

class QuestionGenerationRequest(BaseModel):
    role: str
    seniority: str
    skills: List[str]

class StartInterviewRequest(BaseModel):
    role: str
    seniority: str
    skills: List[str]

class SubmitAnswerRequest(BaseModel):
    session_id: str
    answer: str

# Dependency to get a database session for each request
def get_db():
    db = models.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Gemini API Configuration ---
def get_gemini_client():
    """Get configured Gemini client with API key"""
    # Get API key from environment variable (secure)
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    print(f"🔍 Environment check - GOOGLE_API_KEY: {'SET' if GOOGLE_API_KEY else 'NOT SET'}")
    print(f"🔍 Environment check - DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
    
    if not GOOGLE_API_KEY:
        error_msg = "GOOGLE_API_KEY environment variable not set. Please configure it in Render dashboard."
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
        error_msg = "GOOGLE_API_KEY is set to placeholder value. Please set your actual API key in Render dashboard."
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    print(f"✅ Using Gemini API key: {GOOGLE_API_KEY[:10]}...")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test the API key with a simple call
        test_response = model.generate_content("Say 'Hello' if you can read this.")
        print(f"✅ Gemini API test successful: {test_response.text}")
        
        return model
    except Exception as e:
        error_msg = f"Failed to configure Gemini API: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)


# --- API Endpoints ---

@app.get("/")
def root():
    """Root endpoint - redirect to docs"""
    return {"message": "PrepAI API is running", "docs": "/docs"}

@app.get("/health")
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        from models import engine
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        # Check environment variables
        env_status = {
            "GOOGLE_API_KEY": "SET" if os.getenv("GOOGLE_API_KEY") else "NOT SET",
            "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT SET",
            "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "NOT SET")
        }
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment_variables": env_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "environment_variables": {
                "GOOGLE_API_KEY": "SET" if os.getenv("GOOGLE_API_KEY") else "NOT SET",
                "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT SET",
                "PYTHON_VERSION": os.getenv("PYTHON_VERSION", "NOT SET")
            },
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/api/interviews")
def create_interview(interview_data: InterviewCreate, db: Session = Depends(get_db)):
    """
    Creates a new interview record in the database and returns a set of questions.
    This endpoint is kept for backward compatibility but now also creates an InterviewSession.
    """
    # Create legacy interview record
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


@app.post("/api/start-interview")
async def start_interview(request: StartInterviewRequest):
    """
    Starts a new AI-powered interview session.
    Creates an interview plan, generates the first question, and saves everything to Redis.
    """
    try:
        # Step 1: Call the Plan Creator
        print(f"🚀 Starting interview for {request.role} at {request.seniority} level")
        print(f"📚 Skills to practice: {', '.join(request.skills)}")
        
        plan = create_interview_plan(
            role=request.role,
            seniority=request.seniority,
            skills=request.skills
        )
        
        # Check if plan creation failed
        if "error" in plan:
            print(f"❌ Failed to create interview plan: {plan['error']}")
            return {"error": f"Failed to create interview plan: {plan['error']}"}, 500
        
        session_id = plan["session_id"]
        print(f"✅ Interview plan created successfully. Session ID: {session_id}")
        
        # Step 2: Save the Plan to Redis
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_client = redis.from_url(redis_url)
            
            # Convert plan to JSON string and save to Redis
            plan_json = json.dumps(plan)
            redis_client.set(f"plan:{session_id}", plan_json, ex=3600)  # Expire in 1 hour
            print(f"✅ Interview plan saved to Redis with key: plan:{session_id}")
            
        except Exception as redis_error:
            print(f"❌ Failed to save plan to Redis: {redis_error}")
            return {"error": f"Failed to save interview plan: {str(redis_error)}"}, 500
        
        # Step 3: Generate the First Question
        print("🎭 Generating first interview question...")
        
        # Create interviewer persona from the plan
        interviewer_persona = plan.get("persona", f"{request.seniority} {request.role}")
        
        # Generate the opening question
        first_question = generate_ai_question(
            persona=interviewer_persona,
            instructions="Start the interview with a welcoming introduction and ask the first question that will assess the candidate's abilities. Be professional but friendly, and make the candidate feel comfortable while setting clear expectations for the interview.",
            history=[]
        )
        
        # Check if question generation failed
        if first_question.startswith("Error:"):
            print(f"❌ Failed to generate first question: {first_question}")
            return {"error": f"Failed to generate first question: {first_question}"}, 500
        
        print(f"✅ First question generated: {first_question[:100]}...")
        
        # Step 4: Create and Save the History
        interview_history = [
            {
                "question": first_question,
                "answer": None,
                "timestamp": datetime.utcnow().isoformat(),
                "question_type": "opening"
            }
        ]
        
        # Save history to Redis
        try:
            history_json = json.dumps(interview_history)
            redis_client.set(f"history:{session_id}", history_json, ex=3600)  # Expire in 1 hour
            print(f"✅ Interview history saved to Redis with key: history:{session_id}")
            
        except Exception as redis_error:
            print(f"❌ Failed to save history to Redis: {redis_error}")
            return {"error": f"Failed to save interview history: {str(redis_error)}"}, 500
        
        # Step 5: Return the Response
        response_data = {
            "session_id": session_id,
            "first_question": first_question,
            "interviewer_persona": interviewer_persona,
            "total_goals": plan["total_goals"],
            "estimated_duration_minutes": plan["estimated_duration_minutes"],
            "skills_breakdown": plan.get("ai_generated_metadata", {}).get("overall_approach", ""),
            "status": "started"
        }
        
        print(f"🎯 Interview session {session_id} started successfully!")
        print(f"📊 Total goals: {plan['total_goals']}")
        print(f"⏱️ Estimated duration: {plan['estimated_duration_minutes']} minutes")
        
        return response_data
        
    except Exception as e:
        print(f"❌ Unexpected error in start_interview: {e}")
        return {"error": f"Unexpected error: {str(e)}"}, 500


@app.post("/api/interview/{session_id}/next-question")
async def get_next_question(session_id: str, request: Dict[str, Any]):
    """
    Gets the next question for an ongoing interview session.
    Takes the candidate's answer and generates the next appropriate question.
    """
    try:
        candidate_answer = request.get("answer", "")
        if not candidate_answer:
            return {"error": "Candidate answer is required"}, 400
        
        print(f"🔄 Getting next question for session {session_id}")
        print(f"📝 Candidate answer: {candidate_answer[:100]}...")
        
        # Step 1: Retrieve the interview plan and history from Redis
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_client = redis.from_url(redis_url)
            
            # Get the plan
            plan_json = redis_client.get(f"plan:{session_id}")
            if not plan_json:
                return {"error": "Interview plan not found. Session may have expired."}, 404
            
            plan = json.loads(plan_json.decode('utf-8'))
            
            # Get the history
            history_json = redis_client.get(f"history:{session_id}")
            if not history_json:
                return {"error": "Interview history not found. Session may have expired."}, 404
            
            interview_history = json.loads(history_json.decode('utf-8'))
            
        except Exception as redis_error:
            print(f"❌ Failed to retrieve data from Redis: {redis_error}")
            return {"error": f"Failed to retrieve interview data: {str(redis_error)}"}, 500
        
        # Step 2: Update the history with the candidate's answer
        if interview_history and len(interview_history) > 0:
            # Update the last question with the answer
            interview_history[-1]["answer"] = candidate_answer
            interview_history[-1]["answered_at"] = datetime.utcnow().isoformat()
        
        # Step 3: Generate the next question
        interviewer_persona = plan.get("persona", "AI Interviewer")
        
        # Determine what type of question to ask next based on the plan
        next_question_instructions = "Ask the next question that will assess the candidate's abilities. Build upon their previous answer and progress through the interview plan. Be engaging and professional."
        
        next_question = generate_ai_question(
            persona=interviewer_persona,
            instructions=next_question_instructions,
            history=interview_history
        )
        
        if next_question.startswith("Error:"):
            print(f"❌ Failed to generate next question: {next_question}")
            return {"error": f"Failed to generate next question: {next_question}"}, 500
        
        # Step 4: Add the new question to history
        interview_history.append({
            "question": next_question,
            "answer": None,
            "timestamp": datetime.utcnow().isoformat(),
            "question_type": "follow_up"
        })
        
        # Step 5: Save updated history to Redis
        try:
            updated_history_json = json.dumps(interview_history)
            redis_client.set(f"history:{session_id}", updated_history_json, ex=3600)
            print(f"✅ Updated interview history saved to Redis")
            
        except Exception as redis_error:
            print(f"❌ Failed to save updated history to Redis: {redis_error}")
            return {"error": f"Failed to save interview history: {str(redis_error)}"}, 500
        
        # Step 6: Return the next question
        response_data = {
            "session_id": session_id,
            "next_question": next_question,
            "question_number": len(interview_history),
            "total_questions_asked": len(interview_history),
            "status": "question_generated"
        }
        
        print(f"✅ Next question generated successfully for session {session_id}")
        return response_data
        
    except Exception as e:
        print(f"❌ Unexpected error in get_next_question: {e}")
        return {"error": f"Unexpected error: {str(e)}"}, 500


@app.get("/api/interview/{session_id}/status")
async def get_interview_status(session_id: str):
    """
    Gets the current status and plan for an interview session.
    Useful for resuming interviews or checking progress.
    """
    try:
        print(f"📊 Getting status for interview session {session_id}")
        
        # Retrieve data from Redis
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_client = redis.from_url(redis_url)
            
            # Get the plan
            plan_json = redis_client.get(f"plan:{session_id}")
            if not plan_json:
                return {"error": "Interview plan not found. Session may have expired."}, 404
            
            plan = json.loads(plan_json.decode('utf-8'))
            
            # Get the history
            history_json = redis_client.get(f"history:{session_id}")
            if not history_json:
                return {"error": "Interview history not found. Session may have expired."}, 404
            
            interview_history = json.loads(history_json.decode('utf-8'))
            
        except Exception as redis_error:
            print(f"❌ Failed to retrieve data from Redis: {redis_error}")
            return {"error": f"Failed to retrieve interview data: {str(redis_error)}"}, 500
        
        # Calculate progress
        total_goals = plan.get("total_goals", 0)
        completed_goals = plan.get("completed_goals", 0)
        progress_percentage = (completed_goals / total_goals * 100) if total_goals > 0 else 0
        
        # Get current question (last unanswered question)
        current_question = None
        if interview_history and len(interview_history) > 0:
            for qa in reversed(interview_history):
                if qa.get("answer") is None:
                    current_question = qa.get("question")
                    break
        
        # Prepare response
        status_data = {
            "session_id": session_id,
            "role": plan.get("role"),
            "seniority": plan.get("seniority"),
            "interviewer_persona": plan.get("persona"),
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "progress_percentage": round(progress_percentage, 1),
            "estimated_duration_minutes": plan.get("estimated_duration_minutes"),
            "current_question": current_question,
            "questions_asked": len([qa for qa in interview_history if qa.get("question")]),
            "questions_answered": len([qa for qa in interview_history if qa.get("answer") is not None]),
            "status": plan.get("status", "in_progress"),
            "start_time": plan.get("start_time"),
            "skills_breakdown": plan.get("ai_generated_metadata", {}).get("overall_approach", "")
        }
        
        print(f"✅ Interview status retrieved successfully for session {session_id}")
        print(f"📈 Progress: {completed_goals}/{total_goals} goals completed ({progress_percentage:.1f}%)")
        
        return status_data
        
    except Exception as e:
        print(f"❌ Unexpected error in get_interview_status: {e}")
        return {"error": f"Unexpected error: {str(e)}"}, 500


@app.post("/api/submit-answer", status_code=202)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Receives an answer from the user and triggers the background 
    orchestrator task to process it and generate the next question.
    """
    # Explicit validation (from your LLM code)
    if not request.session_id or not request.answer:
        raise HTTPException(status_code=400, detail="session_id and answer are required.")
    
    try:
        # Trigger the background task
        task = orchestrate_next_turn.delay(request.session_id, request.answer)
        
        # Concise response with useful data (hybrid approach)
        return {
            "message": "Answer received and is being processed.",
            "task_id": task.id  # Useful for monitoring
        }
        
    except Exception as e:
        # Focused error handling (from your LLM code)
        raise HTTPException(status_code=500, detail=f"Failed to submit answer: {str(e)}")


@app.post("/api/interviews/{interview_id}/complete")
def complete_interview(interview_id: int, transcript_data: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Receives the interview transcript, runs the AI analysis synchronously,
    saves everything to database, and returns the full report.
    """
    transcript = transcript_data.get('transcript')
    session_id = transcript_data.get('session_id')  # Get session ID from frontend
    
    if not transcript or not isinstance(transcript, list):
        return {"error": "Invalid transcript data"}, 400
    
    try:
        # --- AI Analysis Logic ---
        # Get Gemini client
        model = get_gemini_client()
        
        # Format the transcript for analysis
        formatted_transcript = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in transcript])
        
        # Extract role and skills from the transcript context
        # We'll analyze the questions to determine the role and skills being tested
        role_context = "Product Manager"  # Default fallback
        skills_context = "Product Sense, Metrics, Problem Solving, Strategic Thinking"  # Default fallback
        
        # Try to extract role and skills from the first question if available
        if transcript and len(transcript) > 0:
            first_question = transcript[0].get('question', '')
            if 'Product Manager' in first_question:
                role_context = "Product Manager"
                skills_context = "Product Sense, User Research, Strategic Thinking, Execution, Metrics & KPIs"
            elif 'Software Engineer' in first_question or 'coding' in first_question.lower() or 'system' in first_question.lower():
                role_context = "Software Engineer"
                skills_context = "System Design, Algorithms, Code Quality, Testing, Performance, Security"
            elif 'Data Analyst' in first_question or 'data' in first_question.lower() or 'analytics' in first_question.lower():
                role_context = "Data Analyst"
                skills_context = "Data Analysis, Statistical Analysis, Data Visualization, Business Intelligence, A/B Testing"
        
        # Create a comprehensive analysis prompt tailored to the role
        master_prompt = f"""
        You are an expert hiring manager at a top tech company (FAANG level), specializing in {role_context} interviews. Your task is to analyze an interview transcript and provide a structured, objective evaluation based on a comprehensive rubric.

        **INTERVIEW CONTEXT:**
        - Role: {role_context}
        - Skills Being Tested: {skills_context}
        - Interview Format: Text-based Q&A session

        **EVALUATION RUBRIC:**
        For each criterion below, provide a score from 1 (Poor) to 5 (Excellent) and a concise one-sentence justification for that score.

        {get_role_specific_rubric(role_context)}

        **INTERVIEW TRANSCRIPT:**
        ---
        {formatted_transcript}
        ---

        **ANALYSIS INSTRUCTIONS:**
        Analyze the candidate's responses thoroughly. Consider:
        - Clarity and structure of their thinking
        - Depth of their analysis
        - Practicality of their solutions
        - Communication quality
        - Strategic mindset
        - Role-specific competencies

        **OUTPUT FORMAT:**
        Your response MUST be a single, valid JSON object. Do not include any text before or after the JSON. The JSON object must follow this exact schema:
        {{
          "overall_summary": "A 3-4 sentence comprehensive summary of the candidate's performance, highlighting their strengths and areas for improvement.",
          "overall_score": <integer between 1-5>,
          "scores": [
            {{"criterion": "<criterion name>", "score": <integer 1-5>, "justification": "<specific, actionable feedback>"}},
            {{"criterion": "<criterion name>", "score": <integer 1-5>, "justification": "<specific, actionable feedback>"}},
            {{"criterion": "<criterion name>", "score": <integer 1-5>, "justification": "<specific, actionable feedback>"}},
            {{"criterion": "<criterion name>", "score": <integer 1-5>, "justification": "<specific, actionable feedback>"}}
          ],
          "key_strengths": [
            "<specific strength with example from their response>",
            "<another specific strength>"
          ],
          "areas_for_improvement": [
            "<specific area with actionable suggestion>",
            "<another specific area with actionable suggestion>"
          ],
          "recommendations": [
            "<specific, actionable recommendation for improvement>",
            "<another specific recommendation>"
          ]
        }}

        **IMPORTANT:** 
        - Be specific and reference their actual responses
        - Provide actionable feedback, not generic statements
        - Score fairly but honestly based on their performance
        - Focus on {role_context} competencies
        """

        print(f"Calling Gemini API for analysis of interview_id: {interview_id}")
        print(f"Transcript length: {len(transcript)} Q&A pairs")
        print(f"Role context: {role_context}")
        print(f"Skills context: {skills_context}")
        
        response = model.generate_content(master_prompt)
        json_response_text = response.text.strip()
        
        # Clean up the response (remove markdown formatting if present)
        if json_response_text.startswith('```json'):
            json_response_text = json_response_text[7:]
        if json_response_text.endswith('```'):
            json_response_text = json_response_text[:-3]
        
        # Parse the JSON response
        report_data = json.loads(json_response_text.strip())
        print("Successfully received analysis report from Gemini.")
        print(f"Report structure: {list(report_data.keys())}")
        
        # --- Save to Database ---
        if session_id:
            # Update the existing interview session
            session = db.query(models.InterviewSession).filter(
                models.InterviewSession.session_id == session_id
            ).first()
            
            if session:
                # Update session with transcript and analysis
                session.transcript = transcript
                session.analysis_results = report_data
                session.completed_at = datetime.utcnow()
                session.status = 'analyzed'
                session.total_responses = len(transcript)
                session.analysis_score = report_data.get('overall_score', 0)
                
                # Create detailed analysis result record
                analysis_result = models.AnalysisResult(
                    session_id=session_id,
                    overall_summary=report_data.get('overall_summary'),
                    overall_score=report_data.get('overall_score'),
                    criterion_scores=report_data.get('scores'),
                    key_strengths=report_data.get('key_strengths'),
                    areas_for_improvement=report_data.get('areas_for_improvement'),
                    recommendations=report_data.get('recommendations'),
                    raw_analysis=report_data
                )
                
                db.add(analysis_result)
                
                # Create skill performance records
                if report_data.get('scores'):
                    for score_item in report_data['scores']:
                        skill_perf = models.SkillPerformance(
                            session_id=session_id,
                            skill_name=score_item.get('criterion', 'Unknown'),
                            skill_score=score_item.get('score', 0),
                            questions_answered=len(transcript),
                            improvement_needed=score_item.get('score', 0) < 3
                        )
                        db.add(skill_perf)
                
                db.commit()
                print(f"Updated session {session_id} with analysis results")
            else:
                print(f"Warning: Session {session_id} not found in database")
        
        # Return the complete, structured report
        return {"status": "analysis-complete", "data": report_data}

    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {json_response_text}")
        return {"status": "error", "message": "Failed to parse AI analysis response"}, 500
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return {"status": "error", "message": str(e)}, 500

def get_role_specific_rubric(role: str) -> str:
    """Returns role-specific evaluation criteria"""
    rubrics = {
        "Product Manager": """
        1. **Problem Framing & Analysis (25%):** 
           - Did the candidate clearly understand and break down the problem?
           - Did they identify key stakeholders and constraints?
           - Did they ask clarifying questions?

        2. **Solution Ideation & Creativity (25%):**
           - Did the candidate generate multiple, diverse solution approaches?
           - Were their ideas innovative and practical?
           - Did they consider different user segments and use cases?

        3. **Strategic Thinking & Prioritization (25%):**
           - Did the candidate discuss trade-offs between different approaches?
           - Did they prioritize solutions based on impact and feasibility?
           - Did they consider business implications and ROI?

        4. **Metrics & Success Definition (25%):**
           - Did the candidate define clear, measurable success criteria?
           - Did they identify both leading and lagging indicators?
           - Did they explain how they would measure and iterate?
        """,
        
        "Software Engineer": """
        1. **Technical Problem Solving (25%):**
           - Did the candidate break down complex technical problems?
           - Did they consider edge cases and constraints?
           - Did they ask clarifying technical questions?

        2. **System Design & Architecture (25%):**
           - Did the candidate design scalable and maintainable systems?
           - Did they consider performance, security, and reliability?
           - Did they discuss trade-offs between different approaches?

        3. **Code Quality & Best Practices (25%):**
           - Did the candidate write clean, readable, and efficient code?
           - Did they consider testing, error handling, and documentation?
           - Did they follow software engineering best practices?

        4. **Technical Communication (25%):**
           - Did the candidate explain technical concepts clearly?
           - Did they justify their design decisions?
           - Did they communicate trade-offs effectively?
        """,
        
        "Data Analyst": """
        1. **Data Understanding & Problem Framing (25%):**
           - Did the candidate understand the business problem and data context?
           - Did they identify relevant data sources and limitations?
           - Did they ask clarifying questions about requirements?

        2. **Analytical Approach & Methodology (25%):**
           - Did the candidate choose appropriate analytical methods?
           - Did they consider statistical validity and sample sizes?
           - Did they plan their analysis systematically?

        3. **Data Analysis & Interpretation (25%):**
           - Did the candidate perform thorough and accurate analysis?
           - Did they identify patterns, trends, and insights?
           - Did they interpret results in business context?

        4. **Communication & Storytelling (25%):**
           - Did the candidate present findings clearly and compellingly?
           - Did they create actionable insights and recommendations?
           - Did they communicate technical concepts to non-technical stakeholders?
        """
    }
    
    return rubrics.get(role, rubrics["Product Manager"])  # Default to PM rubric

@app.post("/api/generate-questions")
def generate_questions(request: QuestionGenerationRequest, db: Session = Depends(get_db)):
    """
    Generates interview questions using Gemini API and saves the session to database.
    """
    try:
        # Get Gemini client
        model = get_gemini_client()
        
        # Create a more targeted prompt based on selected skills
        question_prompt = f"""
        You are an expert interviewer at a top tech company. Generate 3 high-quality interview questions for a {request.role} position at {request.seniority} level.
        
        **FOCUS ON THESE SPECIFIC SKILLS:** {', '.join(request.skills)}
        
        **ROLE-SPECIFIC REQUIREMENTS:**
        - Role: {request.role}
        - Seniority: {request.seniority}
        - Questions should be realistic and commonly asked in real interviews
        - Difficulty should match the {request.seniority} level
        - Each question should test at least one of the specified skills
        - Questions should be open-ended and require detailed responses
        - Make questions specific to {request.role} role and the selected skills
        
        **SKILL-FOCUSED QUESTION GUIDELINES:**
        {get_skill_focused_guidelines(request.role, request.skills)}
        
        **OUTPUT FORMAT:**
        Return ONLY a valid JSON array with exactly 3 questions. Each question should have this structure:
        [
            {{
                "question_text": "The actual question text here",
                "role": "{request.role}",
                "seniority": "{request.seniority}",
                "skill_tags": ["Skill1", "Skill2"],
                "difficulty": "Junior/Mid/Senior",
                "expected_answer_elements": ["Key point 1", "Key point 2", "Key point 3"]
            }},
            // ... 2 more questions
        ]
        
        **IMPORTANT:** 
        - Each question should directly test the skills: {', '.join(request.skills)}
        - Questions should be challenging but appropriate for {request.seniority} level
        - Include real-world scenarios and business context
        - Do not include any text before or after the JSON array
        """
        
        print(f"Generating questions for {request.role} {request.seniority} with skills: {request.skills}")
        
        # Generate questions using Gemini
        response = model.generate_content(question_prompt)
        response_text = response.text.strip()
        
        # Clean up the response (remove markdown formatting if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        # Parse the JSON response
        questions_data = json.loads(response_text.strip())
        
        print(f"Successfully generated {len(questions_data)} questions")
        for i, q in enumerate(questions_data):
            print(f"  Q{i+1}: {q.get('question_text', '')[:80]}...")
        
        # Create a new interview session in the database
        session_id = f"session_{int(datetime.now().timestamp())}"
        new_session = models.InterviewSession(
            session_id=session_id,
            role=request.role,
            seniority=request.seniority,
            selected_skills=request.skills,
            generated_questions=questions_data,
            total_questions=len(questions_data),
            started_at=datetime.utcnow(),
            status='in-progress'
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        print(f"Created interview session: {session_id}")
        
        # Return questions with session ID for tracking
        return {
            "questions": questions_data,
            "session_id": session_id,
            "session_db_id": new_session.id
        }
        
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {"error": f"Failed to generate questions: {str(e)}"}, 500

def get_skill_focused_guidelines(role: str, skills: List[str]) -> str:
    """Returns guidelines for creating skill-focused questions"""
    
    skill_guidelines = {
        "Product Manager": {
            "Product Sense": "Focus on product strategy, user needs, market analysis, and feature prioritization",
            "User Research": "Include user interviews, surveys, personas, and user journey mapping",
            "Data Analysis": "Emphasize metrics, KPIs, A/B testing, and data-driven decision making",
            "Strategic Thinking": "Cover business strategy, competitive analysis, and long-term planning",
            "Execution": "Focus on project management, stakeholder alignment, and delivery",
            "Stakeholder Management": "Include cross-functional collaboration and communication",
            "Metrics & KPIs": "Emphasize measurement frameworks and success metrics",
            "User Experience Design": "Cover UX principles, usability, and design thinking"
        },
        "Software Engineer": {
            "System Design": "Focus on scalable architecture, distributed systems, and system trade-offs",
            "Algorithms & Data Structures": "Include problem-solving, optimization, and algorithmic thinking",
            "Code Quality": "Emphasize clean code, best practices, and maintainability",
            "Testing & Debugging": "Cover testing strategies, debugging techniques, and quality assurance",
            "Performance Optimization": "Include profiling, optimization techniques, and performance metrics",
            "Security": "Focus on security best practices, vulnerabilities, and secure coding",
            "API Design": "Cover RESTful APIs, API design principles, and integration",
            "Database Design": "Include database modeling, optimization, and data integrity"
        },
        "Data Analyst": {
            "Data Visualization": "Focus on creating compelling charts, dashboards, and data stories",
            "Statistical Analysis": "Include hypothesis testing, regression analysis, and statistical significance",
            "SQL & Data Querying": "Emphasize data extraction, transformation, and complex queries",
            "Business Intelligence": "Cover reporting, analytics, and business insights",
            "A/B Testing": "Include experimental design, statistical analysis, and interpretation",
            "Data Storytelling": "Focus on communicating insights and recommendations effectively",
            "Machine Learning Basics": "Cover predictive modeling, classification, and model evaluation",
            "Data Quality & Governance": "Include data validation, cleaning, and governance practices"
        }
    }
    
    role_guidelines = skill_guidelines.get(role, {})
    guidelines = []
    
    for skill in skills:
        if skill in role_guidelines:
            guidelines.append(f"• {skill}: {role_guidelines[skill]}")
        else:
            guidelines.append(f"• {skill}: Focus on practical application and real-world scenarios")
    
    return "\n".join(guidelines)

@app.get("/test-celery")
def test_celery_task():
    """Test endpoint to demonstrate Celery task execution"""
    # This calls the task to be executed by the Celery worker in the background
    task_result = my_test_task.delay(10, 20)
    return {
        "message": "Test task has been sent to the Celery worker!",
        "task_id": task_result.id,
        "status": "Task queued successfully"
    }

@app.get("/test-websocket")
async def test_websocket_endpoint():
    """Test endpoint to verify WebSocket configuration"""
    return {
        "status": "websocket_ready",
        "message": "WebSocket endpoint is configured and ready",
        "endpoint": "/ws/{session_id}",
        "cors_origins": origins,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/websocket-info")
async def websocket_info():
    """Get WebSocket connection information"""
    return {
        "active_connections": len(active_connections),
        "websocket_endpoint": "/ws/{session_id}",
        "cors_enabled": True,
        "allow_origins": origins,
        "timestamp": datetime.now().isoformat()
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication with interview sessions"""
    try:
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Add to active connections
        active_connections.append(websocket)
        print(f"✅ WebSocket: Session {session_id} connected successfully")
        
        # Send a welcome message
        await websocket.send_text(json.dumps({
            "type": "connection_status",
            "message": "WebSocket connection established",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Set up Redis pub/sub for this session
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        print(f"🔌 WebSocket: Attempting Redis connection to {redis_url}")
        
        try:
            redis_client = redis.from_url(redis_url)
            # Test Redis connection
            redis_client.ping()
            print(f"✅ WebSocket: Redis connection successful")
            
            pubsub = redis_client.pubsub()
            
            # Subscribe to the session-specific channel
            channel_name = f"channel:{session_id}"
            pubsub.subscribe(channel_name)
            print(f"🔌 WebSocket: Subscribed to Redis channel {channel_name}")
            
            # Test subscription by checking if we're actually subscribed
            channels = pubsub.channels
            if channel_name.encode() in channels:
                print(f"✅ WebSocket: Redis subscription confirmed for channel {channel_name}")
            else:
                print(f"❌ WebSocket: Redis subscription failed for channel {channel_name}")
                print(f"   Available channels: {channels}")
                raise Exception("Redis subscription failed")
                
        except Exception as e:
            print(f"❌ WebSocket: Redis connection/subscription error: {e}")
            # Send error to client
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Redis connection failed: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }))
            raise e
        
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": f"Listening for AI responses on channel {channel_name}",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        # Keep connection alive and handle messages from both client and Redis
        last_redis_check = time.time()
        while True:
            try:
                # Periodic Redis health check (every 10 seconds)
                current_time = time.time()
                if current_time - last_redis_check > 10:
                    try:
                        redis_client.ping()
                        print(f"✅ WebSocket: Redis health check passed for session {session_id}")
                        last_redis_check = current_time
                    except Exception as health_error:
                        print(f"❌ WebSocket: Redis health check failed for session {session_id}: {health_error}")
                        # Try to reconnect
                        try:
                            redis_client = redis.from_url(redis_url)
                            redis_client.ping()
                            pubsub = redis_client.pubsub()
                            pubsub.subscribe(channel_name)
                            print(f"✅ WebSocket: Redis reconnection successful for session {session_id}")
                            last_redis_check = current_time
                        except Exception as reconnect_error:
                            print(f"❌ WebSocket: Redis reconnection failed for session {session_id}: {reconnect_error}")
                            break
                
                # Check for Redis messages (non-blocking)
                try:
                    redis_message = pubsub.get_message(timeout=0.1)
                    if redis_message and redis_message['type'] == 'message':
                        # This is a message from the Celery task (AI response)
                        ai_question = redis_message['data'].decode('utf-8')
                        print(f"🤖 WebSocket: AI question received from Redis for session {session_id}: {ai_question[:100]}...")
                        
                        # Send the AI question to the client
                        await websocket.send_text(json.dumps({
                            "type": "question",
                            "content": ai_question,
                            "session_id": session_id,
                            "timestamp": datetime.now().isoformat()
                        }))
                        continue
                    elif redis_message and redis_message['type'] == 'subscribe':
                        print(f"🔌 WebSocket: Redis subscription message: {redis_message}")
                    elif redis_message:
                        print(f"🔌 WebSocket: Other Redis message: {redis_message}")
                        
                except Exception as redis_error:
                    print(f"❌ WebSocket: Redis message handling error: {redis_error}")
                    # Continue trying to handle client messages
                
                # Check for client messages (non-blocking)
                try:
                    data = await websocket.receive_text()
                    print(f"📨 WebSocket: Message from session {session_id}: {data}")
                    
                    # Echo back the message (for testing)
                    response = {
                        "type": "message_received",
                        "message": f"Message received: {data}",
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(response))
                    
                except Exception as e:
                    # No message from client, continue checking Redis
                    if "timeout" not in str(e).lower():
                        print(f"❌ WebSocket: Error handling message from session {session_id}: {e}")
                        break
                    continue
                
            except Exception as e:
                print(f"❌ WebSocket: Error in main loop for session {session_id}: {e}")
                break
                
    except Exception as e:
        print(f"❌ WebSocket: Connection error for session {session_id}: {e}")
        # Try to send error message if possible
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Connection error: {str(e)}",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }))
        except:
            pass  # Ignore if we can't send error message
        
    finally:
        # Clean up connection and Redis subscription
        try:
            if 'pubsub' in locals():
                pubsub.unsubscribe(channel_name)
                pubsub.close()
                print(f"🔌 WebSocket: Redis subscription closed for session {session_id}")
        except Exception as e:
            print(f"⚠️ WebSocket: Error closing Redis subscription for session {session_id}: {e}")
            
        if websocket in active_connections:
            active_connections.remove(websocket)
        print(f"🔌 WebSocket: Session {session_id} disconnected")

@app.get("/test-redis")
def test_redis():
    """Test endpoint to verify Redis read/write operations"""
    try:
        # Get Redis URL from environment or use default
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        
        # Create Redis client
        r = redis.from_url(redis_url)
        
        # Test write operation
        test_key = "test_key"
        test_value = f"test_value_{datetime.now().isoformat()}"
        r.set(test_key, test_value)
        print(f"✅ Successfully wrote to Redis: {test_key} = {test_value}")
        
        # Test read operation
        retrieved_value = r.get(test_key)
        if retrieved_value:
            retrieved_value = retrieved_value.decode('utf-8')
            print(f"✅ Successfully read from Redis: {test_key} = {retrieved_value}")
        else:
            print("❌ Failed to read from Redis")
            return {"status": "error", "message": "Failed to read from Redis"}
        
        # Test delete operation
        r.delete(test_key)
        print(f"✅ Successfully deleted from Redis: {test_key}")
        
        # Verify deletion
        deleted_value = r.get(test_key)
        if deleted_value is None:
            print("✅ Successfully verified deletion")
        else:
            print("❌ Failed to verify deletion")
            return {"status": "error", "message": "Failed to verify deletion"}
        
        # Test connection with ping
        ping_response = r.ping()
        if ping_response:
            print("✅ Redis ping successful")
        else:
            print("❌ Redis ping failed")
            return {"status": "error", "message": "Redis ping failed"}
        
        return {
            "status": "success",
            "message": "Redis read/write operations successful",
            "redis_url": redis_url,
            "operations": {
                "write": "success",
                "read": "success", 
                "delete": "success",
                "ping": "success"
            },
            "test_data": {
                "key": test_key,
                "written_value": test_value,
                "retrieved_value": retrieved_value
            }
        }
        
    except redis.ConnectionError as e:
        print(f"❌ Redis connection error: {e}")
        return {"status": "error", "message": f"Redis connection failed: {str(e)}"}
    except Exception as e:
        print(f"❌ Redis test error: {e}")
        return {"status": "error", "message": f"Redis test failed: {str(e)}"}

@app.get("/api/task-status/{task_id}")
def get_task_status(task_id: str):
    """Get the status of a Celery task"""
    try:
        # Get Redis URL from environment
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        # Check for task metadata
        task_key = f"celery-task-meta-{task_id}"
        task_data = r.get(task_key)
        
        if task_data:
            task_info = json.loads(task_data)
            return {
                "task_id": task_id,
                "status": task_info.get("status", "unknown"),
                "result": task_info.get("result", None),
                "traceback": task_info.get("traceback", None),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "task_id": task_id,
                "status": "not_found",
                "message": "Task metadata not found in Redis",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "message": f"Error checking task status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/celery-status")
def get_celery_status():
    """Get general Celery and Redis status"""
    try:
        # Get Redis URL from environment
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        # Check Redis connection
        r.ping()
        redis_status = "connected"
        
        # Check for active tasks
        task_keys = r.keys("celery-task-meta-*")
        active_tasks = len(task_keys)
        
        # Check for pending tasks
        pending_keys = r.keys("celery:*")
        pending_tasks = len(pending_keys)
        
        return {
            "status": "healthy",
            "redis": {
                "status": redis_status,
                "url": redis_url
            },
            "celery": {
                "active_tasks": active_tasks,
                "pending_tasks": pending_tasks,
                "total_tasks": active_tasks + pending_tasks
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Status check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }