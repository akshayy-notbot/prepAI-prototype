from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Connection Setup ---
DATABASE_URL = "postgresql://prepaiuser:prepaipassword@localhost/prepaidb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Table Definitions ---
class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # For now, we can just use a dummy value
    role = Column(String)
    seniority = Column(String)
    skills = Column(JSON) # Storing a list of skills
    status = Column(String, default='pending')

# In models.py, after the Interview class
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    role = Column(String, index=True)
    seniority = Column(String, index=True)
    skill_tags = Column(JSONB) # e.g., ['Product Sense', 'Execution']

# ... you would add other models for User, Question, Report here later

# --- Function to create tables ---
def create_tables():
    Base.metadata.create_all(bind=engine)