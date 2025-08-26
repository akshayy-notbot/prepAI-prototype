import os
import json
import time
import random
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables from .env file if it exists
try:
    print("🔍 Importing dotenv...")
    from dotenv import load_dotenv
    print("✅ dotenv imported successfully")
except Exception as e:
    print(f"❌ Failed to import dotenv: {e}")
    raise

load_dotenv()

try:
    print("🔍 Importing FastAPI components...")
    from fastapi import FastAPI, Depends, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    print("✅ FastAPI components imported successfully")
except Exception as e:
    print(f"❌ Failed to import FastAPI components: {e}")
    raise

try:
    print("🔍 Importing typing...")
    from typing import List, Dict, Any
    print("✅ typing imported successfully")
except Exception as e:
    print(f"❌ Failed to import typing: {e}")
    raise

try:
    print("🔍 Importing models...")
    import models
    print("✅ models imported successfully")
except Exception as e:
    print(f"❌ Failed to import models: {e}")
    raise

try:
    print("🔍 Importing google.generativeai...")
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
except Exception as e:
    print(f"❌ Failed to import google.generativeai: {e}")
    raise

try:
    print("🔍 Importing redis...")
    import redis
    print("✅ redis imported successfully")
except Exception as e:
    print(f"❌ Failed to import redis: {e}")
    raise

# Import our new AI-powered interview components
try:
    print("🔍 Importing agents.InterviewSessionService...")
    # Old import removed - now using autonomous interviewer
    print("✅ agents.InterviewSessionService imported successfully")
except Exception as e:
    print(f"❌ Failed to import agents.InterviewSessionService: {e}")
    raise

