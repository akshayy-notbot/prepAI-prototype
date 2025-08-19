#!/usr/bin/env python3
"""
Test script for the Persona Agent
Run this to test the generate_ai_question function
"""

import os
from dotenv import load_dotenv
from agents.persona import generate_ai_question, generate_follow_up_question, generate_skill_specific_question

# Load environment variables
load_dotenv()

def test_persona_agent():
    """Test the persona agent with sample data"""
    
    print("🧪 Testing Persona Agent...")
    print("=" * 50)
    
    # Test 1: Basic question generation
    print("\n📝 Test 1: Basic Question Generation")
    print("-" * 30)
    
    persona = "Senior Product Manager at Google"
    instructions = "Ask a question about product strategy and user research"
    history = []
    
    try:
        question = generate_ai_question(persona, instructions, history)
        print(f"✅ Generated Question: {question}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: Follow-up question with history
    print("\n📝 Test 2: Follow-up Question with History")
    print("-" * 30)
    
    history = [
        {
            "question": "How would you approach understanding user needs for a new feature?",
            "answer": "I would start by conducting user interviews and surveys to understand pain points, then analyze usage data to identify patterns and opportunities."
        }
    ]
    
    instructions = "Ask a follow-up question about their research methodology"
    
    try:
        question = generate_ai_question(persona, instructions, history)
        print(f"✅ Generated Follow-up: {question}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: Follow-up question function
    print("\n📝 Test 3: Follow-up Question Function")
    print("-" * 30)
    
    last_answer = "I would prioritize based on user impact and business value, using a scoring matrix to evaluate different approaches."
    skills_focus = ["Prioritization", "Business Acumen"]
    
    try:
        question = generate_follow_up_question(persona, last_answer, skills_focus)
        print(f"✅ Generated Follow-up: {question}")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Test 4: Skill-specific question
    print("\n📝 Test 4: Skill-Specific Question")
    print("-" * 30)
    
    try:
        question = generate_skill_specific_question(persona, "Data Analysis", "advanced")
        print(f"✅ Generated Skill Question: {question}")
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Persona Agent Testing Complete!")

if __name__ == "__main__":
    test_persona_agent()
