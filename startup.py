#!/usr/bin/env python3
"""
Startup script for Render deployment
This runs automatically when the service starts and ensures the database is properly configured
"""

import os
import sys
import time
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def run_startup_checks():
    """Run all necessary startup checks and migrations"""
    
    print("🚀 PrepAI Startup Script - Render Deployment")
    print("=" * 50)
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    required_vars = ['DATABASE_URL', 'GOOGLE_API_KEY']
    
    for var in required_vars:
        if not os.getenv(var):
            print(f"❌ Warning: {var} not set")
        else:
            print(f"✅ {var} is configured")
    
    # Wait for database to be ready (important for Render)
    print("\n⏳ Waiting for database connection...")
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from models import engine, Base
            # Test connection using SQLAlchemy 2.0+ syntax
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()  # Consume the result
            print("✅ Database connection successful")
            break
        except Exception as e:
            retry_count += 1
            print(f"⏳ Database not ready (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                print("❌ Failed to connect to database after maximum retries")
                return False
    
    # Create database schema
    print("\n📋 Creating database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database schema created/updated successfully")
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False
    
    # Verify tables exist
    print("\n🔍 Verifying database tables...")
    try:
        from models import SessionLocal, InterviewSession, AnalysisResult, UserResponse, SkillPerformance
        
        db = SessionLocal()
        
        # Check if tables exist by trying to query them
        tables_to_check = [
            ('interview_sessions', InterviewSession),
            ('analysis_results', AnalysisResult),
            ('user_responses', UserResponse),
            ('skill_performance', SkillPerformance)
        ]
        
        for table_name, model in tables_to_check:
            try:
                count = db.query(model).count()
                print(f"✅ {table_name}: {count} records")
            except Exception as e:
                print(f"❌ {table_name}: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False
    
    print("\n🎉 Startup script completed successfully!")
    return True

if __name__ == "__main__":
    success = run_startup_checks()
    if not success:
        print("\n❌ Startup failed - service may not work properly")
        sys.exit(1)
    else:
        print("\n✅ PrepAI is ready to serve requests!")
