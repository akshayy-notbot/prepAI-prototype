import uuid
from datetime import datetime
from typing import List, Dict, Any
import os
import json
import google.generativeai as genai

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
    
    # Configure Gemini client
    try:
        model = get_gemini_client()
    except Exception as e:
        return {
            "error": f"Failed to configure Gemini API: {str(e)}",
            "session_id": session_id,
            "status": "failed"
        }
    
    # Craft the "meta-prompt" for the LLM
    # This is our instruction manual for creating bespoke interview plans
    prompt = f"""You are an expert interview strategist at a top tech company. Your job is to create a comprehensive, structured interview plan tailored to a specific role and skill set.

**INTERVIEW CONTEXT:**
- Role: {role}
- Seniority Level: {seniority}
- Skills to Practice: {', '.join(skills)}

**YOUR TASK:**
Create a detailed interview plan that will thoroughly assess the candidate's abilities in the selected skills. This plan should be realistic, challenging, and appropriate for the specified seniority level.

**PLAN REQUIREMENTS:**
1. **Skill Breakdown**: For each selected skill, identify 2-4 specific sub-skills or competencies that should be tested
2. **Question Strategy**: Determine how many questions/probes are needed for each sub-skill (typically 1-3)
3. **Difficulty Progression**: Structure questions to progress from foundational to advanced concepts
4. **Role-Specific Focus**: Ensure questions are relevant to the actual {role} role and {seniority} level
5. **Interview Flow**: Create a logical sequence that builds upon previous answers

**OUTPUT FORMAT:**
Your response MUST be a single, valid JSON object. Do not include any text before or after the JSON. The JSON object must follow this exact schema:

{{
  "interview_strategy": {{
    "overall_approach": "Brief description of the interview strategy and flow",
    "estimated_duration_minutes": <integer between 15-60>,
    "difficulty_progression": "beginner|intermediate|advanced|mixed"
  }},
  "skill_assessment_plan": [
    {{
      "primary_skill": "<skill name from user selection>",
      "sub_skills": [
        {{
          "name": "<specific sub-skill to test>",
          "description": "<what this sub-skill assesses>",
          "probes_needed": <integer 1-3>,
          "difficulty": "beginner|intermediate|advanced",
          "sample_question_types": ["<type 1>", "<type 2>"]
        }}
      ]
    }}
  ],
  "interviewer_persona": {{
    "role": "<specific interviewer role>",
    "company_context": "<company type/context>",
    "interview_style": "<professional style description>"
  }},
  "evaluation_criteria": {{
    "scoring_framework": "1-5 scale with specific criteria",
    "key_metrics": ["<metric 1>", "<metric 2>", "<metric 3>"],
    "success_indicators": ["<indicator 1>", "<indicator 2>"]
  }}
}}

**IMPORTANT GUIDELINES:**
- Be specific and realistic for the {seniority} {role} level
- Focus on practical, real-world scenarios they would encounter
- Ensure questions can be answered in 2-5 minutes each
- Make the plan challenging but fair for the specified seniority
- Consider industry best practices for {role} interviews
- Balance technical skills with soft skills as appropriate for the role

Generate your interview plan now:"""

    try:
        # Call the Gemini API
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response text
        # Remove markdown code fences if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse the JSON response
        ai_generated_plan = json.loads(response_text)
        
        # Validate the structure
        if not isinstance(ai_generated_plan, dict):
            raise ValueError("Response is not a valid JSON object")
        
        if "skill_assessment_plan" not in ai_generated_plan:
            raise ValueError("Response missing required skill_assessment_plan field")
        
        # Transform AI response into our standardized format
        goals = []
        for skill_section in ai_generated_plan.get("skill_assessment_plan", []):
            primary_skill = skill_section.get("primary_skill", "Unknown Skill")
            for sub_skill in skill_section.get("sub_skills", []):
                goals.append({
                    "skill": f"{primary_skill}: {sub_skill.get('name', 'Unknown')}",
                    "sub_skill": sub_skill.get('name', 'Unknown'),
                    "description": sub_skill.get('description', ''),
                    "status": "pending",
                    "probes_needed": sub_skill.get('probes_needed', 1),
                    "difficulty": sub_skill.get('difficulty', 'intermediate'),
                    "sample_question_types": sub_skill.get('sample_question_types', [])
                })
        
        # Assemble the final interview plan
        interview_plan = {
            "session_id": session_id,
            "persona": ai_generated_plan.get("interviewer_persona", {}).get("role", f"{seniority} {role}"),
            "role": role,
            "seniority": seniority,
            "skills": skills,
            "goals": goals,
            "start_time": start_time.isoformat(),
            "status": "planned",
            "total_goals": len(goals),
            "completed_goals": 0,
            "estimated_duration_minutes": ai_generated_plan.get("interview_strategy", {}).get("estimated_duration_minutes", len(goals) * 3),
            "ai_generated_metadata": {
                "overall_approach": ai_generated_plan.get("interview_strategy", {}).get("overall_approach", ""),
                "difficulty_progression": ai_generated_plan.get("interview_strategy", {}).get("difficulty_progression", "mixed"),
                "evaluation_criteria": ai_generated_plan.get("evaluation_criteria", {}),
                "interviewer_context": ai_generated_plan.get("interviewer_persona", {})
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
            "sub_skill": goal.get("sub_skill", ""),
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
        "overall_approach": interview_plan.get("ai_generated_metadata", {}).get("overall_approach", "")
    }
