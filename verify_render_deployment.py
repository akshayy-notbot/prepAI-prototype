#!/usr/bin/env python3
"""
Render Deployment Database Validation Script
This script validates all database-related configurations before deploying to Render

NOTE: This script is for LOCAL testing with .env files.
      In production, environment variables are managed through Render's dashboard.
"""

import os
import sys
import time
from pathlib import Path
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
import redis
import json

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def validate_environment_variables():
    """Validate all required environment variables"""
    print("🔍 Validating Environment Variables")
    print("=" * 40)
    print("Note: In production, these are managed through Render's dashboard")
    print()
    
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string',
        'REDIS_URL': 'Redis connection string', 
        'GOOGLE_API_KEY': 'Google Gemini API key',
        'ENVIRONMENT': 'Deployment environment'
    }
    
    missing_vars = []
    invalid_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: MISSING - {description}")
        elif var == 'GOOGLE_API_KEY' and ('your_' in value or 'placeholder' in value):
            invalid_vars.append(var)
            print(f"❌ {var}: INVALID - Contains placeholder value")
        elif var == 'DATABASE_URL' and not value.startswith('postgresql://'):
            invalid_vars.append(var)
            print(f"❌ {var}: INVALID - Must start with 'postgresql://'")
        elif var == 'REDIS_URL' and not value.startswith('redis://'):
            invalid_vars.append(var)
            print(f"❌ {var}: INVALID - Must start with 'redis://'")
        else:
            # Show first 20 characters for debugging
            display_value = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars or invalid_vars:
        print(f"\n❌ Validation failed: {len(missing_vars)} missing, {len(invalid_vars)} invalid")
        print("\nFor production deployment:")
        print("• DATABASE_URL and REDIS_URL are automatically set by Render services")
        print("• GOOGLE_API_KEY must be set in Render's environment variables")
        print("• ENVIRONMENT should be set to 'production' in Render")
        return False
    
    print("✅ All environment variables are valid")
    return True

def validate_database_connection():
    """Test database connection and schema"""
    print("\n🗄️ Validating Database Connection")
    print("=" * 40)
    
    try:
        from models import get_engine, Base
        
        # Test connection
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Test basic operations
            result = conn.execute(text("SELECT current_database(), current_user"))
            db_info = result.fetchone()
            print(f"✅ Database: {db_info[0]}, User: {db_info[1]}")
            
            # Check if tables exist
            inspector = engine.dialect.inspector(engine)
            existing_tables = inspector.get_table_names()
            
            required_tables = [
                'interview_sessions',
                'session_states', 
                'topic_graphs',
                'analysis_orchestrators',
                'specialist_agents',
                'user_responses',
                'analysis_results',
                'skill_performance'
            ]
            
            missing_tables = []
            for table in required_tables:
                if table in existing_tables:
                    print(f"✅ Table exists: {table}")
                else:
                    missing_tables.append(table)
                    print(f"❌ Table missing: {table}")
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {missing_tables}")
                print("   Run migrate_database.py to create missing tables")
                return False
            
            # Test table structure
            print("\n🔍 Testing table structure...")
            for table in required_tables[:3]:  # Test first 3 tables
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"✅ {table}: {count} records")
                except Exception as e:
                    print(f"❌ {table}: Error - {e}")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database validation failed: {e}")
        return False

def validate_redis_connection():
    """Test Redis connection and functionality"""
    print("\n🔴 Validating Redis Connection")
    print("=" * 40)
    
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("❌ REDIS_URL not set")
            return False
        
        # Test connection
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()
        print("✅ Redis connection successful")
        
        # Test basic operations
        test_key = "render_deployment_test"
        test_value = {"test": "data", "timestamp": time.time()}
        
        # Test JSON operations (critical for new architecture)
        redis_client.set(test_key, json.dumps(test_value), ex=60)
        retrieved = redis_client.get(test_key)
        
        if retrieved and json.loads(retrieved) == test_value:
            print("✅ Redis JSON operations working")
        else:
            print("❌ Redis JSON operations failed")
            return False
        
        # Test session state operations (critical for new architecture)
        session_key = "session_state:test_session"
        session_data = {
            "current_topic_id": "topic_01",
            "covered_topic_ids": [],
            "conversation_history": [],
            "created_at": time.time()
        }
        
        redis_client.set(session_key, json.dumps(session_data), ex=3600)
        session_retrieved = redis_client.get(session_key)
        
        if session_retrieved and json.loads(session_retrieved) == session_data:
            print("✅ Redis session state operations working")
        else:
            print("❌ Redis session state operations failed")
            return False
        
        # Cleanup test data
        redis_client.delete(test_key, session_key)
        print("✅ Redis cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis validation failed: {e}")
        return False

