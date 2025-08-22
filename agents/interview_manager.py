import uuid
from datetime import datetime
from typing import List, Dict, Any
import os
import json
import google.generativeai as genai
from .archetype_selector import select_interview_archetype
from .temperature_manager import TemperatureManager

# Configure Gemini API
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

def load_prompt_template(archetype: str) -> str:
    """
    Load the appropriate prompt template based on the interview archetype.
    
    Args:
        archetype (str): The interview archetype (CASE_STUDY, BEHAVIORAL_DEEP_DIVE, TECHNICAL_KNOWLEDGE_SCREEN, MIXED)
    
    Returns:
        str: The prompt template content
    """
    prompt_file_map = {
        "CASE_STUDY": "prompts/case_study_prompt.txt",
        "BEHAVIORAL_DEEP_DIVE": "prompts/behavioral_prompt.txt", 
        "TECHNICAL_KNOWLEDGE_SCREEN": "prompts/technical_knowledge_prompt.txt",
        "MIXED": "prompts/case_study_prompt.txt"  # Mixed uses case study as default
    }
    
    prompt_file = prompt_file_map.get(archetype, "prompts/case_study_prompt.txt")
    
    try:
        with open(prompt_file, 'r') as f:
            template = f.read()
        return template
    except FileNotFoundError:
        # Fallback to case study prompt if file not found
        print(f"Warning: Prompt file {prompt_file} not found, using case study prompt as fallback")
        try:
            with open("prompts/case_study_prompt.txt", 'r') as f:
                template = f.read()
            return template
        except FileNotFoundError:
            # Ultimate fallback - return a basic template
            return """You are an AI Interview Architect. Generate a topic graph for {role} at {seniority} level focusing on {skills}.

{{
  "session_narrative": "Interview scenario for {role} position",
  "case_study_details": null,
  "topic_graph": [
    {{
      "topic_id": "topic_1",
      "primary_skill": "{skills[0] if skills else 'General'}",
      "topic_name": "Skill Assessment",
      "question_pattern": "How would you approach {skills[0] if skills else 'this challenge'}?",
      "goal": "Assess understanding of {skills[0] if skills else 'the topic'}",
      "dependencies": [],
      "keywords_for_persona_agent": ["approach", "challenge", "understanding"]
    }}
  ]
}}"""

def create_interview_plan_with_ai(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
    """
    Create a dynamic, AI-generated interview plan based on user selections.
    This function uses the LLM to create bespoke, role-specific interview plans.
    
    Args:
        role (str): The role the user is interviewing for (e.g., "Product Manager", "Software Engineer")
        seniority (str): The seniority level (e.g., "Junior", "Senior", "Manager")
        skills (List[str]): List of skills the user wants to practice
    
    Returns:
        Dict[str, Any]: Complete interview plan with session ID, persona, AI-generated goals, and timing
    """
    
    # Generate unique session ID for tracking
    session_id = str(uuid.uuid4())
    
    # Create timestamp for session start
    start_time = datetime.utcnow()
    
    # Step 1: Select Interview Archetype
    print(f"🎯 Selecting interview archetype for {role} at {seniority} level...")
    archetype_result = select_interview_archetype(role, seniority, skills)
    
    if "error" in archetype_result:
        print(f"⚠️ Archetype selection failed: {archetype_result['error']}, using CASE_STUDY as fallback")
        archetype = "CASE_STUDY"
        reasoning = "Fallback due to archetype selection error"
    else:
        archetype = archetype_result["archetype"]
        reasoning = archetype_result["reasoning"]
    
    print(f"✅ Selected archetype: {archetype} - {reasoning}")
    
    # Step 2: Load the appropriate prompt template
    prompt_template = load_prompt_template(archetype)
    
    # Step 3: Format the prompt with user context
    prompt = prompt_template.format(
        role=role,
        seniority=seniority,
        skills=', '.join(skills)
    )
    
    # Configure Gemini client
    try:
        model = get_gemini_client()
    except Exception as e:
        return {
            "error": f"Failed to configure Gemini API: {str(e)}",
            "session_id": session_id,
            "status": "failed"
        }

    try:
        # Call the Gemini API with temperature 0.8 for creativity and uniqueness
        print(f"🚀 Generating interview plan with temperature 0.8 for {archetype} archetype...")
        
        # Use temperature manager for creative generation (temp 0.8)
        model = TemperatureManager.get_model_with_config("CREATIVE_GENERATION")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response text
        # Remove markdown code fences if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Extract JSON from <JSON_OUTPUT> tags if present
        if "<JSON_OUTPUT>" in response_text and "</JSON_OUTPUT>" in response_text:
            start_tag = response_text.find("<JSON_OUTPUT>") + len("<JSON_OUTPUT>")
            end_tag = response_text.find("</JSON_OUTPUT>")
            response_text = response_text[start_tag:end_tag].strip()
        
        # Parse the JSON response
        ai_generated_plan = json.loads(response_text)
        
        # Validate the structure
        if not isinstance(ai_generated_plan, dict):
            raise ValueError("Response is not a valid JSON object")
        
        if "topic_graph" not in ai_generated_plan:
            raise ValueError("Response missing required topic_graph field")
        
        # Extract the topic graph and session narrative
        topic_graph = ai_generated_plan.get("topic_graph", [])
        session_narrative = ai_generated_plan.get("session_narrative", "")
        case_study_details = ai_generated_plan.get("case_study_details", None)
        
        # Transform topic graph into our standardized format
        goals = []
        for topic in topic_graph:
            goals.append({
                "topic_id": topic.get("topic_id", f"topic_{len(goals)}"),
                "skill": topic.get("primary_skill", "Unknown Skill"),
                "topic_name": topic.get("topic_name", "Unknown Topic"),
                "description": topic.get("goal", ""),
                "status": "pending",
                "dependencies": topic.get("dependencies", []),
                "keywords": topic.get("keywords_for_persona_agent", []),
                "probes_needed": 1,  # Default to 1 probe per topic
                "difficulty": "intermediate"  # Default difficulty
            })
        
        # Assemble the final interview plan with new architecture
        interview_plan = {
            "session_id": session_id,
            "persona": f"{seniority} {role} Interviewer",  # Default persona
            "role": role,
            "seniority": seniority,
            "skills": skills,
            "goals": goals,
            "start_time": start_time.isoformat(),
            "status": "ready",  # New status for new architecture
            "total_goals": len(goals),
            "completed_goals": 0,
            "estimated_duration_minutes": len(goals) * 3,  # 3 minutes per topic
            
            # NEW ARCHITECTURE: Topic Graph Data
            "topic_graph": topic_graph,
            "session_narrative": session_narrative,
            "current_topic_id": goals[0]["topic_id"] if goals else None,
            "covered_topic_ids": [],
            
            # NEW: Archetype Information
            "archetype": archetype,
            "archetype_reasoning": reasoning,
            "case_study_details": case_study_details,
            
            # Legacy metadata for backward compatibility
            "ai_generated_metadata": {
                "overall_approach": f"Structured {archetype.lower().replace('_', ' ')} interview with {len(goals)} topics",
                "difficulty_progression": "mixed",
                "evaluation_criteria": {},
                "interviewer_context": {"role": f"{seniority} {role}"}
            }
        }
        
        return interview_plan
        
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse AI response as JSON: {str(e)}",
            "raw_response": response_text if 'response_text' in locals() else "No response received",
            "session_id": session_id,
            "status": "failed"
        }
    except Exception as e:
        return {
            "error": f"Unexpected error during plan generation: {str(e)}",
            "session_id": session_id,
            "status": "failed"
        }

