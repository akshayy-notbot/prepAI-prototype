#!/usr/bin/env python3
"""
Check Celery task status and Redis connectivity to debug the interview flow issue.
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

def check_celery_task_status(task_id: str) -> Dict[str, Any]:
    """Check the status of a specific Celery task."""
    log(f"Checking Celery task status: {task_id}")
    
    try:
        # Try to check task status via the backend (if it has an endpoint)
        response = requests.get(f"{BACKEND_URL}/api/task-status/{task_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            log(f"⚠️ No task status endpoint found: {response.status_code}", "WARNING")
            return {"status": "unknown", "reason": "No status endpoint"}
            
    except Exception as e:
        log(f"❌ Error checking task status: {e}", "ERROR")
        return {"status": "error", "reason": str(e)}

def test_redis_operations():
    """Test Redis read/write operations to verify connectivity."""
    log("Testing Redis operations...")
    
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        
        # Test basic operations
        test_key = f"test_key_{int(time.time())}"
        test_value = f"test_value_{time.strftime('%H:%M:%S')}"
        
        # Write
        redis_client.set(test_key, test_value, ex=60)  # Expire in 60 seconds
        log(f"✅ Redis write test: {test_key} = {test_value}", "SUCCESS")
        
        # Read
        retrieved_value = redis_client.get(test_key)
        if retrieved_value == test_value:
            log(f"✅ Redis read test: {test_key} = {retrieved_value}", "SUCCESS")
        else:
            log(f"❌ Redis read test failed: expected {test_value}, got {retrieved_value}", "ERROR")
        
        # Cleanup
        redis_client.delete(test_key)
        log("✅ Redis cleanup completed", "SUCCESS")
        
        return redis_client
        
    except Exception as e:
        log(f"❌ Redis operations failed: {e}", "ERROR")
        return None

def check_session_data(session_id: str, redis_client: redis.Redis):
    """Check what data exists for a specific session."""
    log(f"Checking session data for: {session_id}")
    
    try:
        # Check interview plan
        plan_key = f"plan:{session_id}"
        plan_data = redis_client.get(plan_key)
        if plan_data:
            plan = json.loads(plan_data)
            log(f"✅ Interview plan found: {len(plan.get('goals', []))} goals", "SUCCESS")
            for goal in plan.get('goals', []):
                log(f"  - {goal.get('skill')}: {goal.get('status')} ({goal.get('probes_needed')} probes)", "INFO")
        else:
            log("❌ No interview plan found", "ERROR")
        
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
            log("❌ No conversation history found", "ERROR")
            
        # Check if there are any pending tasks
        task_keys = redis_client.keys(f"celery-task-meta-*")
        if task_keys:
            log(f"ℹ️ Found {len(task_keys)} Celery task metadata keys", "INFO")
            for key in task_keys[:5]:  # Show first 5
                log(f"  - {key}", "INFO")
        else:
            log("ℹ️ No Celery task metadata found", "INFO")
            
    except Exception as e:
        log(f"❌ Error checking session data: {e}", "ERROR")

def test_redis_pubsub_manual(session_id: str, redis_client: redis.Redis):
    """Manually test Redis pub/sub to see if messages are being published."""
    log(f"Manually testing Redis pub/sub for session: {session_id}")
    
    try:
        # Subscribe to the session channel
        channel_name = f"channel:{session_id}"
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel_name)
        
        log(f"✅ Subscribed to channel: {channel_name}")
        log("⏳ Waiting for messages (10 seconds)...")
        
        # Wait for messages
        start_time = time.time()
        message_received = False
        
        while time.time() - start_time < 10:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                log(f"✅ Message received on channel {channel_name}: {message['data']}", "SUCCESS")
                message_received = True
                break
            time.sleep(0.1)
        
        if not message_received:
            log(f"⚠️ No messages received on channel {channel_name} within 10 seconds", "WARNING")
            
            # Check if the channel exists and has any subscribers
            pubsub_channels = redis_client.pubsub_channels()
            log(f"ℹ️ Available channels: {pubsub_channels}", "INFO")
            
            # Check if there are any messages in the channel
            channel_info = redis_client.pubsub_numsub(channel_name)
            log(f"ℹ️ Channel {channel_name} subscribers: {channel_info}", "INFO")
        
        pubsub.unsubscribe(channel_name)
        pubsub.close()
        return message_received
        
    except Exception as e:
        log(f"❌ Redis pub/sub test failed: {e}", "ERROR")
        return False

def simulate_celery_task_manually(session_id: str, redis_client: redis.Redis):
    """Manually simulate what the Celery task should do to test the flow."""
    log(f"Manually simulating Celery task for session: {session_id}")
    
    try:
        # Get the current conversation history
        history_key = f"history:{session_id}"
        history_data = redis_client.get(history_key)
        
        if not history_data:
            log("❌ No conversation history found to simulate", "ERROR")
            return False
        
        history = json.loads(history_data)
        log(f"✅ Found {len(history)} conversation turns", "SUCCESS")
        
        # Simulate adding a new AI question
        new_question = "This is a test question to verify the WebSocket Redis integration is working."
        new_turn = {
            "question": new_question,
            "answer": None,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "question_type": "test_simulation"
        }
        
        history.append(new_turn)
        
        # Save updated history
        redis_client.set(history_key, json.dumps(history), ex=3600)
        log("✅ Updated conversation history", "SUCCESS")
        
        # Publish to Redis channel (this is what the Celery task should do)
        channel_name = f"channel:{session_id}"
        redis_client.publish(channel_name, new_question)
        log(f"✅ Published test question to channel: {channel_name}", "SUCCESS")
        
        return True
        
    except Exception as e:
        log(f"❌ Manual simulation failed: {e}", "ERROR")
        return False

def main():
    """Main debugging function."""
    log("🔍 Celery and Redis Debug Tool")
    log("=" * 50)
    
    # Get session ID from user
    session_id = input("Enter the session ID from your test (or press Enter to skip): ").strip()
    
    if not session_id:
        log("⚠️ No session ID provided, running basic tests only", "WARNING")
        session_id = "test_session_123"
    
    # Test 1: Redis connectivity
    log("\n1️⃣ Testing Redis connectivity...")
    redis_client = test_redis_operations()
    if not redis_client:
        log("❌ Cannot continue without Redis connection", "ERROR")
        return
    
    # Test 2: Check session data
    log("\n2️⃣ Checking session data...")
    check_session_data(session_id, redis_client)
    
    # Test 3: Test Redis pub/sub
    log("\n3️⃣ Testing Redis pub/sub...")
    test_redis_pubsub_manual(session_id, redis_client)
    
    # Test 4: Manual simulation
    log("\n4️⃣ Manually simulating Celery task...")
    if simulate_celery_task_manually(session_id, redis_client):
        log("✅ Manual simulation completed", "SUCCESS")
        
        # Test 5: Check if WebSocket receives the simulated message
        log("\n5️⃣ Testing WebSocket reception...")
        log("⚠️ Now go back to your browser and check if the WebSocket received the test question", "WARNING")
        log("⚠️ You should see a message like: 'This is a test question to verify...'", "WARNING")
        
        # Wait a bit and test pub/sub again
        log("⏳ Waiting 5 seconds, then testing pub/sub again...")
        time.sleep(5)
        test_redis_pubsub_manual(session_id, redis_client)
    
    log("\n🎯 Debug session completed!", "SUCCESS")

if __name__ == "__main__":
    main()
