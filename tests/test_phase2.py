#!/usr/bin/env python3
"""
Test script for Phase 2: The Intelligent Persona Agent
This script tests the new conversational intelligence and case study knowledge base.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_router_agent():
    """Test the Router Agent's ability to distinguish between answers and clarifying questions"""
    print("🧪 Testing Router Agent Intent Classification...")
    
    try:
        from agents.persona import RouterAgent
        
        router = RouterAgent()
        
        # Test case 1: User answering a question
        print("\n📋 Test 1: User Answering Question")
        result1 = router.analyze_response(
            interviewer_persona_summary="Senior Product Manager",
            current_topic_goal="Assess structured thinking in problem framing",
            conversation_history=[],
            user_latest_answer="I would start by understanding the user's needs and then prioritize features based on impact and effort."
        )
        print(f"Result: {result1}")
        
        # Test case 2: User asking for clarification
        print("\n📋 Test 2: User Asking for Clarification")
        result2 = router.analyze_response(
            interviewer_persona_summary="Senior Product Manager",
            current_topic_goal="Assess structured thinking in problem framing",
            conversation_history=[],
            user_latest_answer="Can you tell me more about the mobile application? I'm not sure I understand the context."
        )
        print(f"Result: {result2}")
        
        # Test case 3: User asking another type of question
        print("\n📋 Test 3: User Asking Another Question")
        result3 = router.analyze_response(
            interviewer_persona_summary="Senior Product Manager",
            current_topic_goal="Assess structured thinking in problem framing",
            conversation_history=[],
            user_latest_answer="What do you mean by 'user engagement'? Are we talking about daily active users or time spent in the app?"
        )
        print(f"Result: {result3}")
        
        # Verify that clarifying questions are properly identified
        clarifying_questions = [result2, result3]
        correctly_identified = 0
        
        for result in clarifying_questions:
            if result.get("next_action") == "ANSWER_CLARIFICATION":
                correctly_identified += 1
        
        if correctly_identified >= 2:
            print("✅ Router Agent correctly identifies clarifying questions!")
            return True
        else:
            print(f"❌ Router Agent only identified {correctly_identified}/2 clarifying questions")
            return False
        
    except Exception as e:
        print(f"❌ Router Agent test failed: {e}")
        return False

def test_generator_agent():
    """Test the Generator Agent's ability to handle different triggering actions"""
    print("\n🧪 Testing Generator Agent Response Generation...")
    
    try:
        from agents.persona import GeneratorAgent
        
        generator = GeneratorAgent()
        
        # Mock case study details
        case_study_details = {
            "companyName": "TechFlow Solutions",
            "companyDescription": "A B2B SaaS company specializing in workflow automation",
            "appName": "FlowMaster",
            "platform": "Web Application",
            "techStack": ["React", "Node.js", "PostgreSQL", "Redis"],
            "userBase": "Enterprise teams looking to streamline their processes",
            "coreProblem": "Low user adoption of new features despite high sign-up rates",
            "keyFeatures": ["Workflow Builder", "Team Collaboration", "Analytics Dashboard", "API Integration"]
        }
        
        # Test case 1: START_INTERVIEW action
        print("\n📋 Test 1: START_INTERVIEW Action")
        result1 = generator.generate_response(
            persona_role="Senior Product Manager",
            persona_company_context="TechFlow Solutions",
            interview_style="Professional and engaging",
            session_narrative="Your team is tasked with improving user adoption of new features in FlowMaster.",
            case_study_details=case_study_details,
            topic_graph_json=[
                {
                    "topic_id": "PM_01_Problem_Definition",
                    "primary_skill": "Product Sense",
                    "topic_name": "Problem Definition",
                    "goal": "Assess structured thinking in problem framing",
                    "dependencies": [],
                    "keywords_for_persona_agent": ["user adoption", "problem framing", "hypothesis"]
                }
            ],
            current_topic_id="PM_01_Problem_Definition",
            covered_topic_ids=[],
            conversation_history=[],
            triggering_action="START_INTERVIEW"
        )
        
        if "error" not in result1:
            print("✅ START_INTERVIEW response generated successfully!")
            print(f"   Response: {result1['response_text'][:100]}...")
        else:
            print(f"❌ START_INTERVIEW failed: {result1.get('error', 'Unknown error')}")
            return False
        
        # Test case 2: ANSWER_CLARIFICATION action
        print("\n📋 Test 2: ANSWER_CLARIFICATION Action")
        result2 = generator.generate_response(
            persona_role="Senior Product Manager",
            persona_company_context="TechFlow Solutions",
            interview_style="Professional and engaging",
            session_narrative="Your team is tasked with improving user adoption of new features in FlowMaster.",
            case_study_details=case_study_details,
            topic_graph_json=[
                {
                    "topic_id": "PM_01_Problem_Definition",
                    "primary_skill": "Product Sense",
                    "topic_name": "Problem Definition",
                    "goal": "Assess structured thinking in problem framing",
                    "dependencies": [],
                    "keywords_for_persona_agent": ["user adoption", "problem framing", "hypothesis"]
                }
            ],
            current_topic_id="PM_01_Problem_Definition",
            covered_topic_ids=[],
            conversation_history=[
                {"question": "What's the main challenge you're facing?", "answer": "Can you tell me more about the mobile application?"}
            ],
            triggering_action="ANSWER_CLARIFICATION"
        )
        
        if "error" not in result2:
            print("✅ ANSWER_CLARIFICATION response generated successfully!")
            print(f"   Response: {result2['response_text'][:100]}...")
        else:
            print(f"❌ ANSWER_CLARIFICATION failed: {result2.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Generator Agent test failed: {e}")
        return False

