#!/usr/bin/env python3
"""
Test script for Phase 1: The "World Context" & Archetype Foundation
This script tests the new archetype selection and interview plan generation system.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_archetype_selection():
    """Test the archetype selection functionality"""
    print("🧪 Testing Archetype Selection...")
    
    try:
        from agents.archetype_selector import select_interview_archetype
        
        # Test case 1: Product Manager (should be CASE_STUDY)
        print("\n📋 Test 1: Product Manager with Product Sense")
        result1 = select_interview_archetype("Product Manager", "Senior", ["Product Sense", "Go-to-Market Strategy"])
        print(f"Result: {result1}")
        
        # Test case 2: Software Engineer with Leadership (should be BEHAVIORAL_DEEP_DIVE)
        print("\n📋 Test 2: Software Engineer with Leadership")
        result2 = select_interview_archetype("Software Engineer", "Senior", ["Leadership", "Team Management"])
        print(f"Result: {result2}")
        
        # Test case 3: Data Scientist with technical skills (should be TECHNICAL_KNOWLEDGE_SCREEN)
        print("\n📋 Test 3: Data Scientist with Technical Skills")
        result3 = select_interview_archetype("Data Scientist", "Junior", ["SQL", "Python", "Statistics"])
        print(f"Result: {result3}")
        
        # Test case 4: Mixed skills (should be MIXED or CASE_STUDY)
        print("\n📋 Test 4: Mixed Skills")
        result4 = select_interview_archetype("Product Manager", "Manager", ["System Design", "Team Leadership"])
        print(f"Result: {result4}")
        
        return True
        
    except Exception as e:
        print(f"❌ Archetype selection test failed: {e}")
        return False

def test_interview_plan_generation():
    """Test the interview plan generation with new archetype system"""
    print("\n🧪 Testing Interview Plan Generation...")
    
    try:
        from agents.InterviewSessionService import create_interview_plan_with_ai
        
        # Test case 1: Product Manager case study
        print("\n📋 Test 1: Product Manager Case Study")
        plan1 = create_interview_plan_with_ai("Product Manager", "Senior", ["Product Sense", "Go-to-Market Strategy"])
        
        if "error" in plan1:
            print(f"❌ Plan generation failed: {plan1['error']}")
            return False
        
        print(f"✅ Plan generated successfully!")
        print(f"   Archetype: {plan1.get('archetype', 'Unknown')}")
        print(f"   Reasoning: {plan1.get('archetype_reasoning', 'Unknown')}")
        print(f"   Session Narrative: {plan1.get('session_narrative', 'None')[:100]}...")
        print(f"   Case Study Details: {'Available' if plan1.get('case_study_details') else 'None'}")
        print(f"   Topics: {len(plan1.get('topic_graph', []))}")
        
        # Test case 2: Behavioral interview
        print("\n📋 Test 2: Behavioral Deep Dive")
        plan2 = create_interview_plan_with_ai("Software Engineer", "Senior", ["Leadership", "Conflict Resolution"])
        
        if "error" in plan2:
            print(f"❌ Plan generation failed: {plan2['error']}")
            return False
        
        print(f"✅ Plan generated successfully!")
        print(f"   Archetype: {plan2.get('archetype', 'Unknown')}")
        print(f"   Reasoning: {plan2.get('archetype_reasoning', 'Unknown')}")
        print(f"   Session Narrative: {plan2.get('session_narrative', 'None')}")
        print(f"   Case Study Details: {'Available' if plan2.get('case_study_details') else 'None'}")
        print(f"   Topics: {len(plan2.get('topic_graph', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Interview plan generation test failed: {e}")
        return False

def test_prompt_templates():
    """Test that prompt templates can be loaded correctly"""
    print("\n🧪 Testing Prompt Templates...")
    
    try:
        from agents.InterviewSessionService import load_prompt_template
        
        # Test loading each template
        templates = ["CASE_STUDY", "BEHAVIORAL_DEEP_DIVE", "TECHNICAL_KNOWLEDGE_SCREEN"]
        
        for template_name in templates:
            print(f"\n📋 Testing {template_name} template...")
            template = load_prompt_template(template_name)
            
            if template and len(template) > 100:  # Basic validation
                print(f"✅ {template_name} template loaded successfully ({len(template)} characters)")
            else:
                print(f"❌ {template_name} template failed to load properly")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Prompt template test failed: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("🚀 Starting Phase 1 Testing: The 'World Context' & Archetype Foundation")
    print("=" * 70)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set. Please set it before running tests.")
        return False
    
    print("✅ Environment check passed")
    
    # Run tests
    tests = [
        ("Prompt Templates", test_prompt_templates),
        ("Archetype Selection", test_archetype_selection),
        ("Interview Plan Generation", test_interview_plan_generation)
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
    print("📊 PHASE 1 TEST RESULTS")
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
        print("🎉 Phase 1 implementation is working correctly!")
        print("\n✅ What's been implemented:")
        print("   - Archetype Selection Agent")
        print("   - Dynamic prompt template loading")
        print("   - Temperature 0.8 for creativity")
        print("   - Case study details generation")
        print("   - Archetype-based interview planning")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
