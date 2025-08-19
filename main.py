import os
import json
from typing import List, Dict, Any
from datetime import datetime

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
    # WARNING: Storing API keys in code is insecure. This is for local testing only.
    # In production, use environment variables
    GOOGLE_API_KEY = "AIzaSyAx-lbk6L--IuSvKPSrSd6G1JzC-nKvPAg"
    
    if GOOGLE_API_KEY == "paste_your_google_api_key_here":
        raise ValueError("Please update the GOOGLE_API_KEY in main.py with your actual API key")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash')


# --- API Endpoints ---

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