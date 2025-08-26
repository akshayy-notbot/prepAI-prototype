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
    Analyze user input and determine the most appropriate interview archetype using expert heuristics.
    
    Args:
        role (str): The role the user is interviewing for
        seniority (str): The seniority level
        skills (list): List of skills the user wants to practice
    
    Returns:
        Dict[str, Any]: Contains archetype, confidence_score, reasoning, and suggested_focus
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
    
    prompt = f"""You are a Principal Recruiter and Interview Strategist from a top-tier tech company. You have decades of experience designing interview loops. Your expertise lies in analyzing a candidate's profile and desired skills to recommend the single most effective interview format to test their core abilities.

**USER PROFILE:**
- Role: {role}
- Seniority: {seniority}
- Skills to Practice: {', '.join(skills)}

**DECISION HEURISTICS (Your Guiding Principles):**
1.  **Primary Intent:** Your primary goal is to identify the user's core intent. Is this a practice session for a problem-solving loop, a behavioral screen, or a technical knowledge test?
2.  **Role and Seniority Weighting:** The user's `{role}` and `{seniority}` are strong signals.
    - Product and senior engineering roles often lean towards `CASE_STUDY` (System Design, Product Sense).
    - All senior and leadership roles require a strong behavioral component. If behavioral skills are listed alongside technical ones, consider which is the likely focus of the interview they are preparing for.
3.  **Skill Categorization:** Mentally categorize the listed skills.
    - **Problem-Solving Skills** (e.g., System Design, Go-to-Market Strategy, API Design) strongly suggest `CASE_STUDY`.
    - **Experience-Based Skills** (e.g., Leadership, Stakeholder Management, Conflict Resolution) strongly suggest `BEHAVIORAL_DEEP_DIVE`.
    - **Factual Knowledge Skills** (e.g., SQL, Data Structures, Algorithms) strongly suggest `TECHNICAL_KNOWLEDGE_SCREEN`.
4.  **The `MIXED` Archetype:** Only use the `MIXED` archetype if there is a clear and balanced demand for two distinct formats (e.g., a junior candidate asking for "Data Structures" and "Teamwork"). For senior roles, try to infer the primary format.

**YOUR TASK:**
Based on the user's profile and your expert heuristics, analyze the inputs and determine the single most effective interview archetype.
Provide a confidence score for your recommendation.
From the list of Skills to Practice, you must also identify the single most significant skill that should be the central theme of the interview.

**OUTPUT SCHEMA:**
Your response MUST be a single, valid JSON object and nothing else.

{{
  "archetype": "<Choose ONE: 'CASE_STUDY' | 'BEHAVIORAL_DEEP_DIVE' | 'TECHNICAL_KNOWLEDGE_SCREEN' | 'MIXED'>",
  "confidence_score": <A float between 0.0 and 1.0 representing your confidence in the chosen archetype>,
  "reasoning": "A brief, one-sentence explanation for your choice, justifying it based on the heuristics.",
  "suggested_focus": "Based on the skills, suggest the primary skill that the generated interview should focus on."
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
        
        # Validate new fields if present
        if "confidence_score" in result:
            confidence = result["confidence_score"]
            if not isinstance(confidence, (int, float)) or confidence < 0.0 or confidence > 1.0:
                print(f"⚠️ Warning: confidence_score {confidence} is not a valid float between 0.0 and 1.0")
        
        if "suggested_focus" in result:
            print(f"✅ Suggested focus: {result['suggested_focus']}")
        
        print(f"✅ Archetype selection successful: {result['archetype']}")
        if "confidence_score" in result:
            print(f"✅ Confidence score: {result['confidence_score']}")
        
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