def create_interview_plan(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
    """
    Wrapper function that calls the AI-powered plan generator.
    Maintains backward compatibility with existing code.
    """
    return create_interview_plan_with_ai(role, seniority, skills)

def update_goal_status(interview_plan: Dict[str, Any], skill: str, new_status: str) -> Dict[str, Any]:
    """
    Update the status of a specific goal in the interview plan.
    
    Args:
        interview_plan (Dict[str, Any]): The current interview plan
        skill (str): The skill to update
        new_status (str): The new status (e.g., "in_progress", "completed", "failed")
    
    Returns:
        Dict[str, Any]: Updated interview plan
    """
    
    for goal in interview_plan.get("goals", []):
        if goal.get("skill") == skill:
            goal["status"] = new_status
            break
    
    # Update completion count
    completed_count = sum(1 for goal in interview_plan.get("goals", []) if goal.get("status") == "completed")
    interview_plan["completed_goals"] = completed_count
    
    # Update overall status if all goals are completed
    if completed_count == len(interview_plan.get("goals", [])) and completed_count > 0:
        interview_plan["status"] = "completed"
    
    return interview_plan

def get_plan_summary(interview_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of the interview plan for display purposes.
    
    Args:
        interview_plan (Dict[str, Any]): The interview plan
    
    Returns:
        Dict[str, Any]: Summary information
    """
    
    if "error" in interview_plan:
        return {"error": interview_plan["error"], "status": "failed"}
    
    goals_by_skill = {}
    for goal in interview_plan.get("goals", []):
        primary_skill = goal.get("skill", "").split(": ")[0] if ": " in goal.get("skill", "") else goal.get("skill", "")
        if primary_skill not in goals_by_skill:
            goals_by_skill[primary_skill] = []
        goals_by_skill[primary_skill].append({
            "topic_id": goal.get("topic_id", ""),
            "topic_name": goal.get("topic_name", ""),
            "difficulty": goal.get("difficulty", ""),
            "probes_needed": goal.get("probes_needed", 1),
            "status": goal.get("status", "pending")
        })
    
    return {
        "session_id": interview_plan.get("session_id"),
        "role": interview_plan.get("role"),
        "seniority": interview_plan.get("seniority"),
        "persona": interview_plan.get("persona"),
        "total_goals": interview_plan.get("total_goals", 0),
        "completed_goals": interview_plan.get("completed_goals", 0),
        "estimated_duration": interview_plan.get("estimated_duration_minutes", 0),
        "status": interview_plan.get("status"),
        "skills_breakdown": goals_by_skill,
        "session_narrative": interview_plan.get("session_narrative", ""),
        "current_topic_id": interview_plan.get("current_topic_id"),
        "covered_topic_ids": interview_plan.get("covered_topic_ids", []),
        # NEW: Archetype and case study information
        "archetype": interview_plan.get("archetype", "CASE_STUDY"),
        "archetype_reasoning": interview_plan.get("archetype_reasoning", ""),
        "case_study_details": interview_plan.get("case_study_details", None)
    }
