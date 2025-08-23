#!/usr/bin/env python3
"""
Test script for the new unified PersonaAgent system.
This replaces the old RouterAgent + GeneratorAgent two-prompt system.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded from .env file")
except ImportError:
    print("⚠️  python-dotenv not available, trying to load manually")
    # Manual loading as fallback
    try:
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded manually")
    except Exception as e:
        print(f"❌ Failed to load environment variables: {e}")

def test_unified_persona_agent():
    """Test the new unified PersonaAgent system"""
    print("🧪 Testing Unified PersonaAgent System...")
    
    # Check if environment variables are loaded
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    print(f"✅ GOOGLE_API_KEY found (length: {len(google_api_key)})")
    
    try:
        # Import the new PersonaAgent
        from agents.persona import PersonaAgent
        print("✅ PersonaAgent imported successfully")
        
        # Create an instance
        agent = PersonaAgent()
        print("✅ PersonaAgent instance created successfully")
        
        # Test data
        session_id = "test_session_123"
        topic_graph = [
            {
                "topic_id": "topic_1",
                "topic_name": "Leadership",
                "goal": "Assess leadership capabilities",
                "primary_skill": "Leadership",
                "dependencies": []
            },
            {
                "topic_id": "topic_2", 
                "topic_name": "Problem Solving",
                "goal": "Evaluate problem-solving approach",
                "primary_skill": "Problem Solving",
                "dependencies": ["topic_1"]
            }
        ]
        session_narrative = "This is a behavioral interview to assess leadership and problem-solving skills."
        interviewer_persona = "Senior Product Manager"
        
        print(f"📊 Test topic graph: {len(topic_graph)} topics")
        print(f"📖 Session narrative: {session_narrative[:50]}...")
        
        # Test 1: START_OF_INTERVIEW
        print("\n🔍 Test 1: START_OF_INTERVIEW")
        result1 = agent.process_user_response(
            session_id=session_id,
            user_answer="",  # No user answer for first question
            topic_graph=topic_graph,
            session_narrative=session_narrative,
            interviewer_persona=interviewer_persona
        )
        
        if result1.get("success"):
            print(f"✅ START_OF_INTERVIEW successful")
            print(f"   Turn type: {result1.get('turn_type')}")
            print(f"   Response: {result1.get('response_text', '')[:100]}...")
            print(f"   Current topic: {result1.get('current_topic_id')}")
        else:
            print(f"❌ START_OF_INTERVIEW failed: {result1.get('error')}")
            return False
        
        # Test 2: MID_INTERVIEW
        print("\n🔍 Test 2: MID_INTERVIEW")
        result2 = agent.process_user_response(
            session_id=session_id,
            user_answer="I led a team of 5 developers to deliver a major feature on time.",
            topic_graph=topic_graph,
            session_narrative=session_narrative,
            interviewer_persona=interviewer_persona
        )
        
        if result2.get("success"):
            print(f"✅ MID_INTERVIEW successful")
            print(f"   Turn type: {result2.get('turn_type')}")
            print(f"   Response: {result2.get('response_text', '')[:100]}...")
            print(f"   Current topic: {result2.get('current_topic_id')}")
            print(f"   Goal achieved: {result2.get('goal_achieved')}")
        else:
            print(f"❌ MID_INTERVIEW failed: {result2.get('error')}")
            return False
        
        # Test 3: Check session state persistence
        print("\n🔍 Test 3: Session State Persistence")
        session_state = agent._get_session_state(session_id)
        if session_state:
            print(f"✅ Session state retrieved successfully")
            print(f"   Current topic: {session_state.get('current_topic_id')}")
            print(f"   Covered topics: {session_state.get('covered_topic_ids')}")
            print(f"   Conversation history: {len(session_state.get('conversation_history', []))} turns")
        else:
            print(f"❌ Failed to retrieve session state")
            return False
        
        print("\n🎉 All tests passed! Unified PersonaAgent is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unified_persona_agent()
    sys.exit(0 if success else 1)
