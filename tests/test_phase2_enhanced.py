#!/usr/bin/env python3
"""
Enhanced Test script for Phase 2: The Intelligent Persona Agent (Final Version)
This script tests the new PROBE_HESITATION action and improved conversational intelligence.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_enhanced_router_agent():
    """Test the enhanced Router Agent with PROBE_HESITATION detection"""
    print("🧪 Testing Enhanced Router Agent with PROBE_HESITATION...")
    
    try:
        from agents.persona import RouterAgent
        
        router = RouterAgent()
        
        # Test case 1: User answering a question
        print("\n📋 Test 1: User Answering Question")
        result1 = router.analyze_response(
            current_topic_goal="Assess structured thinking in problem framing",
            user_latest_answer="I would start by understanding the user's needs and then prioritize features based on impact and effort."
        )
        print(f"Result: {result1}")
        
        # Test case 2: User asking for clarification
        print("\n📋 Test 2: User Asking for Clarification")
        result2 = router.analyze_response(
            current_topic_goal="Assess structured thinking in problem framing",
            user_latest_answer="Can you tell me more about the mobile application? I'm not sure I understand the context."
        )
        print(f"Result: {result2}")
        
        # Test case 3: User expressing hesitation/reluctance
        print("\n📋 Test 3: User Expressing Hesitation")
        result3 = router.analyze_response(
            current_topic_goal="Assess structured thinking in problem framing",
            user_latest_answer="This is a really broad problem. I'm not sure where to start. It feels overwhelming."
        )
        print(f"Result: {result3}")
        
        # Test case 4: User pushing back/refusing
        print("\n📋 Test 4: User Pushing Back")
        result4 = router.analyze_response(
            current_topic_goal="Assess structured thinking in problem framing",
            user_latest_answer="I don't think I have enough information to answer this properly. Can we focus on something else?"
        )
        print(f"Result: {result4}")
        
        # Test case 5: User showing confusion
        print("\n📋 Test 5: User Showing Confusion")
        result5 = router.analyze_response(
            current_topic_goal="Assess structured thinking in problem framing",
            user_latest_answer="I'm confused about what you're asking. This doesn't make sense to me."
        )
        print(f"Result: {result5}")
        
        # Verify that different types of responses are properly classified
        classifications = {
            "answer": result1.get("next_action"),
            "clarification": result2.get("next_action"),
            "hesitation": result3.get("next_action"),
            "pushback": result4.get("next_action"),
            "confusion": result5.get("next_action")
        }
        
        print(f"\n📊 Classification Results:")
        for response_type, action in classifications.items():
            print(f"   {response_type.capitalize()}: {action}")
        
        # Check if PROBE_HESITATION is being used appropriately
        hesitation_actions = [result3.get("next_action"), result4.get("next_action"), result5.get("next_action")]
        probe_hesitation_count = sum(1 for action in hesitation_actions if action == "PROBE_HESITATION")
        
        if probe_hesitation_count >= 2:
            print(f"✅ Router Agent correctly identifies hesitation/pushback ({probe_hesitation_count}/3 cases)")
            return True
        else:
            print(f"❌ Router Agent only identified {probe_hesitation_count}/3 hesitation cases as PROBE_HESITATION")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced Router Agent test failed: {e}")
        return False

def test_enhanced_generator_agent():
    """Test the enhanced Generator Agent with PROBE_HESITATION handling"""
    print("\n🧪 Testing Enhanced Generator Agent with PROBE_HESITATION...")
    
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
        
        # Test case 1: PROBE_HESITATION action
        print("\n📋 Test 1: PROBE_HESITATION Action")
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
            conversation_history=[
                {"question": "How would you approach improving user adoption?", "answer": "This is really broad. I'm not sure where to start."}
            ],
            triggering_action="PROBE_HESITATION"
        )
        
        if "error" not in result1:
            print("✅ PROBE_HESITATION response generated successfully!")
            print(f"   Response: {result1['response_text'][:100]}...")
            
            # Check if response shows empathy and encouragement
            response_text = result1['response_text'].lower()
            empathy_indicators = ["understand", "broad", "specific", "clarity", "help", "simplify"]
            empathy_count = sum(1 for indicator in empathy_indicators if indicator in response_text)
            
            if empathy_count >= 2:
                print("✅ Response shows appropriate empathy and encouragement")
                return True
            else:
                print(f"❌ Response lacks empathy indicators (found {empathy_count}/6)")
                return False
        else:
            print(f"❌ PROBE_HESITATION failed: {result1.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced Generator Agent test failed: {e}")
        return False

def test_safety_rules():
    """Test that the AI doesn't leak internal instructions"""
    print("\n🧪 Testing Safety Rules (No Prompt Leaking)...")
    
    try:
        from agents.persona import GeneratorAgent
        
        generator = GeneratorAgent()
        
        # Mock case study details
        case_study_details = {
            "companyName": "TestCorp",
            "companyDescription": "A test company",
            "appName": "TestApp",
            "platform": "Web Application",
            "techStack": ["React", "Node.js"],
            "userBase": "Test users",
            "coreProblem": "Test problem",
            "keyFeatures": ["Feature 1", "Feature 2"]
        }
        
        # Test that the AI doesn't reveal internal instructions
        result = generator.generate_response(
            persona_role="Senior Product Manager",
            persona_company_context="TestCorp",
            interview_style="Professional and engaging",
            session_narrative="Test narrative",
            case_study_details=case_study_details,
            topic_graph_json=[],
            current_topic_id="test",
            covered_topic_ids=[],
            conversation_history=[],
            triggering_action="START_INTERVIEW"
        )
        
        if "error" not in result:
            response_text = result['response_text'].lower()
            
            # Check for forbidden terms that would indicate prompt leaking
            forbidden_terms = [
                "triggering_action", "next_action", "router agent", "generator agent",
                "persona agent", "case_study_details", "topic_graph_json", "session_state",
                "rules of engagement", "critical safety rule", "output schema"
            ]
            
            leaked_terms = [term for term in forbidden_terms if term in response_text]
            
            if not leaked_terms:
                print("✅ No internal instructions leaked - Safety rules working correctly!")
                return True
            else:
                print(f"❌ Internal instructions leaked: {leaked_terms}")
                return False
        else:
            print(f"❌ Safety test failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Safety rules test failed: {e}")
        return False