def test_case_study_integration():
    """Test that case study details are properly integrated into responses"""
    print("\n🧪 Testing Case Study Integration...")
    
    try:
        from agents.persona import GeneratorAgent
        
        generator = GeneratorAgent()
        
        # Mock case study details
        case_study_details = {
            "companyName": "InnovateCorp",
            "companyDescription": "A fintech startup building AI-powered investment tools",
            "appName": "SmartInvest",
            "platform": "Mobile (iOS and Android)",
            "techStack": ["React Native", "Python", "TensorFlow", "AWS"],
            "userBase": "Millennial investors aged 25-40",
            "coreProblem": "High user churn in the first 30 days after signup",
            "keyFeatures": ["AI Portfolio Recommendations", "Social Trading", "Educational Content", "Risk Assessment"]
        }
        
        # Test that company name is used in START_INTERVIEW
        result = generator.generate_response(
            persona_role="Senior Product Manager",
            persona_company_context="InnovateCorp",
            interview_style="Professional and engaging",
            session_narrative="Your team needs to reduce user churn in the first 30 days.",
            case_study_details=case_study_details,
            topic_graph_json=[
                {
                    "topic_id": "PM_01_Problem_Definition",
                    "primary_skill": "Product Sense",
                    "topic_name": "Problem Definition",
                    "goal": "Assess structured thinking in problem framing",
                    "dependencies": [],
                    "keywords_for_persona_agent": ["user churn", "problem framing", "hypothesis"]
                }
            ],
            current_topic_id="PM_01_Problem_Definition",
            covered_topic_ids=[],
            conversation_history=[],
            triggering_action="START_INTERVIEW"
        )
        
        if "error" not in result:
            response_text = result['response_text']
            if "InnovateCorp" in response_text:
                print("✅ Company name from case study details is used in response!")
                return True
            else:
                print("❌ Company name from case study details not found in response")
                return False
        else:
            print(f"❌ Case study integration test failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Case study integration test failed: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 Starting Phase 2 Testing: The Intelligent Persona Agent")
    print("=" * 70)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set. Please set it before running tests.")
        return False
    
    print("✅ Environment check passed")
    
    # Run tests
    tests = [
        ("Router Agent Intent Classification", test_router_agent),
        ("Generator Agent Response Generation", test_generator_agent),
        ("Case Study Integration", test_case_study_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PHASE 2 TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 2 implementation is working correctly!")
        print("\n✅ What's been implemented:")
        print("   - Case Study Knowledge Base integration")
        print("   - Enhanced Router Agent with ANSWER_CLARIFICATION detection")
        print("   - Upgraded Generator Agent with context-aware responses")
        print("   - START_INTERVIEW logic for graceful interview starts")
        print("   - ANSWER_CLARIFICATION logic for handling user questions")
        print("   - Optional session_narrative handling for all archetypes")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
