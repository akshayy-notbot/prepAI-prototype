#!/usr/bin/env python3
"""
Debug script for the interview flow issue where AI doesn't respond after first answer.
This script will test the backend endpoints and Redis pub/sub mechanism step by step.
"""

import requests
import json
import time
import redis
import os
from typing import Dict, Any

# Configuration
BACKEND_URL = "https://prepai-api.onrender.com"
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

def log(message: str, level: str = "INFO"):
    """Log messages with timestamp and level."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_backend_health():
    """Test if the backend is accessible."""
    log("Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            log("✅ Backend health check passed", "SUCCESS")
            return True
        else:
            log(f"❌ Backend health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Backend connection error: {e}", "ERROR")
        return False

def start_interview(role: str, seniority: str, skills: list) -> Dict[str, Any]:
    """Start an interview and return the session data."""
    log(f"Starting interview for {role} ({seniority}) with skills: {skills}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/start-interview",
            json={
                "role": role,
                "seniority": seniority,
                "skills": skills
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            log(f"✅ Interview started successfully. Session ID: {session_id}", "SUCCESS")
            return data
        else:
            log(f"❌ Failed to start interview: {response.status_code}", "ERROR")
            log(f"Response: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log(f"❌ Interview start error: {e}", "ERROR")
        return None

def submit_answer(session_id: str, answer: str) -> Dict[str, Any]:
    """Submit an answer and return the response."""
    log(f"Submitting answer for session {session_id}")
    log(f"Answer: {answer[:50]}...")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/submit-answer",
            json={
                "session_id": session_id,
                "answer": answer
            },
            timeout=30
        )
        
        if response.status_code == 202:
            data = response.json()
            task_id = data.get('task_id')
            log(f"✅ Answer submitted successfully. Task ID: {task_id}", "SUCCESS")
            return data
        else:
            log(f"❌ Failed to submit answer: {response.status_code}", "ERROR")
            log(f"Response: {response.text}", "ERROR")
            return None
            
    except Exception as e:
        log(f"❌ Answer submission error: {e}", "ERROR")
        return None

def test_redis_connection():
    """Test Redis connection and basic operations."""
    log("Testing Redis connection...")
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        log("✅ Redis connection successful", "SUCCESS")
        return redis_client
    except Exception as e:
        log(f"❌ Redis connection failed: {e}", "ERROR")
        return None

def check_redis_data(redis_client: redis.Redis, session_id: str):
    """Check what data is stored in Redis for the session."""
    log(f"Checking Redis data for session {session_id}")
    
    try:
        # Check interview plan
        plan_key = f"plan:{session_id}"
        plan_data = redis_client.get(plan_key)
        if plan_data:
            plan = json.loads(plan_data)
            log(f"✅ Interview plan found: {len(plan.get('goals', []))} goals", "SUCCESS")
            for goal in plan.get('goals', []):
                log(f"  - {goal.get('skill')}: {goal.get('status')} ({goal.get('probes_needed')} probes needed)", "INFO")
        else:
            log("❌ No interview plan found in Redis", "ERROR")
        
        # Check conversation history
        history_key = f"history:{session_id}"
        history_data = redis_client.get(history_key)
        if history_data:
            history = json.loads(history_data)
            log(f"✅ Conversation history found: {len(history)} turns", "SUCCESS")
            for i, turn in enumerate(history):
                log(f"  Turn {i+1}: Q: {turn.get('question', 'N/A')[:50]}...", "INFO")
                if turn.get('answer'):
                    log(f"         A: {turn.get('answer', 'N/A')[:50]}...", "INFO")
        else:
            log("❌ No conversation history found in Redis", "ERROR")
            
    except Exception as e:
        log(f"❌ Error checking Redis data: {e}", "ERROR")

def test_redis_pubsub(redis_client: redis.Redis, session_id: str, timeout: int = 10):
    """Test Redis pub/sub mechanism to see if messages are being published."""
    log(f"Testing Redis pub/sub for session {session_id} (timeout: {timeout}s)")
    
    try:
        # Subscribe to the session channel
        channel_name = f"channel:{session_id}"
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel_name)
        
        log(f"✅ Subscribed to channel: {channel_name}")
        log("Waiting for messages...")
        
        # Wait for messages
        start_time = time.time()
        message_received = False
        
        while time.time() - start_time < timeout:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                log(f"✅ Message received on channel {channel_name}: {message['data']}", "SUCCESS")
                message_received = True
                break
            time.sleep(0.1)
        
        if not message_received:
            log(f"⚠️ No messages received on channel {channel_name} within {timeout}s", "WARNING")
        
        pubsub.unsubscribe(channel_name)
        pubsub.close()
        return message_received
        
    except Exception as e:
        log(f"❌ Redis pub/sub test failed: {e}", "ERROR")
        return False

def run_full_debug():
    """Run the complete debug sequence."""
    log("🚀 Starting full interview flow debug...", "INFO")
    
    # Step 1: Test backend health
    if not test_backend_health():
        log("❌ Backend health check failed. Stopping debug.", "ERROR")
        return
    
    # Step 2: Test Redis connection
    redis_client = test_redis_connection()
    if not redis_client:
        log("❌ Redis connection failed. Stopping debug.", "ERROR")
        return
    
    # Step 3: Start interview
    interview_data = start_interview(
        role="Product Manager",
        seniority="Senior",
        skills=["Product Sense", "User Research", "Strategic Thinking"]
    )
    
    if not interview_data:
        log("❌ Failed to start interview. Stopping debug.", "ERROR")
        return
    
    session_id = interview_data['session_id']
    
    # Step 4: Check initial Redis data
    log("--- Checking initial Redis data ---", "INFO")
    check_redis_data(redis_client, session_id)
    
    # Step 5: Submit answer
    answer = "I have 5 years of experience as a Product Manager at a tech company. I've led multiple product launches and worked closely with engineering and design teams to deliver user-centric solutions."
    
    submit_result = submit_answer(session_id, answer)
    if not submit_result:
        log("❌ Failed to submit answer. Stopping debug.", "ERROR")
        return
    
    # Step 6: Wait a bit for processing
    log("Waiting 5 seconds for answer processing...", "INFO")
    time.sleep(5)
    
    # Step 7: Check updated Redis data
    log("--- Checking updated Redis data ---", "INFO")
    check_redis_data(redis_client, session_id)
    
    # Step 8: Test Redis pub/sub
    log("--- Testing Redis pub/sub ---", "INFO")
    test_redis_pubsub(redis_client, session_id, timeout=15)
    
    # Step 9: Final status check
    log("--- Final status check ---", "INFO")
    check_redis_data(redis_client, session_id)
    
    log("🎉 Debug sequence completed!", "SUCCESS")

def run_quick_test():
    """Run a quick test to check basic functionality."""
    log("🔍 Running quick test...", "INFO")
    
    if test_backend_health():
        log("✅ Backend is accessible", "SUCCESS")
    else:
        log("❌ Backend is not accessible", "ERROR")
    
    if test_redis_connection():
        log("✅ Redis is accessible", "SUCCESS")
    else:
        log("❌ Redis is not accessible", "ERROR")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        run_quick_test()
    else:
        run_full_debug()
