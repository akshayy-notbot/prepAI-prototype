#!/usr/bin/env python3
"""
Test script for the AI-Powered Interview Manager
Run this to test the create_interview_plan_with_ai function
"""

import os
from dotenv import load_dotenv
from agents.interview_manager import create_interview_plan_with_ai, get_plan_summary, update_goal_status
import json

# Load environment variables
load_dotenv()

def test_ai_powered_interview_manager():
    """Test the AI-powered interview manager with sample data"""
    
    print("🧪 Testing AI-Powered Interview Manager...")
    print("=" * 60)
    
    # Test 1: Product Manager interview plan
    print("\n📝 Test 1: Product Manager Interview Plan")
    print("-" * 40)
    
    role = "Product Manager"
    seniority = "Senior"
    skills = ["Product Sense", "Leadership"]
    
    try:
        plan = create_interview_plan_with_ai(role, seniority, skills)
        
        if "error" in plan:
            print(f"❌ Plan generation failed: {plan['error']}")
            return
        
        print(f"✅ Session ID: {plan['session_id']}")
        print(f"✅ Persona: {plan['persona']}")
        print(f"✅ Total Goals: {plan['total_goals']}")
        print(f"✅ Estimated Duration: {plan['estimated_duration_minutes']} minutes")
        print(f"✅ Status: {plan['status']}")
        
        print("\n📊 AI-Generated Goals Breakdown:")
        for goal in plan['goals']:
            print(f"  • {goal['skill']}")
            print(f"    - Sub-skill: {goal['sub_skill']}")
            print(f"    - Difficulty: {goal['difficulty']}")
            print(f"    - Probes needed: {goal['probes_needed']}")
            print(f"    - Description: {goal['description'][:60]}...")
        
        print(f"\n🎯 Overall Approach: {plan.get('ai_generated_metadata', {}).get('overall_approach', 'N/A')}")
        print(f"📈 Difficulty Progression: {plan.get('ai_generated_metadata', {}).get('difficulty_progression', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: Software Engineer interview plan
    print("\n📝 Test 2: Software Engineer Interview Plan")
    print("-" * 40)
    
    role = "Software Engineer"
    seniority = "Junior"
    skills = ["System Design", "Technical Problem Solving"]
    
    try:
        plan = create_interview_plan_with_ai(role, seniority, skills)
        
        if "error" in plan:
            print(f"❌ Plan generation failed: {plan['error']}")
        else:
            print(f"✅ Session ID: {plan['session_id']}")
            print(f"✅ Persona: {plan['persona']}")
            print(f"✅ Total Goals: {plan['total_goals']}")
            print(f"✅ Estimated Duration: {plan['estimated_duration_minutes']} minutes")
            
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: Data Analyst interview plan
    print("\n📝 Test 3: Data Analyst Interview Plan")
    print("-" * 40)
    
    role = "Data Analyst"
    seniority = "Mid-Level"
    skills = ["Data Analysis", "Business Acumen", "Communication"]
    
    try:
        plan = create_interview_plan_with_ai(role, seniority, skills)
        
        if "error" in plan:
            print(f"❌ Plan generation failed: {plan['error']}")
        else:
            print(f"✅ Session ID: {plan['session_id']}")
            print(f"✅ Persona: {plan['persona']}")
            print(f"✅ Total Goals: {plan['total_goals']}")
            print(f"✅ Estimated Duration: {plan['estimated_duration_minutes']} minutes")
            
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Test 4: Plan summary
    print("\n📝 Test 4: Plan Summary")
    print("-" * 40)
    
    try:
        # Create a plan for testing
        test_plan = create_interview_plan_with_ai("Product Manager", "Senior", ["Product Sense"])
        
        if "error" not in test_plan:
            summary = get_plan_summary(test_plan)
            print(f"✅ Summary generated successfully")
            print(f"✅ Role: {summary['role']}")
            print(f"✅ Seniority: {summary['seniority']}")
            print(f"✅ Skills breakdown: {len(summary['skills_breakdown'])} skill categories")
            
            for skill, sub_skills in summary['skills_breakdown'].items():
                print(f"  • {skill}: {len(sub_skills)} sub-skills")
        else:
            print(f"❌ Could not generate summary: {test_plan['error']}")
            
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
    
    # Test 5: Goal status update
    print("\n📝 Test 5: Goal Status Update")
    print("-" * 40)
    
    try:
        # Create a simple plan for testing
        test_plan = create_interview_plan_with_ai("Product Manager", "Senior", ["Product Sense"])
        
        if "error" not in test_plan:
            print(f"✅ Initial completed goals: {test_plan['completed_goals']}")
            
            # Update a goal status
            if test_plan['goals']:
                first_goal = test_plan['goals'][0]
                updated_plan = update_goal_status(test_plan, first_goal['skill'], "completed")
                print(f"✅ After update - completed goals: {updated_plan['completed_goals']}")
                
                # Check if the specific goal was updated
                for goal in updated_plan['goals']:
                    if goal['skill'] == first_goal['skill']:
                        print(f"✅ Goal status updated to: {goal['status']}")
                        break
            else:
                print("⚠️ No goals generated to test with")
        else:
            print(f"❌ Could not test goal update: {test_plan['error']}")
                
    except Exception as e:
        print(f"❌ Test 5 failed: {e}")
    
    # Test 6: Full plan structure with AI metadata
    print("\n📝 Test 6: Full AI-Generated Plan Structure")
    print("-" * 40)
    
    try:
        full_plan = create_interview_plan_with_ai("Product Manager", "Manager", ["Product Sense", "Leadership", "Business Acumen"])
        
        if "error" not in full_plan:
            print("📋 Full AI-Generated Interview Plan Structure:")
            print(json.dumps(full_plan, indent=2))
        else:
            print(f"❌ Could not generate full plan: {full_plan['error']}")
        
    except Exception as e:
        print(f"❌ Test 6 failed: {e}")
    
    # Test 7: Edge case - single skill
    print("\n📝 Test 7: Edge Case - Single Skill")
    print("-" * 40)
    
    try:
        single_skill_plan = create_interview_plan_with_ai("Software Engineer", "Intern", ["Communication"])
        
        if "error" not in single_skill_plan:
            print(f"✅ Single skill plan generated successfully")
            print(f"✅ Total goals: {single_skill_plan['total_goals']}")
            print(f"✅ Estimated duration: {single_skill_plan['estimated_duration_minutes']} minutes")
        else:
            print(f"❌ Single skill plan failed: {single_skill_plan['error']}")
        
    except Exception as e:
        print(f"❌ Test 7 failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 AI-Powered Interview Manager Testing Complete!")

if __name__ == "__main__":
    test_ai_powered_interview_manager()