# Old agent imports removed - now using autonomous interviewer
print("✅ Using autonomous interviewer system")


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
# Database tables will be created in the startup event, not during import

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
        # Create database tables (moved from import time to startup)
        print("🗄️ Starting database schema migration...")
        try:
            models.create_tables()
            print("✅ Database tables created successfully")
        except Exception as db_error:
            print(f"❌ Database schema migration failed: {db_error}")
            print("⚠️  This might be due to:")
            print("   • User lacks CREATE TABLE permissions")
            print("   • PostgreSQL version doesn't support JSONB")
            print("   • Schema conflicts with existing tables")
            print("   • Database connection issues")
            print("\n🔍 Check Render PostgreSQL service configuration")
            raise db_error
        
        # Import startup script functions
        try:
            print("🔍 Importing startup script...")
            from startup import run_startup_checks
            print("✅ Startup script imported successfully")
        except Exception as startup_import_error:
            print(f"❌ Failed to import startup script: {startup_import_error}")
            print("⚠️  Startup validation will be skipped")
            return
        
        # Run startup checks
        try:
            print("🔍 Running startup validation...")
            success = run_startup_checks()
            if success:
                print("✅ PrepAI Backend is ready to serve requests!")
            else:
                print("❌ PrepAI Backend startup failed - some features may not work")
        except Exception as startup_error:
            print(f"❌ Startup validation failed: {startup_error}")
            print("⚠️  Service will continue but may have issues")
            
    except Exception as e:
        print(f"❌ Critical startup error: {e}")
        print("🚨 Service cannot start properly")
        print("📋 Troubleshooting steps:")
        print("   1. Check Render PostgreSQL service status")
        print("   2. Verify DATABASE_URL in environment variables")
        print("   3. Check database user permissions")
        print("   4. Ensure PostgreSQL version supports JSONB")
        raise e

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
    db = models.get_session_local()()
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
        from models import get_engine
        with get_engine().connect() as conn:
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
    NEW ARCHITECTURE: Starts a new AI-powered interview session with topic_graph.
    Creates an interview plan, generates the first question, and saves everything to Redis.
    """
    try:
        # Step 1: Call the Plan Creator (NEW: Generates topic_graph)
        print(f"🚀 Starting interview for {request.role} at {request.seniority} level")
        print(f"📚 Skills to practice: {', '.join(request.skills)}")
        
        # Generate unique session ID
        session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
        print(f"✅ Generated session ID: {session_id}")
        
        # Step 2: Initialize Session Tracker and Autonomous Interviewer
        try:
            from agents.autonomous_interviewer import AutonomousInterviewer
            from agents.session_tracker import SessionTracker
            
            # Initialize session tracker and autonomous interviewer
            session_tracker = SessionTracker()
            autonomous_interviewer = AutonomousInterviewer()
            
            # Create new session with simplified structure
            session_data = session_tracker.create_session(
                session_id=session_id,
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General"  # Focus on first skill
            )
            
            print(f"✅ Session created successfully with autonomous interviewer")
            
        except Exception as session_error:
            print(f"❌ Failed to create session: {session_error}")
            return {"error": f"Failed to create interview session: {session_error}"}, 500
        
        # Step 2: Redis storage removed - session tracker handles all state management
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
            redis_client = redis.from_url(redis_url)
            
            # Convert plan to JSON string and save to Redis
            plan_json = json.dumps(plan)
            redis_client.set(f"plan:{session_id}", plan_json, ex=3600)  # Expire in 1 hour
            
            # NEW: Save topic_graph separately for fast access
            topic_graph_json = json.dumps(topic_graph)
            redis_client.set(f"topic_graph:{session_id}", topic_graph_json, ex=3600)
            
            # NEW: Save session narrative separately
            redis_client.set(f"narrative:{session_id}", session_narrative, ex=3600)
            
            # NEW: Save case study details separately (if available)
            case_study_details = plan.get("case_study_details")
            if case_study_details:
                case_study_json = json.dumps(case_study_details)
                redis_client.set(f"case_study:{session_id}", case_study_json, ex=3600)
                print(f"✅ Case study details saved to Redis with key: case_study:{session_id}")
            
            # NEW: Save archetype information separately
            archetype_info = {
                "archetype": plan.get("archetype", "CASE_STUDY"),
                "reasoning": plan.get("archetype_reasoning", ""),
            }
            archetype_json = json.dumps(archetype_info)
            redis_client.set(f"archetype:{session_id}", archetype_json, ex=3600)
            print(f"✅ Archetype information saved to Redis with key: archetype:{session_id}")
            
            print(f"✅ Interview plan and topic_graph saved to Redis with key: plan:{session_id}")
            
        except Exception as redis_error:
            print(f"❌ Failed to save plan to Redis: {redis_error}")
            return {"error": f"Failed to save interview plan: {str(redis_error)}"}, 500
        
        # Step 3: Generate the First Question (NEW: Using Autonomous Interviewer)
        print("🎭 Generating first interview question using new Autonomous Interviewer...")
        
        # NEW: Use Autonomous Interviewer for first question
        try:
            from agents.autonomous_interviewer import AutonomousInterviewer
            from agents.session_tracker import SessionTracker
            
            # Initialize session tracker and autonomous interviewer
            session_tracker = SessionTracker()
            autonomous_interviewer = AutonomousInterviewer()
            
            # Create new session with simplified structure
            session_data = session_tracker.create_session(
                session_id=session_id,
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General"  # Focus on first skill
            )
            
            # Get initial question from autonomous interviewer
            first_question_result = autonomous_interviewer.get_initial_question(
                role=request.role,
                seniority=request.seniority,
                skill=request.skills[0] if request.skills else "General",
                session_context=session_tracker.get_session_context(session_id)
            )
            
            if not first_question_result.get("response_text"):
                raise Exception(f"Autonomous Interviewer failed to generate opening statement")
            
            opening_statement = first_question_result["response_text"]
            print(f"✅ Opening statement generated using Autonomous Interviewer: {opening_statement[:100]}...")
            
            # Update session with initial state
            session_tracker.update_interview_state(session_id, first_question_result["interview_state"])
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed: {interviewer_error}")
            return {"error": f"Failed to generate opening statement: {interviewer_error}"}, 500
        
        # Check if opening statement generation failed
        if opening_statement.startswith("Error:"):
            print(f"❌ Failed to generate opening statement: {opening_statement}")
            return {"error": f"Failed to generate opening statement: {opening_statement}"}, 500
        
        print(f"✅ Opening statement generated: {opening_statement[:100]}...")
        
        # Step 4: Create and Save the History
        interview_history = [
            {
                "question": opening_statement,
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
        
        # Step 5: Return the Response (NEW: Simplified Autonomous Structure)
        response_data = {
            "session_id": session_id,
            "opening_statement": opening_statement,
            "status": "started",
            "role": request.role,
            "seniority": request.seniority,
            "skill": request.skills[0] if request.skills else "General",
            "estimated_duration_minutes": 45,  # Default duration
            "message": "Interview started successfully with autonomous interviewer"
        }
        
        print(f"🎯 Interview session {session_id} started successfully!")
        print(f"📊 Total goals: {plan['total_goals']}")
        print(f"⏱️ Estimated duration: {plan['estimated_duration_minutes']} minutes")
        print(f"📋 Topic graph: {len(topic_graph)} topics ready")
        
        return response_data
        
    except ValueError as e:
        # Handle validation errors gracefully
        print(f"❌ Validation error in start_interview: {e}")
        return {"error": f"Interview configuration error: {str(e)}"}, 400
    except FileNotFoundError as e:
        # Handle missing configuration files gracefully
        print(f"❌ Configuration file missing in start_interview: {e}")
        return {"error": f"System configuration error: {str(e)}"}, 500
    except Exception as e:
        # Handle all other unexpected errors gracefully
        print(f"❌ Unexpected error in start_interview: {e}")
        return {"error": f"Unexpected error: {str(e)}"}, 500

@app.get("/api/interview/{session_id}/status")
async def get_interview_status(session_id: str):
    """
    Gets the current status and plan for an interview session.
    Updated to include topic_graph information.
    """
    try:
        print(f"📊 Getting status for interview session {session_id}")
        
        # Retrieve data from Redis
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
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
            
            # NEW: Get topic_graph and session narrative
            topic_graph_json = redis_client.get(f"topic_graph:{session_id}")
            topic_graph = json.loads(topic_graph_json.decode('utf-8') if topic_graph_json else [])
            
            narrative = redis_client.get(f"narrative:{session_id}")
            session_narrative = narrative.decode('utf-8') if narrative else ""
            
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
        
        # NEW: Get current topic information
        current_topic_id = plan.get("current_topic_id", "")
        covered_topic_ids = plan.get("covered_topic_ids", [])
        
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
            "skills_breakdown": plan.get("ai_generated_metadata", {}).get("overall_approach", ""),
            
            # NEW: Topic Graph Information
            "topic_graph": {
                "total_topics": len(topic_graph),
                "current_topic_id": current_topic_id,
                "covered_topic_ids": covered_topic_ids,
                "session_narrative": session_narrative,
                "next_topic": None
            },
            "full_topic_graph": topic_graph,
            
            # NEW: Enhanced Case Study Features
            "dynamic_events": plan.get("dynamic_events", []),
            "interviewer_briefing_doc": plan.get("interviewer_briefing_doc", {})
        }
        
        # Find next topic
        if topic_graph and current_topic_id:
            for topic in topic_graph:
                if (topic["topic_id"] not in covered_topic_ids and 
                    topic["topic_id"] != current_topic_id):
                    status_data["topic_graph"]["next_topic"] = topic
                    break
        
        print(f"✅ Interview status retrieved successfully for session {session_id}")
        print(f"📈 Progress: {completed_goals}/{total_goals} goals completed ({progress_percentage:.1f}%)")
        print(f"📋 Current topic: {current_topic_id}")
        
        return status_data
        
    except Exception as e:
        print(f"❌ Unexpected error in get_interview_status: {e}")
        return {"error": f"Unexpected error: {str(e)}"}, 500

@app.post("/api/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    """
    NEW ARCHITECTURE: Receives an answer from the user and processes it using the new PersonaAgent system.
    This is the core of the new two-loop architecture.
    """
    # Validation
    if not request.session_id or not request.answer:
        raise HTTPException(status_code=400, detail="session_id and answer are required.")
    
    try:
        print(f"🎯 Processing answer for session {request.session_id} using NEW ARCHITECTURE")
        
        # Get Redis connection
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
        redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # A. Fetch the Current State from Redis
        print("📥 Fetching current state from Redis...")
        
        # Get the interview plan
        plan_json = redis_client.get(f"plan:{request.session_id}")
        if not plan_json:
            raise HTTPException(status_code=404, detail="Interview plan not found. Session may have expired.")
        
        plan = json.loads(plan_json.decode('utf-8') if isinstance(plan_json, bytes) else plan_json)
        print(f"✅ Retrieved interview plan with {len(plan.get('goals', []))} goals")
        
        # Get the topic_graph and session_narrative
        topic_graph_json = redis_client.get(f"topic_graph:{request.session_id}")
        if not topic_graph_json:
            raise HTTPException(status_code=404, detail="Topic graph not found. Session may have expired.")
        
        topic_graph = json.loads(topic_graph_json.decode('utf-8') if isinstance(topic_graph_json, bytes) else topic_graph_json)
        print(f"✅ Retrieved topic graph with {len(topic_graph)} topics")
        
        narrative = redis_client.get(f"narrative:{request.session_id}")
        session_narrative = narrative.decode('utf-8') if narrative else ""
        print(f"✅ Retrieved session narrative: {session_narrative[:50]}...")
        
        # Get the conversation history
        history_json = redis_client.get(f"history:{request.session_id}")
        if not history_json:
            raise HTTPException(status_code=404, detail="Conversation history not found. Session may have expired.")
        
        conversation_history = json.loads(history_json.decode('utf-8') if isinstance(history_json, bytes) else history_json)
        print(f"✅ Retrieved conversation history with {len(conversation_history)} turns")
        
        # B. Update the Conversation History
        print("📝 Updating conversation history with user's answer...")
        
        if not conversation_history:
            raise HTTPException(status_code=400, detail="Conversation history is empty")
        
        # Update the last turn's answer
        last_turn = conversation_history[-1]
        last_turn["answer"] = request.answer
        print(f"✅ Updated last turn with user's answer: {request.answer[:50]}...")
        
        # Also add user's answer to session tracker
        try:
            from agents.session_tracker import SessionTracker
            session_tracker = SessionTracker()
            session_tracker.add_conversation_turn(request.session_id, "user", request.answer)
            print(f"✅ Added user's answer to session tracker")
        except Exception as e:
            print(f"⚠️ Warning: Failed to add user's answer to session tracker: {e}")
        
        # C. NEW ARCHITECTURE: Use Autonomous Interviewer for Response Generation
        print("🎭 Using NEW Autonomous Interviewer system for response generation...")
        
        try:
            from agents.autonomous_interviewer import AutonomousInterviewer
            from agents.session_tracker import SessionTracker
            
            # Initialize autonomous interviewer and session tracker
            autonomous_interviewer = AutonomousInterviewer()
            session_tracker = SessionTracker()
            
            # Get current session state
            session_data = session_tracker.get_session(request.session_id)
            if not session_data:
                raise Exception("Session not found or expired")
            
            # Get conversation history in the format expected by autonomous interviewer
            conversation_history = []
            for turn in conversation_history:
                conversation_history.append({
                    "role": "interviewer" if turn.get("question") else "user",
                    "content": turn.get("question", "") or turn.get("answer", "")
                })
            
            # Process the user response using autonomous interviewer
            interviewer_result = autonomous_interviewer.conduct_interview_turn(
                role=session_data["role"],
                seniority=session_data["seniority"],
                skill=session_data["skill"],
                interview_stage=session_data["current_stage"],
                conversation_history=conversation_history,
                session_context=session_tracker.get_session_context(request.session_id)
            )
            
            if not interviewer_result.get("response_text"):
                raise Exception("Autonomous Interviewer failed to generate response")
            
            new_ai_question = interviewer_result["response_text"]
            current_stage = interviewer_result["interview_state"]["current_stage"]
            skill_progress = interviewer_result["interview_state"]["skill_progress"]
            next_focus = interviewer_result["interview_state"]["next_focus"]
            
            print(f"✅ Autonomous Interviewer generated response")
            print(f"📊 Current stage: {current_stage}")
            print(f"🎯 Skill progress: {skill_progress}")
            print(f"🎯 Next focus: {next_focus}")
            
            # Update session state
            session_tracker.update_interview_state(request.session_id, interviewer_result["interview_state"])
            
            # Add the new question to conversation history
            session_tracker.add_conversation_turn(request.session_id, "interviewer", new_ai_question)
            
            # Check if interview should end (based on skill progress or other criteria)
            if skill_progress in ["expert", "advanced"] and len(conversation_history) > 10:
                print("🎉 Interview completed by Autonomous Interviewer!")
                # Mark session as completed
                session_tracker.update_session(request.session_id, {"status": "completed"})
            
        except Exception as interviewer_error:
            print(f"❌ Autonomous Interviewer failed, falling back to legacy method: {interviewer_error}")
            
            # Fallback to legacy evaluation and question generation
            current_goal = None
            for goal in plan.get("goals", []):
                if goal.get("status") == "pending":
                    current_goal = goal
                    break
            
            if not current_goal:
                raise HTTPException(status_code=400, detail="No pending goals found in interview plan")
            
            # Get the last question for context
            last_question = last_turn.get("question", "")
            
            # Evaluate the user's answer
            skills_to_assess = [current_goal.get("skill", "General")]
            evaluation_result = evaluate_answer(
                answer=request.answer,
                question=last_question,
                skills_to_assess=skills_to_assess
            )
            
            if not evaluation_result:
                raise HTTPException(status_code=500, detail="Failed to evaluate answer")
            
            print(f"✅ Legacy evaluation completed with overall score: {evaluation_result.get('overall_score', 'N/A')}")
            
            # Simple goal processing logic
            if current_goal:
                score = evaluation_result.get("scores", {}).get(current_goal["skill"], {}).get("score", 0)
                if score >= 3:  # Consider a score of 3+ a successful probe
                    current_goal["probes_needed"] -= 1
                    print(f"✅ Decremented probes for {current_goal['skill']}: {current_goal['probes_needed'] + 1} -> {current_goal['probes_needed']}")
                    
                    if current_goal["probes_needed"] <= 0:
                        current_goal["status"] = "covered"
                        print(f"🎯 Goal '{current_goal['skill']}' marked as covered")
            
            # Determine the Next Action
            next_goal = next((g for g in plan.get("goals", []) if g.get("status") == "pending"), None)
            
            if not next_goal:
                # All goals are covered, interview is complete
                print("🎉 All interview goals have been covered!")
                new_ai_question = "Thank you, that concludes our interview. We will be in touch regarding the next steps."
                agent_used = "legacy_fallback"
                current_topic_id = "completed"
                covered_topic_ids = [g["skill"] for g in plan.get("goals", [])]
            else:
                skill_name = next_goal.get("skill", "the required skills")
                instruction = f"The current goal is to assess '{skill_name}'. Ask a question related to this skill, considering the conversation history."
                print(f"🎯 Next target: {skill_name}")
                
                # This should not happen with the new architecture
                # If we reach here, it means the new architecture failed
                print(f"❌ New architecture failed, cannot generate question for skill: {skill_name}")
                return {"error": f"Failed to generate question using new architecture. Please restart the interview."}, 500
        
        # D. Save State and Return the New Question
        print("💾 Saving updated state to Redis...")
        
        # Append new turn to history
        new_turn = {
            "question": new_ai_question,
            "answer": None,
            "timestamp": None,  # Will be set by the frontend
            "question_type": "follow_up"
        }
        conversation_history.append(new_turn)
        
        # Update plan with new topic information if using new architecture
        if "current_topic_id" in locals() and current_topic_id:
            # Only update the plan object in memory for Redis storage
            # Do NOT write to PostgreSQL during real-time interview
            plan["current_topic_id"] = current_topic_id
            plan["covered_topic_ids"] = covered_topic_ids
        
        # Save updated plan and history back to Redis (ONLY Redis during interview)
        updated_plan_json = json.dumps(plan)
        updated_history_json = json.dumps(conversation_history)
        
        redis_client.set(f"plan:{request.session_id}", updated_plan_json, ex=3600)
        redis_client.set(f"history:{request.session_id}", updated_history_json, ex=3600)
        
        print("✅ Updated plan and history saved to Redis")
        print("ℹ️ Note: Session state remains in Redis only during interview")
        
        # Return the new question immediately
        result = {
            "success": True,
            "message": "Answer processed successfully",
            "next_question": new_ai_question,
            "session_id": request.session_id,
            "goals_remaining": len([g for g in plan.get("goals", []) if g.get("status") == "pending"]),
            "total_goals": len(plan.get("goals", [])),
            "timestamp": datetime.now().isoformat(),
            
            # NEW: Architecture Information
            "architecture": "unified_persona",
            "agent_used": agent_used,
            "current_topic_id": current_topic_id if "current_topic_id" in locals() else "",
            "covered_topic_ids": covered_topic_ids if "covered_topic_ids" in locals() else [],
            "turn_type": turn_type if "turn_type" in locals() else "MID_INTERVIEW",
            
            # NEW: State Management Information
            "state_storage": "redis_only",  # All real-time state stays in Redis
            "postgresql_write": "none",  # No database writes during interview
            
            # NEW: Enhanced Case Study Features
            "dynamic_events": plan.get("dynamic_events", []),
            "interviewer_briefing_doc": plan.get("interviewer_briefing_doc", {})
        }
        
        # Add PersonaAgent metrics if available
        if "persona_result" in locals():
            result["total_latency_ms"] = persona_result.get("total_latency_ms", 0)
            result["goal_achieved"] = persona_result.get("goal_achieved", False)
        
        print(f"🎉 Answer processing completed successfully for session {request.session_id}")
        print(f"🏗️ Architecture used: {result['architecture']}")
        print(f"🤖 Agent used: {result['agent_used']}")
        print(f"💾 State storage: {result['state_storage']}")
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to process answer: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

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





@app.get("/test-redis")
def test_redis():
    """Test endpoint to verify Redis read/write operations"""
    try:
        # Get Redis URL from environment
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
        
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
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
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
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
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