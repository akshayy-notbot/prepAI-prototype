#!/usr/bin/env python3
"""
Database migration script for PrepAI enhanced schema
Run this to create the new tables and migrate existing data
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import engine, Base, SessionLocal, Interview, Question

def migrate_database():
    """Migrate database to new enhanced schema"""
    
    print("🚀 Starting PrepAI Database Migration")
    print("=" * 50)
    
    try:
        # Create all new tables
        print("📋 Creating new database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully")
        
        # Test database connection
        db = SessionLocal()
        print("🔌 Database connection test successful")
        
        # Check existing data
        existing_interviews = db.query(Interview).count()
        existing_questions = db.query(Question).count()
        
        print(f"📊 Found {existing_interviews} existing interviews")
        print(f"📊 Found {existing_questions} existing questions")
        
        # Create sample data for testing (optional)
        if existing_questions == 0:
            print("🌱 Creating sample questions for testing...")
            create_sample_questions(db)
        
        db.close()
        
        print("\n🎉 Database migration completed successfully!")
        print("\n📋 New tables created:")
        print("   • interview_sessions - Complete interview sessions")
        print("   • user_responses - Individual user responses")
        print("   • analysis_results - Detailed analysis results")
        print("   • skill_performance - Skill-specific performance tracking")
        print("\n🔧 Ready to use enhanced PrepAI system!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

def create_sample_questions(db):
    """Create sample questions for testing"""
    
    sample_questions = [
        {
            "question_text": "How would you design a product to help people learn a new language?",
            "role": "Product Manager",
            "seniority": "Senior",
            "skill_tags": ["Product Design", "User Empathy"]
        },
        {
            "question_text": "Tell me about a time you used data to influence a product decision.",
            "role": "Product Manager",
            "seniority": "Senior",
            "skill_tags": ["Metrics", "Execution"]
        },
        {
            "question_text": "Design a scalable system for handling millions of concurrent users.",
            "role": "Software Engineer",
            "seniority": "Senior",
            "skill_tags": ["System Design", "Scalability"]
        },
        {
            "question_text": "How would you analyze user engagement data to identify drop-off points?",
            "role": "Data Analyst",
            "seniority": "Mid-Level",
            "skill_tags": ["Data Analysis", "User Behavior"]
        }
    ]
    
    for q_data in sample_questions:
        question = Question(**q_data)
        db.add(question)
    
    db.commit()
    print(f"✅ Created {len(sample_questions)} sample questions")

def show_database_structure():
    """Display the current database structure"""
    
    print("\n🏗️  Current Database Structure")
    print("=" * 40)
    
    # Get table information
    inspector = engine.dialect.inspector(engine)
    tables = inspector.get_table_names()
    
    for table_name in tables:
        print(f"\n📋 Table: {table_name}")
        columns = inspector.get_columns(table_name)
        
        for col in columns:
            col_type = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"   • {col['name']}: {col_type} ({nullable})")
            
            # Show JSON field details
            if 'JSON' in col_type or 'JSONB' in col_type:
                print(f"     └─ JSON field for storing structured data")

if __name__ == "__main__":
    print("🔧 PrepAI Database Migration Tool")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('models.py'):
        print("❌ Error: models.py not found. Please run this script from the PrepAI project directory.")
        sys.exit(1)
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Show database structure
        show_database_structure()
        
        print("\n🚀 Next steps:")
        print("   1. Start your backend server: uvicorn main:app --reload")
        print("   2. Test the enhanced system with skill selection")
        print("   3. Check the database for saved interview sessions")
    else:
        print("\n❌ Migration failed. Please check the error messages above.")
        sys.exit(1)
