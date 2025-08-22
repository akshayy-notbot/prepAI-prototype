import os
import json
import google.generativeai as genai
from typing import Dict, Any
from .temperature_manager import TemperatureManager

def get_gemini_client():
    """Get configured Gemini client with API key"""
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
        raise ValueError("GOOGLE_API_KEY is set to placeholder value. Please set your actual API key.")
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model
    except Exception as e:
        raise ValueError(f"Failed to configure Gemini API: {str(e)}")

def select_interview_archetype(role: str, seniority: str, skills: list) -> Dict[str, Any]:
    """
    Analyze user input and determine the most appropriate interview archetype.
    
    Args:
        role (str): The role the user is interviewing for
        seniority (str): The seniority level
        skills (list): List of skills the user wants to practice
    
    Returns:
        Dict[str, Any]: Contains archetype and reasoning
    """
    
    try:
        # Use temperature manager for consistent classification (temp 0.3)
        print(f"🌡️ Getting model with CLASSIFICATION config...")
        model = TemperatureManager.get_model_with_config("CLASSIFICATION")
        print(f"✅ Model configured successfully")
    except Exception as e:
        print(f"❌ Failed to configure Gemini API: {e}")
        # If we can't even configure the API, this is a critical error
        raise ValueError(f"Failed to configure Gemini API for archetype selection: {str(e)}")
    
    prompt = f"""You are an expert AI career coach and interview planner. Your job is to analyze a user's career goals and the skills they want to practice to determine the most effective interview format for them.

**USER PROFILE:**
- Role: {role}
- Seniority: {seniority}
- Skills to Practice: {', '.join(skills)}

**DECISION FRAMEWORK:**
- Use a 'CASE_STUDY' for roles and skills that require problem-solving in a hypothetical business context (e.g., Product Management, System Design, Go-to-Market Strategy).
- Use a 'BEHAVIORAL_DEEP_DIVE' for skills related to leadership, teamwork, and past experiences (e.g., Stakeholder Management, Conflict Resolution, Project Ownership). This is common for all senior roles.
- Use a 'TECHNICAL_KNOWLEDGE_SCREEN' for skills that test specific, factual knowledge (e.g., Data Structures, API Design, SQL).
- If the skills are a clear mix (e.g., 'System Design' and 'Team Leadership'), you can select a 'MIXED' archetype.

**YOUR TASK:**
Based on the user's profile and the decision framework, select the single most appropriate interview archetype.

**OUTPUT SCHEMA:**
Your response MUST be a single, valid JSON object and nothing else.

{{
  "archetype": "<Choose ONE: 'CASE_STUDY' | 'BEHAVIORAL_DEEP_DIVE' | 'TECHNICAL_KNOWLEDGE_SCREEN' | 'MIXED'>",
  "reasoning": "A brief, one-sentence explanation for your choice."
}}"""

    try:
        # Call the Gemini API with temperature 0.3 for consistent classification
        print(f"📤 Sending archetype selection prompt to Gemini API...")
        response = model.generate_content(prompt)
        print(f"✅ Gemini API response received")
        
        response_text = response.text.strip()
        print(f"🔍 Raw response length: {len(response_text)}")
        print(f"🔍 Raw response preview: {response_text[:200]}...")
        
        # Clean up the response text
        if response_text.startswith("```json"):
            response_text = response_text[7:]
            print(f"🔍 Removed opening ```json")
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            print(f"🔍 Removed closing ```")
        
        response_text = response_text.strip()
        print(f"🔍 Cleaned response length: {len(response_text)}")
        
        # Parse the JSON response
        print(f"🔍 Attempting to parse JSON...")
        result = json.loads(response_text.strip())
        print(f"✅ JSON parsed successfully")
        
        # Validate the structure
        if not isinstance(result, dict):
            raise ValueError("Response is not a valid JSON object")
        
        if "archetype" not in result:
            raise ValueError("Response missing required archetype field")
        
        print(f"✅ Archetype selection successful: {result['archetype']}")
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in archetype selection: {e}")
        print(f"🔍 Response text that failed to parse: {response_text[:500]}...")
        # If we can't parse the AI response, this is a critical error
        raise ValueError(f"Failed to parse AI response as JSON in archetype selection: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error during archetype selection: {e}")
        print(f"🔍 Error type: {type(e)}")
        print(f"🔍 Error details: {str(e)}")
        # If we get an unexpected error, this is a critical error
        raise ValueError(f"Unexpected error during archetype selection: {str(e)}")
