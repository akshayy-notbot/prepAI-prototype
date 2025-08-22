#!/usr/bin/env python3
"""
Test Configuration for Render Deployment
This file contains configuration and helper functions for testing against your live Render infrastructure.
"""

import os
from typing import Dict, Any

# Render-specific test configuration
RENDER_TEST_CONFIG = {
    # API endpoints
    'api_base_url': os.getenv('RENDER_API_URL', 'https://your-api.onrender.com'),
    'health_check_endpoint': '/health',
    'start_interview_endpoint': '/api/interview/start',
    'submit_answer_endpoint': '/api/interview/submit-answer',
    'get_status_endpoint': '/api/interview/{session_id}/status',
    
    # Test data
    'test_role': 'Product Manager',
    'test_seniority': 'Senior',
    'test_skills': ['Problem Framing', 'User Research', 'Data Analysis'],
    
    # Performance thresholds
    'router_agent_target_ms': 750,
    'generator_agent_target_ms': 3000,
    'api_response_target_ms': 2000,
    
    # Test session management
    'test_session_prefix': 'test_session_',
    'cleanup_after_tests': True,
    'max_test_duration_seconds': 300,  # 5 minutes
    
    # Error handling
    'max_retries': 3,
    'retry_delay_seconds': 1,
    'timeout_seconds': 30
}

def get_render_test_headers() -> Dict[str, str]:
    """Get headers for Render API requests"""
    return {
        'Content-Type': 'application/json',
        'User-Agent': 'PrepAI-TestSuite/1.0',
        'Accept': 'application/json'
    }

def get_test_interview_data() -> Dict[str, Any]:
    """Get standardized test data for interview creation"""
    return {
        'role': RENDER_TEST_CONFIG['test_role'],
        'seniority': RENDER_TEST_CONFIG['test_seniority'],
        'skills': RENDER_TEST_CONFIG['test_skills']
    }

def validate_render_environment() -> bool:
    """Validate that all required environment variables are set for Render testing"""
    required_vars = [
        'RENDER_API_URL',
        'DATABASE_URL',
        'REDIS_URL',
        'GOOGLE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables for Render testing: {', '.join(missing_vars)}")
        print("Please set these variables before running Render integration tests.")
        return False
    
    print("✅ Render environment configuration validated")
    return True

def get_test_session_id(prefix: str = None) -> str:
    """Generate a unique test session ID"""
    import time
    import uuid
    
    if prefix is None:
        prefix = RENDER_TEST_CONFIG['test_session_prefix']
    
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}{timestamp}_{unique_id}"

def cleanup_test_session(session_id: str, redis_client=None):
    """Clean up test session data"""
    try:
        if redis_client:
            # Clean up Redis
            keys_to_delete = [
                f"session_state:{session_id}",
                f"plan:{session_id}",
                f"topic_graph:{session_id}",
                f"history:{session_id}"
            ]
            
            for key in keys_to_delete:
                redis_client.delete(key)
            
            print(f"🧹 Cleaned up Redis keys for session: {session_id}")
            
    except Exception as e:
        print(f"⚠️ Warning: Failed to cleanup test session {session_id}: {e}")

def print_render_test_info():
    """Print information about the Render test configuration"""
    print("☁️ Render Test Configuration")
    print("-" * 40)
    print(f"API Base URL: {RENDER_TEST_CONFIG['api_base_url']}")
    print(f"Test Role: {RENDER_TEST_CONFIG['test_role']}")
    print(f"Test Seniority: {RENDER_TEST_CONFIG['test_seniority']}")
    print(f"Test Skills: {', '.join(RENDER_TEST_CONFIG['test_skills'])}")
    print(f"Router Agent Target: < {RENDER_TEST_CONFIG['router_agent_target_ms']}ms")
    print(f"Generator Agent Target: < {RENDER_TEST_CONFIG['generator_agent_target_ms']}ms")
    print(f"API Response Target: < {RENDER_TEST_CONFIG['api_response_target_ms']}ms")
    print(f"Cleanup After Tests: {RENDER_TEST_CONFIG['cleanup_after_tests']}")
    print(f"Max Test Duration: {RENDER_TEST_CONFIG['max_test_duration_seconds']}s")

if __name__ == "__main__":
    # Print configuration when run directly
    print_render_test_info()
    
    # Validate environment
    if validate_render_environment():
        print("\n✅ Ready for Render testing!")
    else:
        print("\n❌ Environment not ready for Render testing")