def validate_database_pool_settings():
    """Validate database connection pool settings"""
    print("\n🏊 Validating Database Pool Settings")
    print("=" * 40)
    
    try:
        from models import get_engine
        
        engine = get_engine()
        pool = engine.pool
        
        print(f"✅ Pool size: {pool.size()}")
        print(f"✅ Max overflow: {pool._max_overflow}")
        print(f"✅ Pool timeout: {pool._timeout}")
        
        # Test connection pool under load
        print("\n🔍 Testing connection pool...")
        connections = []
        
        try:
            for i in range(5):  # Test 5 concurrent connections
                conn = engine.connect()
                connections.append(conn)
                print(f"✅ Connection {i+1} acquired")
            
            print("✅ Connection pool working correctly")
            
        finally:
            # Cleanup connections
            for conn in connections:
                conn.close()
            print("✅ All connections properly closed")
        
        return True
        
    except Exception as e:
        print(f"❌ Pool validation failed: {e}")
        return False

def validate_architecture_compatibility():
    """Validate that the new architecture is compatible with the database"""
    print("\n🏗️ Validating Architecture Compatibility")
    print("=" * 40)
    
    try:
        from models import get_session_local, InterviewSession, SessionState
        from agents.persona import PersonaAgent
        
        # Test PersonaAgent initialization
        persona_agent = PersonaAgent()
        print("✅ PersonaAgent initialized successfully")
        
        # Test database session creation
        db = get_session_local()()
        print("✅ Database session created successfully")
        
        # Test model imports and relationships
        session_count = db.query(InterviewSession).count()
        state_count = db.query(SessionState).count()
        
        print(f"✅ InterviewSession model: {session_count} records")
        print(f"✅ SessionState model: {state_count} records")
        
        # Test JSONB field operations (critical for new architecture)
        test_session = InterviewSession(
            session_id="test_arch_validation",
            role="Product Manager",
            seniority="Senior",
            selected_skills=["Product Design", "User Empathy"],
            topic_graph=[{"topic_id": "topic_01", "goal": "Test goal"}],
            session_narrative="Test narrative"
        )
        
        db.add(test_session)
        db.commit()
        print("✅ JSONB field operations working")
        
        # Cleanup test data
        db.delete(test_session)
        db.commit()
        print("✅ Test data cleanup successful")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Architecture validation failed: {e}")
        return False

def generate_deployment_report():
    """Generate a comprehensive deployment report"""
    print("\n📋 Render Deployment Report")
    print("=" * 40)
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": os.getenv('ENVIRONMENT', 'unknown'),
        "database_url": os.getenv('DATABASE_URL', 'not_set')[:30] + "...",
        "redis_url": os.getenv('REDIS_URL', 'not_set')[:30] + "...",
        "google_api_key_set": bool(os.getenv('GOOGLE_API_KEY')),
        "python_version": os.getenv('PYTHON_VERSION', 'unknown')
    }
    
    print(f"📅 Deployment Time: {report['timestamp']}")
    print(f"🌍 Environment: {report['environment']}")
    print(f"🗄️ Database: {report['database_url']}")
    print(f"🔴 Redis: {report['redis_url']}")
    print(f"🤖 Google API: {'✅ Configured' if report['google_api_key_set'] else '❌ Not Configured'}")
    print(f"🐍 Python: {report['python_version']}")
    
    return report

def main():
    """Run all validation checks"""
    print("🚀 PrepAI Render Deployment Validation")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", validate_environment_variables),
        ("Database Connection", validate_database_connection),
        ("Redis Connection", validate_redis_connection),
        ("Database Pool", validate_database_pool_settings),
        ("Architecture Compatibility", validate_architecture_compatibility)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            print(f"\n{'='*20} {check_name} {'='*20}")
            success = check_func()
            results.append((check_name, success))
        except Exception as e:
            print(f"❌ {check_name} failed with exception: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for check_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All validations passed! Ready for Render deployment.")
        generate_deployment_report()
        return True
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
