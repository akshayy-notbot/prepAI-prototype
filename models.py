from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, DateTime, Text, Boolean, UUID
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from sqlalchemy import text

# Use the DATABASE_URL from the environment (Render will provide this)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required. Please set it in Render dashboard.")

# Create the declarative base for SQLAlchemy models
Base = declarative_base()

# Simple initialization - create engine when needed
def get_engine():
    """Get database engine"""
    return create_engine(DATABASE_URL)

def get_session_local():
    """Get database session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

# Legacy aliases for backward compatibility
def get_engine_legacy():
    """Legacy function - use get_engine() instead"""
    return get_engine()

def get_session_local_legacy():
    """Legacy function - use get_session_local() instead"""
    return get_session_local()

# --- Enhanced Table Definitions for New Architecture ---

class InterviewSession(Base):
    """
    Stores complete interview sessions with the new topic_graph architecture.
    Note: Real-time state is managed in Redis, not in this table.
    """
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)  # Frontend-generated session ID
    user_id = Column(Integer, index=True, default=1)  # For now, using dummy user ID
    
    # Interview Configuration
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    selected_skills = Column(JSONB, nullable=False)  # Array of selected skills
    
    # New Architecture: Topic Graph (Permanent Blueprint)
    topic_graph = Column(JSONB, nullable=False)  # The machine-readable interview blueprint
    session_narrative = Column(Text)  # The project scenario backdrop
    
    # Session Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    status = Column(String, default='ready')  # ready, in_progress, completed, analyzed
    
    # Final State (Persisted after interview ends, not during real-time)
    final_current_topic_id = Column(String)  # Final topic when interview ended
    final_covered_topic_ids = Column(JSONB)  # Final array of completed topic IDs
    
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

class SessionState(Base):
    """
    Final session state for completed interviews (persisted after completion).
    Real-time state during interviews lives in Redis only.
    """
    __tablename__ = "session_states"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Final State (from Redis when interview ended)
    final_current_topic_id = Column(String, nullable=False)
    final_covered_topic_ids = Column(JSONB, default=list)  # Array of completed topic IDs
    
    # Final Conversation State
    final_conversation_history = Column(JSONB)  # Complete conversation history
    final_topic_progress = Column(JSONB)  # Final progress tracking for each topic
    
    # Performance Tracking (aggregated from Redis)
    total_router_agent_calls = Column(Integer, default=0)
    total_generator_agent_calls = Column(Integer, default=0)
    total_response_time_ms = Column(Integer, default=0)
    
    # Timestamps
    interview_completed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SessionState(session_id={self.session_id}, final_topic={self.final_current_topic_id})>"

class TopicGraph(Base):
    """
    Stores reusable topic graphs for different role/seniority combinations
    """
    __tablename__ = "topic_graphs"

    id = Column(Integer, primary_key=True, index=True)
    graph_id = Column(String, unique=True, index=True)
    
    # Graph Configuration
    role = Column(String, nullable=False)
    seniority = Column(String, nullable=False)
    skills = Column(JSONB, nullable=False)  # Array of skills this graph covers
    
    # Graph Content
    session_narrative = Column(Text, nullable=True)  # Can be null for pure topic-based interviews
    topic_graph = Column(JSONB, nullable=False)  # The structured topic blueprint
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<TopicGraph(id={self.graph_id}, role={self.role}, seniority={self.seniority})>"

class AnalysisOrchestrator(Base):
    """
    Coordinates post-interview analysis across multiple specialist agents
    """
    __tablename__ = "analysis_orchestrators"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    
    # Analysis Coordination
    analysis_status = Column(String, default='pending')  # pending, in_progress, completed, failed
    specialist_agents = Column(JSONB)  # Array of agent configurations and results
    
    # Analysis Results
    overall_analysis = Column(JSONB)  # Aggregated results from all agents
    individual_agent_results = Column(JSONB)  # Results from each specialist agent
    
    # Performance Metrics
    total_analysis_time_ms = Column(Integer)
    agent_execution_times = Column(JSONB)  # Timing for each specialist agent
    
    # Timestamps
    analysis_started_at = Column(DateTime)
    analysis_completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AnalysisOrchestrator(session_id={self.session_id}, status={self.analysis_status})>"

class SpecialistAgent(Base):
    """
    Individual specialist agents for post-interview analysis
    """
    __tablename__ = "specialist_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String, nullable=False)  # technical, communication, problem_solving, strategic
    session_id = Column(String, index=True)
    
    # Agent Configuration
    agent_config = Column(JSONB)  # Agent-specific configuration
    analysis_prompt = Column(Text)  # The prompt used for this agent
    
    # Analysis Results
    analysis_result = Column(JSONB)  # Agent's analysis output
    confidence_score = Column(Integer)  # Agent's confidence in its analysis
    
    # Performance
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    
    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SpecialistAgent(type={self.agent_type}, session_id={self.session_id})>"

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
    
    # New Architecture: Topic Tracking
    topic_id = Column(String)  # Which topic this response addresses
    goal_achieved = Column(Boolean)  # Whether the topic goal was met
    
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
    
    # New Architecture: Topic-Based Analysis
    topic_performance = Column(JSONB)  # Performance breakdown by topic
    skill_gaps = Column(JSONB)  # Identified skill gaps by topic
    
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
    
    # New Architecture: Topic-Based Tracking
    topic_id = Column(String)  # Which topic this skill was assessed in
    goal_achievement = Column(Boolean)  # Whether the topic goal was met
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SkillPerformance(skill={self.skill_name}, score={self.skill_score})>"

# Legacy tables (keeping for backward compatibility during transition)
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
    """Create all database tables with robust error handling"""
    try:
        print("🗄️ Starting database schema migration...")
        
        # Get engine and test connection
        engine = get_engine()
        
        # Test basic connection first
        with engine.connect() as conn:
            # Check PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            
            # Check if we can create tables
            result = conn.execute(text("SELECT current_user, current_database()"))
            user, db_name = result.fetchone()
            print(f"✅ Connected as user '{user}' to database '{db_name}'")
            
            # Check user permissions
            result = conn.execute(text("""
                SELECT has_table_privilege(current_user, 'information_schema.tables', 'SELECT') as can_select,
                       has_schema_privilege(current_user, 'public', 'CREATE') as can_create
            """))
            perms = result.fetchone()
            print(f"✅ User permissions - SELECT: {perms[0]}, CREATE: {perms[1]}")
        
        # Now try to create tables
        print("📋 Creating new database schema...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified successfully")
        
        # Verify tables were created
        with engine.connect() as conn:
            inspector = engine.dialect.inspector(engine)
            existing_tables = inspector.get_table_names()
            
            expected_tables = [
                'interview_sessions', 'session_states', 'topic_graphs',
                'analysis_orchestrators', 'specialist_agents', 'user_responses',
                'analysis_results', 'skill_performance', 'interviews', 'questions'
            ]
            
            missing_tables = [table for table in expected_tables if table not in existing_tables]
            if missing_tables:
                print(f"⚠️ Warning: Some tables missing: {missing_tables}")
            else:
                print("✅ All expected tables verified")
                
    except Exception as e:
        error_msg = str(e).lower()
        
        if "permission denied" in error_msg:
            print("❌ Permission denied. User cannot create tables.")
            print("   Solution: Grant CREATE permission to database user")
        elif "does not exist" in error_msg:
            print("❌ Database or schema does not exist.")
            print("   Solution: Check DATABASE_URL and database existence")
        elif "jsonb" in error_msg:
            print("❌ JSONB field error. PostgreSQL version might be too old.")
            print("   Solution: Ensure PostgreSQL 9.4+ for JSONB support")
        elif "syntax error" in error_msg:
            print("❌ SQL syntax error during table creation.")
            print("   Solution: Check table definitions for syntax issues")
        else:
            print(f"❌ Unexpected error creating tables: {e}")
        
        print(f"\n🔍 Full error details: {e}")
        raise e