def test_enhanced_start_interview():
    """Test the enhanced START_INTERVIEW logic with aspirational persona"""
    print("\n🧪 Testing Enhanced START_INTERVIEW Logic...")
    
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
        
        # Test the new START_INTERVIEW logic
        result = generator.generate_response(
            persona_role="Senior Product Manager",
            persona_company_context="a top-tier tech company working on large-scale consumer products",
            interview_style="Professional and engaging",
            session_narrative="Your team needs to reduce user churn in the first 30 days after signup.",
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
            print(f"✅ START_INTERVIEW response generated successfully!")
            print(f"   Response: {response_text[:200]}...")
            
            # Check for the new START_INTERVIEW elements
            response_lower = response_text.lower()
            
            # Check for aspirational self-introduction
            has_greeting = any(phrase in response_lower for phrase in ["hi", "hello", "thanks for", "my name is"])
            has_persona = any(phrase in response_lower for phrase in ["product manager", "senior", "tech company"])
            
            # Check for case study transition
            has_transition = any(phrase in response_lower for phrase in ["hypothetical", "imagine", "let's walk through", "for our session"])
            
            # Check for narrative presentation
            has_narrative = "innovatecorp" in response_lower or "smartinvest" in response_lower
            
            # Check for opening question
            has_question = "?" in response_text
            
            print(f"\n📊 START_INTERVIEW Elements Check:")
            print(f"   ✅ Greeting & Persona: {has_greeting and has_persona}")
            print(f"   ✅ Case Study Transition: {has_transition}")
            print(f"   ✅ Narrative Presentation: {has_narrative}")
            print(f"   ✅ Opening Question: {has_question}")
            
            # Require at least 3 out of 4 elements to pass
            elements_present = sum([has_greeting and has_persona, has_transition, has_narrative, has_question])
            
            if elements_present >= 3:
                print(f"✅ START_INTERVIEW logic working correctly ({elements_present}/4 elements present)")
                return True
            else:
                print(f"❌ START_INTERVIEW missing elements ({elements_present}/4 elements present)")
                return False
        else:
            print(f"❌ START_INTERVIEW failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Enhanced START_INTERVIEW test failed: {e}")
        return False

def main():
    """Run all enhanced Phase 2 tests"""
    print("🚀 Starting Enhanced Phase 2 Testing: Final Conversational Intelligence")
    print("=" * 80)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set. Please set it before running tests.")
        return False
    
    print("✅ Environment check passed")
    
    # Run tests
    tests = [
        ("Enhanced Router Agent (PROBE_HESITATION)", test_enhanced_router_agent),
        ("Enhanced Generator Agent (PROBE_HESITATION)", test_enhanced_generator_agent),
        ("Safety Rules (No Prompt Leaking)", test_safety_rules),
        ("Enhanced START_INTERVIEW Logic", test_enhanced_start_interview)
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
    print("\n" + "=" * 80)
    print("📊 ENHANCED PHASE 2 TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Enhanced Phase 2 implementation is working correctly!")
        print("\n✅ What's been enhanced:")
        print("   - PROBE_HESITATION action for user hesitation/pushback")
        print("   - Improved sentiment analysis and intent classification")
        print("   - Enhanced empathy and encouragement in responses")
        print("   - Safety rules to prevent prompt leaking")
        print("   - Redundancy avoidance for better conversation flow")
        print("   - More natural and resilient conversational AI")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
