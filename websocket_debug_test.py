#!/usr/bin/env python3
"""
WebSocket Debug Test for PrepAI Interview System
Tests the complete flow: interview start, answer submission, and AI response via WebSocket
"""

import asyncio
import websockets
import json
import time
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "https://prepai-api.onrender.com"
WEBSOCKET_URL = "wss://prepai-api.onrender.com"

async def test_complete_interview_flow():
    """Test the complete interview flow with the new Redis subscription fix"""
    print("🚀 Testing Complete Interview Flow with Redis Fix")
    print("=" * 60)
    
    # Step 1: Start an interview
    print("\n📝 Step 1: Starting Interview...")
    try:
        start_response = requests.post(f"{BACKEND_URL}/api/start-interview", json={
            "role": "Product Manager",
            "level": "Senior"
        })
        
        if start_response.status_code == 200:
            interview_data = start_response.json()
            session_id = interview_data.get('session_id')
            print(f"✅ Interview started successfully!")
            print(f"   Session ID: {session_id}")
            print(f"   First Question: {interview_data.get('first_question', '')[:100]}...")
        else:
            print(f"❌ Failed to start interview: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return
    except Exception as e:
        print(f"❌ Error starting interview: {e}")
        return
    
    # Step 2: Connect to WebSocket
    print(f"\n🔌 Step 2: Connecting to WebSocket...")
    websocket_url = f"{WEBSOCKET_URL}/ws/{session_id}"
    print(f"   URL: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Wait for initial messages
            print("\n📨 Waiting for initial WebSocket messages...")
            initial_messages = []
            start_time = time.time()
            
            while time.time() - start_time < 10:  # Wait up to 10 seconds for initial messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    initial_messages.append(message)
                    print(f"📨 Received: {message[:200]}...")
                    
                    # Check if we got the subscription confirmation
                    if "Listening for AI responses" in message:
                        print("✅ Got subscription confirmation message!")
                        break
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"⚠️ Error receiving initial message: {e}")
                    break
            
            print(f"📊 Received {len(initial_messages)} initial messages")
            
            # Step 3: Submit an answer
            print(f"\n✍️ Step 3: Submitting Answer...")
            try:
                answer_response = requests.post(f"{BACKEND_URL}/api/submit-answer", json={
                    "session_id": session_id,
                    "answer": "This is a test answer to verify the Redis subscription fix is working properly."
                })
                
                if answer_response.status_code == 202:
                    task_data = answer_response.json()
                    task_id = task_data.get('task_id')
                    print(f"✅ Answer submitted successfully!")
                    print(f"   Task ID: {task_id}")
                    print(f"   Status: {task_data.get('status', 'Unknown')}")
                else:
                    print(f"❌ Failed to submit answer: {answer_response.status_code}")
                    print(f"   Response: {answer_response.text}")
                    return
            except Exception as e:
                print(f"❌ Error submitting answer: {e}")
                return
            
            # Step 4: Wait for AI response via WebSocket
            print(f"\n🤖 Step 4: Waiting for AI Response via WebSocket...")
            print("   (This should work now with the 2-second Redis subscription delay)")
            
            ai_response_received = False
            start_time = time.time()
            timeout = 30  # Wait up to 30 seconds
            
            while time.time() - start_time < timeout:
                try:
                    # Check for WebSocket messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"📨 WebSocket message: {message[:200]}...")
                    
                    # Parse the message
                    try:
                        data = json.loads(message)
                        if data.get('type') == 'question':
                            ai_question = data.get('content', '')
                            print(f"🎉 SUCCESS! AI Response Received!")
                            print(f"   Question: {ai_question[:100]}...")
                            ai_response_received = True
                            break
                        elif data.get('type') == 'error':
                            print(f"❌ Error message: {data.get('message', 'Unknown error')}")
                            break
                        else:
                            print(f"ℹ️ Other message type: {data.get('type', 'Unknown')}")
                    except json.JSONDecodeError:
                        print(f"⚠️ Non-JSON message: {message}")
                        
                except asyncio.TimeoutError:
                    # Check if we're still within timeout
                    elapsed = time.time() - start_time
                    if elapsed % 5 < 1:  # Print status every 5 seconds
                        print(f"⏳ Still waiting... ({elapsed:.0f}s elapsed)")
                    continue
                except Exception as e:
                    print(f"❌ Error receiving WebSocket message: {e}")
                    break
            
            if ai_response_received:
                print(f"\n🎉 TEST PASSED! The Redis subscription fix is working!")
                print(f"   AI responded in {time.time() - start_time:.1f} seconds")
            else:
                print(f"\n❌ TEST FAILED! No AI response received within {timeout} seconds")
                print(f"   This suggests the Redis subscription fix may not be working")
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return

def main():
    """Main function to run the debug test"""
    print("🔧 PrepAI WebSocket Debug Test")
    print("=" * 40)
    print(f"Backend: {BACKEND_URL}")
    print(f"WebSocket: {WEBSOCKET_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the async test
    asyncio.run(test_complete_interview_flow())
    
    print("\n" + "=" * 40)
    print("Debug test completed!")

if __name__ == "__main__":
    main()
