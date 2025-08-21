#!/usr/bin/env python3
"""
Simple test script to verify the WebSocket fix works.
This script will simulate the interview flow and check if messages are properly received.
"""

import asyncio
import websockets
import json
import time
import requests
import os

# Configuration
BACKEND_URL = "https://prepai-api.onrender.com"
WS_BASE_URL = "wss://prepai-api.onrender.com"

async def test_websocket_flow():
    """Test the complete WebSocket flow with Redis integration."""
    print("🚀 Testing WebSocket flow with Redis integration...")
    
    # Step 1: Start an interview
    print("\n1️⃣ Starting interview...")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/start-interview",
            json={
                "role": "Product Manager",
                "seniority": "Senior",
                "skills": ["Product Sense", "User Research"]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start interview: {response.status_code}")
            return None
            
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Interview started. Session ID: {session_id}")
        return session_id
        
    except Exception as e:
        print(f"❌ Error starting interview: {e}")
        return None

async def test_websocket_connection(session_id: str):
    """Test WebSocket connection and message handling."""
    print(f"\n2️⃣ Testing WebSocket connection for session {session_id}...")
    
    ws_url = f"{WS_BASE_URL}/ws/{session_id}"
    print(f"🔌 Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Wait for connection status message
            print("⏳ Waiting for connection status...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received: {data}")
                
                if data.get('type') == 'connection_status':
                    print("✅ Connection status received")
                elif data.get('type') == 'status':
                    print("✅ Status message received")
                else:
                    print(f"⚠️ Unexpected message type: {data.get('type')}")
                    
            except asyncio.TimeoutError:
                print("⚠️ No connection status received within 5 seconds")
            
            # Wait a bit more for any additional messages
            print("⏳ Waiting for additional messages...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(message)
                print(f"📨 Additional message: {data}")
            except asyncio.TimeoutError:
                print("ℹ️ No additional messages received (this is normal)")
            
            print("✅ WebSocket test completed successfully")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False

async def test_answer_submission(session_id: str):
    """Test submitting an answer and waiting for AI response."""
    print(f"\n3️⃣ Testing answer submission for session {session_id}...")
    
    answer = "I have experience in product management with a focus on user research and strategic thinking."
    print(f"📝 Submitting answer: {answer[:50]}...")
    
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
            print(f"✅ Answer submitted successfully. Task ID: {task_id}")
            return True
        else:
            print(f"❌ Failed to submit answer: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error submitting answer: {e}")
        return False

async def test_ai_response_reception(session_id: str):
    """Test receiving AI response via WebSocket."""
    print(f"\n4️⃣ Testing AI response reception for session {session_id}...")
    
    ws_url = f"{WS_BASE_URL}/ws/{session_id}"
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected for AI response test")
            
            # Wait for AI response (should come from Redis channel)
            print("⏳ Waiting for AI response (up to 30 seconds)...")
            start_time = time.time()
            
            while time.time() - start_time < 30:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    print(f"📨 Message received: {data}")
                    
                    if data.get('type') == 'question':
                        print("🎉 AI question received successfully!")
                        print(f"Question: {data.get('content', 'N/A')}")
                        return True
                    elif data.get('type') == 'connection_status' or data.get('type') == 'status':
                        print(f"ℹ️ Status message: {data.get('message', 'N/A')}")
                        continue
                    else:
                        print(f"📨 Other message: {data}")
                        
                except asyncio.TimeoutError:
                    # Continue waiting
                    elapsed = time.time() - start_time
                    if elapsed % 5 < 1:  # Print progress every 5 seconds
                        print(f"⏳ Still waiting... ({elapsed:.0f}s elapsed)")
                    continue
                    
            print("⚠️ No AI response received within 30 seconds")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket error during AI response test: {e}")
        return False

async def main():
    """Run the complete test sequence."""
    print("🧪 WebSocket Fix Test Suite")
    print("=" * 50)
    
    # Test 1: Start interview
    session_id = await test_websocket_flow()
    if not session_id:
        print("❌ Cannot continue without session ID")
        return
    
    # Test 2: Test WebSocket connection
    ws_success = await test_websocket_connection(session_id)
    if not ws_success:
        print("❌ WebSocket connection test failed")
        return
    
    # Test 3: Submit answer
    submit_success = await test_answer_submission(session_id)
    if not submit_success:
        print("❌ Answer submission test failed")
        return
    
    # Test 4: Wait for AI response
    print("\n⏳ Waiting 5 seconds for answer processing...")
    await asyncio.sleep(5)
    
    ai_response_success = await test_ai_response_reception(session_id)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Interview Start: {'PASS' if session_id else 'FAIL'}")
    print(f"✅ WebSocket Connection: {'PASS' if ws_success else 'FAIL'}")
    print(f"✅ Answer Submission: {'PASS' if submit_success else 'FAIL'}")
    print(f"✅ AI Response Reception: {'PASS' if ai_response_success else 'FAIL'}")
    
    if ai_response_success:
        print("\n🎉 SUCCESS: The WebSocket fix is working!")
        print("The AI should now respond after submitting answers.")
    else:
        print("\n❌ ISSUE: AI response not received.")
        print("The problem might be in the Celery task or Redis setup.")

if __name__ == "__main__":
    asyncio.run(main())
