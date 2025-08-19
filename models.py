from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Use the DATABASE_URL from the environment, with a local default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://prepaiuser:prepaipassword@localhost/prepaidb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Enhanced Table Definitions ---

class InterviewSession(Base):
    """
    Stores complete interview sessions with metadata, questions, responses, and analysis
    """
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, default=1)  # For now, using dummy user ID
    session_id = Column(String, unique=True, index=True)  # Frontend-generated session ID
    
    # Interview Configuration
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    selected_skills = Column(JSONB, nullable=False)  # Array of selected skills
    
    # Session Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String, default='in-progress')  # in-progress, completed, analyzed
    
    # Generated Questions (stored as JSON)
    generated_questions = Column(JSONB)  # Full question objects from Gemini API
    
    # User Responses (stored as JSON)
    transcript = Column(JSONB)  # Array of Q&A pairs
    
    # Analysis Results (stored as JSON)
    analysis_results = Column(JSONB)  # Full analysis from Gemini API
    
    # Performance Metrics
    total_questions = Column(Integer, default=0)
    total_responses = Column(Integer, default=0)
    analysis_score = Column(Integer)  # Overall score from analysis
    
    def __repr__(self):
        return f"<InterviewSession(id={self.id}, role={self.role}, status={self.status})>"

class UserResponse(Base):
    """
    Individual user responses to questions (alternative to storing in transcript JSON)
    """
    __tablename__ = "user_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    question_index = Column(Integer)  # Position in the question sequence
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_metadata = Column(JSONB)  # Role, skills, difficulty, etc.
    
    # User response
    user_answer = Column(Text, nullable=False)
    response_length = Column(Integer)  # Character count
    response_time = Column(Integer)  # Time taken to respond in seconds
    
    # Timestamps
    question_asked_at = Column(DateTime)
    answered_at = Column(DateTime)
    
    def __repr__(self):
        return f"<UserResponse(session_id={self.session_id}, question_index={self.question_index})>"

class AnalysisResult(Base):
    """
    Detailed analysis results for each interview session
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Analysis metadata
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    analysis_model = Column(String, default='gemini-1.5-flash')
    
    # Analysis content (structured JSON)
    overall_summary = Column(Text)
    overall_score = Column(Integer)
    
    # Detailed scores (stored as JSON)
    criterion_scores = Column(JSONB)  # Array of criterion scores with justifications
    
    # Strengths and improvements (stored as JSON)
    key_strengths = Column(JSONB)  # Array of strengths
    areas_for_improvement = Column(JSONB)  # Array of improvement areas
    recommendations = Column(JSONB)  # Array of recommendations
    
    # Raw analysis data
    raw_analysis = Column(JSONB)  # Complete response from Gemini API
    
    def __repr__(self):
        return f"<AnalysisResult(session_id={self.session_id}, score={self.overall_score})>"

class SkillPerformance(Base):
    """
    Track performance across different skills for analytics
    """
    __tablename__ = "skill_performance"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    skill_name = Column(String, nullable=False)
    
    # Performance metrics
    skill_score = Column(Integer)  # Score for this specific skill
    questions_answered = Column(Integer, default=0)
    improvement_needed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SkillPerformance(skill={self.skill_name}, score={self.skill_score})>"

# Legacy tables (keeping for backward compatibility)
class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    role = Column(String)
    seniority = Column(String)
    skills = Column(JSON)
    status = Column(String, default='pending')

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    role = Column(String, index=True)
    seniority = Column(String, index=True)
    skill_tags = Column(JSONB)

# --- Function to create tables ---
def create_tables():
    Base.metadata.create_all(bind=engine)