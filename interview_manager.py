import uuid
from datetime import datetime
from typing import List, Dict, Any
import os
import json
import google.generativeai as genai
from agents.utils import get_gemini_client

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
    
    # NEW ARCHITECTURE: Lean, Strategic Prompt for Topic Graph Generation
    prompt = f"""You are a meticulous AI Interview Architect. Your role is to design a structured, machine-readable blueprint for a hyper-realistic interview simulation. You will not generate the questions themselves, but rather the logical flow and key topics for the Persona Agent to use.

**CONTEXT:**
- Role: {role}
- Seniority: {seniority}
- Core Skills to Assess: {', '.join(skills)}

**PRIMARY DIRECTIVE:**
Generate a topic graph for a single, cohesive interview session. This graph must be structured around a central, realistic case study or project scenario appropriate for the candidate's role and seniority.

**DESIGN PRINCIPLES:**
1.  **Narrative First**: Start by creating a brief, engaging scenario that will serve as the backdrop for the entire interview. This makes the interview feel like a real project discussion, not a random quiz.
2.  **Topic Granularity**: Break down each primary skill into specific, assessable topics. Each topic should represent a single conversational turn or a small set of related probes.
3.  **Logical Dependencies**: Structure the topics in a logical sequence. A foundational topic must appear before an advanced one that depends on it.
4.  **Actionable Keywords**: For each topic, provide a set of concrete keywords. These keywords are the direct input for the Persona Agent to generate its specific questions. They are the bridge between your plan and the live interview.
5.  **Efficiency**: Your output is a blueprint for another AI. Be concise. Avoid conversational filler and long descriptions.

**OUTPUT SCHEMA:**
Your response MUST be a single, valid JSON object, enclosed within <JSON_OUTPUT> tags. Adhere strictly to this schema:

<JSON_OUTPUT>
{{
  "session_narrative": "A brief, 1-2 sentence project scenario to provide context for the entire interview. (e.g., 'Your team is tasked with designing a new feature for our e-commerce platform to provide personalized recommendations to users.')",
  "topic_graph": [
    {{
      "topic_id": "<unique_id_string_for_this_topic, e.g., 'PM_01_Problem_Definition'>",
      "primary_skill": "<The main skill this topic assesses, from the user's list>",
      "topic_name": "<A short, descriptive name for this topic, e.g., 'Defining User Personas'>",
      "goal": "<A concise (under 10 words) description of the signal you are trying to capture, e.g., 'Assess structured thinking in problem framing.'>",
      "dependencies": ["<list of topic_ids that must precede this one, or an empty list []>"],
      "keywords_for_persona_agent": ["<keyword1>", "<keyword2>", "<keyword3>"]
    }}
  ]
}}
</JSON_OUTPUT>

Generate the interview blueprint now."""

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
            
            # Legacy metadata for backward compatibility
            "ai_generated_metadata": {
                "overall_approach": f"Structured interview with {len(goals)} topics",
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
        "covered_topic_ids": interview_plan.get("covered_topic_ids", [])
    }
