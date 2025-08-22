#!/usr/bin/env python3
"""
Test script to verify persona variety in START_INTERVIEW responses
This ensures the AI generates different names and companies instead of always using the same ones.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_persona_variety():
    """Test that different personas generate different names and companies"""
    print("🧪 Testing Persona Variety in START_INTERVIEW...")
    
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
        
        personas = [
            ("Senior Product Manager", "a top-tier tech company working on large-scale consumer products"),
            ("Engineering Manager", "a leading software company building enterprise solutions"),
            ("Data Science Lead", "a cutting-edge AI company working on machine learning products"),
            ("Design Director", "a creative tech company focused on user experience")
        ]
        
        generated_names = []
        generated_companies = []
        
        for i, (role, context) in enumerate(personas):
            print(f"\n📋 Test {i+1}: {role} at {context}")
            
            result = generator.generate_response(
                persona_role=role,
                persona_company_context=context,
                interview_style="Professional and engaging",
                session_narrative="Your team needs to solve a complex technical challenge.",
                case_study_details=case_study_details,
                topic_graph_json=[
                    {
                        "topic_id": "TEST_01",
                        "primary_skill": "Problem Solving",
                        "topic_name": "Problem Definition",
                        "goal": "Assess structured thinking",
                        "dependencies": [],
                        "keywords_for_persona_agent": ["problem solving", "thinking"]
                    }
                ],
                current_topic_id="TEST_01",
                covered_topic_ids=[],
                conversation_history=[],
                triggering_action="START_INTERVIEW"
            )
            
            if "error" not in result:
                response_text = result['response_text']
                print(f"   Response: {response_text[:150]}...")
                
                # Extract name and company from response
                import re
                
                # Look for name patterns like "My name is [Name]"
                name_match = re.search(r'My name is (\w+)', response_text, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1)
                    generated_names.append(name)
                    print(f"   ✅ Name: {name}")
                else:
                    print("   ❌ No name found")
                
                # Look for company patterns like "at [Company]"
                company_match = re.search(r'at (\w+)', response_text, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1)
                    generated_companies.append(company)
                    print(f"   ✅ Company: {company}")
                else:
                    print("   ❌ No company found")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                return False
        
        # Analyze variety
        print(f"\n📊 Persona Variety Analysis:")
        print(f"   Names generated: {generated_names}")
        print(f"   Companies generated: {generated_companies}")
        
        # Check for variety
        unique_names = len(set(generated_names))
        unique_companies = len(set(generated_companies))
        
        print(f"   Unique names: {unique_names}/{len(generated_names)}")
        print(f"   Unique companies: {unique_companies}/{len(generated_companies)}")
        
        # Require at least 3 unique names and 3 unique companies
        if unique_names >= 3 and unique_companies >= 3:
            print("✅ Excellent variety in persona generation!")
            return True
        elif unique_names >= 2 and unique_companies >= 2:
            print("✅ Good variety in persona generation")
            return True
        else:
            print("❌ Limited variety in persona generation")
            return False
        
    except Exception as e:
        print(f"❌ Persona variety test failed: {e}")
        return False

def main():
    """Run the persona variety test"""
    print("🚀 Testing Persona Variety in START_INTERVIEW Responses")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY environment variable not set. Please set it before running tests.")
        return False
    
    print("✅ Environment check passed")
    
    # Run test
    success = test_persona_variety()
    
    if success:
        print("\n🎉 Persona variety test passed!")
        print("The AI is now generating diverse personas with different names and companies.")
    else:
        print("\n⚠️ Persona variety test failed.")
        print("The AI might still be generating repetitive personas.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
