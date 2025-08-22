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
    print(f"🔑 Getting Gemini API key from environment...")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        print(f"❌ GOOGLE_API_KEY environment variable not set")
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
        print(f"❌ GOOGLE_API_KEY is set to placeholder value")
        raise ValueError("GOOGLE_API_KEY is set to placeholder value. Please set your actual API key.")
    
    print(f"✅ GOOGLE_API_KEY found, length: {len(GOOGLE_API_KEY)}")
    
    try:
        print(f"🤖 Configuring Gemini API...")
        genai.configure(api_key=GOOGLE_API_KEY)
        print(f"✅ Gemini API configured successfully")
        
        print(f"🚀 Creating GenerativeModel instance...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        print(f"✅ GenerativeModel created successfully")
        
        if not model:
            print(f"❌ Failed to create Gemini model instance")
            raise ValueError("Failed to create Gemini model instance")
        
        print(f"✅ Gemini client ready")
        return model
    except Exception as e:
        print(f"❌ Failed to configure Gemini API: {e}")
        raise ValueError(f"Failed to configure Gemini API: {str(e)}")

def load_prompt_template(archetype: str) -> str:
    """
    Load the appropriate prompt template based on the interview archetype.
    
    Args:
        archetype (str): The interview archetype (CASE_STUDY, BEHAVIORAL_DEEP_DIVE, TECHNICAL_KNOWLEDGE_SCREEN, MIXED)
    
    Returns:
        str: The prompt template content
    """
    print(f"📝 Loading prompt template for archetype: {archetype}")
    
    prompt_file_map = {
        "CASE_STUDY": "prompts/case_study_prompt.txt",
        "BEHAVIORAL_DEEP_DIVE": "prompts/behavioral_prompt.txt", 
        "TECHNICAL_KNOWLEDGE_SCREEN": "prompts/technical_knowledge_prompt.txt",
        "MIXED": "prompts/case_study_prompt.txt"  # Mixed uses case study as default
    }
    
    prompt_file = prompt_file_map.get(archetype, "prompts/case_study_prompt.txt")
    print(f"🔍 Selected prompt file: {prompt_file}")
    
    try:
        print(f"📖 Reading prompt file: {prompt_file}")
        with open(prompt_file, 'r') as f:
            template = f.read()
        print(f"✅ Prompt file read successfully, length: {len(template)}")
        
        if not template or template.strip() == "":
            raise ValueError(f"Prompt file {prompt_file} is empty")
        return template
    except FileNotFoundError:
        print(f"❌ Critical error: Prompt file {prompt_file} not found")
        raise FileNotFoundError(f"Prompt template file {prompt_file} is missing. This is a critical configuration error.")
    except Exception as e:
        print(f"❌ Error reading prompt file {prompt_file}: {e}")
        raise ValueError(f"Failed to read prompt file {prompt_file}: {e}")

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
        
    Raises:
        ValueError: If any step in the interview plan creation fails
        FileNotFoundError: If required prompt template files are missing
    """
    
    # Generate unique session ID for tracking
    session_id = str(uuid.uuid4())
    
    # Create timestamp for session start
    start_time = datetime.utcnow()
    
    try:
        # Step 1: Select Interview Archetype
        print(f"🎯 Selecting interview archetype for {role} at {seniority} level...")
        archetype_result = select_interview_archetype(role, seniority, skills)
        
        print(f"🔍 Archetype result: {type(archetype_result)}")
        if archetype_result:
            print(f"🔍 Archetype result keys: {list(archetype_result.keys()) if isinstance(archetype_result, dict) else 'Not a dict'}")
        
        # Validate archetype result
        if not archetype_result or "error" in archetype_result:
            error_msg = archetype_result.get("error", "Unknown error") if archetype_result else "No result returned"
            print(f"❌ Archetype selection failed: {error_msg}")
            raise ValueError(f"Failed to select interview archetype: {error_msg}")
        
        archetype = archetype_result["archetype"]
        reasoning = archetype_result["reasoning"]
        
        print(f"✅ Selected archetype: {archetype} - {reasoning}")
        
        # Step 2: Load the appropriate prompt template
        print(f"📝 Loading prompt template for archetype: {archetype}")
        prompt_template = load_prompt_template(archetype)
        print(f"🔍 Prompt template type: {type(prompt_template)}")
        print(f"🔍 Prompt template length: {len(prompt_template) if prompt_template else 'None'}")
        
        if not prompt_template:
            raise ValueError("Failed to load prompt template")
        
        # Step 3: Format the prompt with user context
        prompt = prompt_template.format(
            role=role,
            seniority=seniority,
            skills=', '.join(skills)
        )
        print(f"🔍 Formatted prompt length: {len(prompt)}")
        
        # Configure Gemini client
        try:
            print(f"🤖 Configuring Gemini client...")
            model = get_gemini_client()
            print(f"✅ Gemini client configured successfully")
        except Exception as e:
            print(f"❌ Failed to configure Gemini API: {e}")
            # If we can't configure the Gemini API, this is a critical error
            raise ValueError(f"Failed to configure Gemini API: {str(e)}")

        try:
            # Call the Gemini API with temperature 0.8 for creativity and uniqueness
            print(f"🚀 Generating interview plan with temperature 0.8 for {archetype} archetype...")
            
            # Use temperature manager for creative generation (temp 0.8)
            print(f"🌡️ Getting model with CREATIVE_GENERATION config...")
            model = TemperatureManager.get_model_with_config("CREATIVE_GENERATION")
            print(f"✅ Model configured with temperature: {model}")
            
            print(f"📤 Sending prompt to Gemini API...")
            response = model.generate_content(prompt)
            print(f"✅ Gemini API response received")
            
            response_text = response.text.strip()
            print(f"🔍 Raw response length: {len(response_text)}")
            print(f"🔍 Raw response preview: {response_text[:200]}...")
            
            # Clean up the response text
            # Remove markdown code fences if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
                print(f"🔍 Removed opening ```json")
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                print(f"🔍 Removed closing ```")
            
            response_text = response_text.strip()
            print(f"🔍 Cleaned response length: {len(response_text)}")
            
            # Extract JSON from <JSON_OUTPUT> tags if present
            if "<JSON_OUTPUT>" in response_text and "</JSON_OUTPUT>" in response_text:
                start_tag = response_text.find("<JSON_OUTPUT>") + len("<JSON_OUTPUT>")
                end_tag = response_text.find("</JSON_OUTPUT>")
                response_text = response_text[start_tag:end_tag].strip()
                print(f"🔍 Extracted JSON from <JSON_OUTPUT> tags")
            
            print(f"🔍 Final response text: {response_text[:200]}...")
            
            # Parse the JSON response
            print(f"🔍 Attempting to parse JSON...")
            ai_generated_plan = json.loads(response_text)
            print(f"✅ JSON parsed successfully")
            
            # Validate the structure
            if not isinstance(ai_generated_plan, dict):
                raise ValueError("Response is not a valid JSON object")
            
            if "topic_graph" not in ai_generated_plan:
                raise ValueError("Response missing required topic_graph field")
            
            print(f"✅ Response validation passed")
            
            # Extract the topic graph and session narrative
            topic_graph = ai_generated_plan.get("topic_graph", [])
            session_narrative = ai_generated_plan.get("session_narrative", "")
            case_study_details = ai_generated_plan.get("case_study_details", None)
            
            print(f"🔍 Topic graph length: {len(topic_graph)}")
            print(f"🔍 Session narrative length: {len(session_narrative)}")
            
            # Validate that we have a meaningful topic graph
            if not topic_graph or len(topic_graph) == 0:
                raise ValueError("AI generated an empty topic graph")
            
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
            
            print(f"🔍 Transformed goals length: {len(goals)}")
            
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
            
            print(f"✅ Interview plan assembled successfully")
            print(f"🔍 Final plan keys: {list(interview_plan.keys())}")
            
            return interview_plan
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"🔍 Response text that failed to parse: {response_text[:500]}...")
            # If we can't parse the AI response, this is a critical error
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error during plan generation: {e}")
            print(f"🔍 Error type: {type(e)}")
            print(f"🔍 Error details: {str(e)}")
            # If we get an unexpected error, this is a critical error
            raise ValueError(f"Unexpected error during plan generation: {str(e)}")
            
    except Exception as e:
        # Catch any other unexpected errors and ensure we always return a dictionary
        print(f"❌ Critical error in create_interview_plan_with_ai: {e}")
        print(f"🔍 Error type: {type(e)}")
        print(f"🔍 Error details: {str(e)}")
        # If we get a critical error, this is a critical error
        raise ValueError(f"Critical error during interview plan creation: {str(e)}")

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
