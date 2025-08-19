#!/usr/bin/env python3
"""
Test script for the new API endpoints
Tests the integration of interview_manager and persona agent with FastAPI
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on a different port

def test_api_integration():
    """Test the new API endpoints"""
    
    print("🧪 Testing API Integration...")
    print("=" * 50)
    
    # Test 1: Start Interview
    print("\n📝 Test 1: Start Interview")
    print("-" * 30)
    
    start_interview_data = {
        "role": "Product Manager",
        "seniority": "Senior",
        "skills": ["Product Sense", "Leadership"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/start-interview", json=start_interview_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Interview started successfully!")
            print(f"✅ Session ID: {result.get('session_id')}")
            print(f"✅ First Question: {result.get('first_question', '')[:100]}...")
            print(f"✅ Total Goals: {result.get('total_goals')}")
            print(f"✅ Estimated Duration: {result.get('estimated_duration_minutes')} minutes")
            
            session_id = result.get('session_id')
            
            # Test 2: Get Interview Status
            print("\n📝 Test 2: Get Interview Status")
            print("-" * 30)
            
            status_response = requests.get(f"{BASE_URL}/api/interview/{session_id}/status")
            
            if status_response.status_code == 200:
                status_result = status_response.json()
                print(f"✅ Status retrieved successfully!")
                print(f"✅ Role: {status_result.get('role')}")
                print(f"✅ Seniority: {status_result.get('seniority')}")
                print(f"✅ Progress: {status_result.get('progress_percentage')}%")
                print(f"✅ Current Question: {status_result.get('current_question', '')[:100]}...")
                
                # Test 3: Get Next Question
                print("\n📝 Test 3: Get Next Question")
                print("-" * 30)
                
                next_question_data = {
                    "answer": "I would start by understanding the user's needs through research and interviews, then prioritize features based on impact and feasibility. I'd also consider technical constraints and business goals."
                }
                
                next_response = requests.post(f"{BASE_URL}/api/interview/{session_id}/next-question", json=next_question_data)
                
                if next_response.status_code == 200:
                    next_result = next_response.json()
                    print(f"✅ Next question generated successfully!")
                    print(f"✅ Next Question: {next_result.get('next_question', '')[:100]}...")
                    print(f"✅ Question Number: {next_result.get('question_number')}")
                    print(f"✅ Total Questions Asked: {next_result.get('total_questions_asked')}")
                    
                    # Test 4: Check Updated Status
                    print("\n📝 Test 4: Check Updated Status")
                    print("-" * 30)
                    
                    updated_status_response = requests.get(f"{BASE_URL}/api/interview/{session_id}/status")
                    
                    if updated_status_response.status_code == 200:
                        updated_status = updated_status_response.json()
                        print(f"✅ Updated status retrieved!")
                        print(f"✅ Questions Asked: {updated_status.get('questions_asked')}")
                        print(f"✅ Questions Answered: {updated_status.get('questions_answered')}")
                        print(f"✅ Progress: {updated_status.get('progress_percentage')}%")
                    else:
                        print(f"❌ Failed to get updated status: {updated_status_response.status_code}")
                        print(f"❌ Error: {updated_status_response.text}")
                        
                else:
                    print(f"❌ Failed to get next question: {next_response.status_code}")
                    print(f"❌ Error: {next_response.text}")
                    
            else:
                print(f"❌ Failed to get status: {status_response.status_code}")
                print(f"❌ Error: {status_response.text}")
                
        else:
            print(f"❌ Failed to start interview: {response.status_code}")
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure your FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 API Integration Testing Complete!")

def test_error_handling():
    """Test error handling in the API endpoints"""
    
    print("\n🧪 Testing Error Handling...")
    print("=" * 50)
    
    # Test 1: Invalid session ID
    print("\n📝 Test 1: Invalid Session ID")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/interview/invalid-session-id/status")
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Missing answer in next question
    print("\n📝 Test 2: Missing Answer in Next Question")
    print("-" * 30)
    
    try:
        response = requests.post(f"{BASE_URL}/api/interview/test-session/next-question", json={})
        print(f"✅ Status code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Error Handling Testing Complete!")

if __name__ == "__main__":
    print("🚀 Starting API Integration Tests...")
    print("Make sure your FastAPI server is running!")
    print("=" * 50)
    
    # Wait a moment for user to read
    time.sleep(2)
    
    test_api_integration()
    test_error_handling()
