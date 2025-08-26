#!/usr/bin/env python3
"""
Test script for the Evaluation Agent
Run this to test the evaluate_answer function
"""

import os
from dotenv import load_dotenv
from agents.evaluation import evaluate_answer

# Load environment variables
load_dotenv()

def test_evaluation():
    """Test the evaluation agent with sample data"""
    
    # Sample question and answer
    question = "How would you design a system to handle 1 million concurrent users?"
    answer = """
    I would start by understanding the requirements and constraints. For 1 million concurrent users, 
    I'd need to consider scalability, reliability, and performance. I'd use a distributed architecture 
    with load balancers, multiple application servers, and a distributed database. I'd also implement 
    caching strategies and consider using CDNs for static content. The system would need horizontal 
    scaling capabilities and proper monitoring.
    """
    
    # Skills to assess
    skills_to_assess = ["Problem Framing", "System Design", "Scalability Thinking"]
    
    print("🧪 Testing Evaluation Agent...")
    print(f"Question: {question}")
    print(f"Answer: {answer[:100]}...")
    print(f"Skills to assess: {skills_to_assess}")
    print("\n" + "="*50 + "\n")
    
    try:
        # Call the evaluation function
        result = evaluate_answer(answer, question, skills_to_assess)
        
        if "error" in result:
            print(f"❌ Evaluation failed: {result['error']}")
            return
        
        print("✅ Evaluation successful!")
        print("\n📊 Results:")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}")
        print(f"Overall Feedback: {result.get('overall_feedback', 'N/A')}")
        
        print("\n📝 Individual Skill Scores:")
        for skill, details in result.get('scores', {}).items():
            score = details.get('score', 'N/A')
            feedback = details.get('feedback', 'N/A')
            print(f"  {skill}: {score}/5")
            print(f"    Feedback: {feedback}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")

if __name__ == "__main__":
    test_evaluation()
