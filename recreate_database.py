#!/usr/bin/env python3
"""
Database recreation script for the new two-loop architecture.
This script will drop all existing tables and recreate them with the new schema.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def recreate_database():
    """Recreate the database with new schema"""
    print("🗄️ Recreating database with new two-loop architecture schema...")
    
    try:
        # Import models after environment is loaded
        import models
        from sqlalchemy import text
        
        # Get database engine
        engine = models.engine
        
        # Drop all existing tables
        print("🗑️ Dropping existing tables...")
        models.Base.metadata.drop_all(bind=engine)
        print("✅ All existing tables dropped")
        
        # Create new tables with updated schema
        print("🏗️ Creating new tables with updated schema...")
        models.create_tables()
        print("✅ New tables created successfully")
        
        # Verify table creation
        print("\n📋 Verifying new table structure...")
        with get_engine().connect() as conn:
            # Get list of tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result]
            
            print("📊 Created tables:")
            for table in tables:
                print(f"  - {table}")
            
            # Check specific new tables
            new_tables = [
                'interview_sessions',
                'session_states', 
                'topic_graphs',
                'analysis_orchestrators',
                'specialist_agents'
            ]
            
            missing_tables = [table for table in new_tables if table not in tables]
            if missing_tables:
                print(f"⚠️ Missing expected tables: {missing_tables}")
                return False
            
            print("✅ All expected tables created successfully")
        
        # Test inserting a sample record
        print("\n🧪 Testing database functionality...")
        try:
            from sqlalchemy.orm import Session
            db = models.get_session_local()()
            
            # Test creating a sample topic graph
            sample_topic_graph = [
                {
                    "topic_id": "PM_01_Problem_Definition",
                    "primary_skill": "Problem Framing",
                    "topic_name": "Defining User Personas",
                    "goal": "Assess structured thinking in problem framing.",
                    "dependencies": [],
                    "keywords_for_persona_agent": ["user personas", "problem definition", "user research"]
                }
            ]
            
            # Create a sample interview session
            sample_session = models.InterviewSession(
                session_id="test_session_001",
                role="Product Manager",
                seniority="Senior",
                selected_skills=["Product Sense", "User Research"],
                topic_graph=sample_topic_graph,
                session_narrative="Test session for database validation",
                final_current_topic_id="PM_01_Problem_Definition",  # Updated field name
                final_covered_topic_ids=[],  # Updated field name
                status="ready"
            )
            
            db.add(sample_session)
            db.commit()
            print("✅ Sample interview session created successfully")
            
            # Test retrieving the session
            retrieved_session = db.query(models.InterviewSession).filter(
                models.InterviewSession.session_id == "test_session_001"
            ).first()
            
            if retrieved_session:
                print(f"✅ Session retrieved: {retrieved_session.role} {retrieved_session.seniority}")
                print(f"📊 Topic graph has {len(retrieved_session.topic_graph)} topics")
                print(f"📖 Narrative: {retrieved_session.session_narrative[:50]}...")
            else:
                print("❌ Failed to retrieve created session")
                return False
            
            # Clean up test data
            db.delete(retrieved_session)
            db.commit()
            print("✅ Test data cleaned up")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Database functionality test failed: {e}")
            return False
        
        print("\n🎉 Database recreation completed successfully!")
        print("📋 New schema includes:")
        print("  - Enhanced InterviewSession with topic_graph")
        print("  - SessionState for real-time state management")
        print("  - TopicGraph for reusable interview blueprints")
        print("  - AnalysisOrchestrator for post-interview analysis")
        print("  - SpecialistAgent for parallel analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Database recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("🚀 Database Recreation Script for New Two-Loop Architecture")
    print("=" * 60)
    
    # Check environment variables
    required_vars = ['DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set DATABASE_URL before running this script.")
        sys.exit(1)
    
    # Confirm with user
    print("\n⚠️  WARNING: This will DESTROY all existing data!")
    print("This script will:")
    print("  1. Drop ALL existing tables")
    print("  2. Create new tables with updated schema")
    print("  3. Test the new database functionality")
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("❌ Database recreation cancelled by user")
        sys.exit(0)
    
    # Proceed with recreation
    success = recreate_database()
    
    if success:
        print("\n✅ Database recreation completed successfully!")
        print("🚀 You can now run the new architecture!")
    else:
        print("\n❌ Database recreation failed!")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
