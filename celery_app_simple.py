# Simplified Celery app for Render deployment without Redis
# This version provides mock implementations to avoid Redis dependency

import os
import json
from typing import Dict, Any, List

# Mock Redis client for development/deployment without Redis
class MockRedisClient:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value
        return True
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
        return True

# Mock Celery app
class MockCelery:
    def __init__(self):
        self.name = "mock_celery"
    
    def task(self, func):
        # Return the function as-is for now
        return func

# Create mock instances
celery = MockCelery()
redis_client = MockRedisClient()

# Mock task decorator
def mock_task(func):
    return func

# Import agent functions (these should work without Redis)
try:
    from agents.evaluation import evaluate_answer
    from agents.persona import generate_ai_question
except ImportError:
    # Mock implementations if agents are not available
    def evaluate_answer(answer, question, skills_to_assess):
        return {
            "scores": {skill: {"score": 3, "feedback": "Mock evaluation"} for skill in skills_to_assess},
            "overall_score": 3,
            "feedback": "Mock feedback - Redis not available"
        }
    
    def generate_ai_question(role, seniority, skills):
        return f"Mock question for {role} {seniority} with skills: {', '.join(skills)}"

@mock_task
def orchestrate_next_turn(session_id: str, user_answer: str) -> Dict[str, Any]:
    """
    Simplified orchestrator task that works without Redis.
    
    This is a mock implementation for deployment without Redis.
    """
    try:
        print(f"🎯 Starting mock orchestration for session {session_id}")
        
        # Mock response for now
        return {
            "status": "success",
            "message": "Mock orchestration completed",
            "session_id": session_id,
            "note": "Redis not available - using mock implementation"
        }
        
    except Exception as e:
        print(f"❌ Mock orchestration error: {e}")
        return {"error": str(e)}

@mock_task
def my_test_task():
    """Mock test task"""
    return {"status": "success", "message": "Mock test task completed"}

# Export the same interface as the original celery_app
__all__ = ['celery', 'redis_client', 'orchestrate_next_turn', 'my_test_task']
