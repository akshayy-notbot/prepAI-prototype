"""
InterviewSessionService - A Stateless Factory for Creating AI-Powered Interview Plans

This service acts as a factory that creates complete, packaged interview plans.
It does NOT manage live interview state - that responsibility belongs to the Persona Agent.

Core Responsibilities:
1. Receive user requirements (role, seniority, skills)
2. Orchestrate archetype selection
3. Load appropriate prompt templates
4. Generate complete interview plans using Gemini AI
5. Return packaged "interview-in-a-box" with session_id

Key Principles:
- Stateless: No persistent state management
- Factory Pattern: Creates and ships products
- Single Responsibility: Plan creation only
- No Live State: Persona Agent handles all runtime state
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
import os
import json
import google.generativeai as genai
from .archetype_selector import select_interview_archetype
from .temperature_manager import TemperatureManager


class InterviewSessionService:
    """
    A stateless factory service for creating AI-powered interview plans.
    
    This service creates complete interview plans and returns them to the client.
    It does not manage live interview state - that is handled by the Persona Agent
    using Redis for fast session state management.
    
    Architecture:
    - Factory: Creates interview plans
    - Stateless: No persistent state
    - Single Responsibility: Plan creation only
    - Clean Separation: Factory creates, Persona Agent operates
    """
    
    @staticmethod
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

    @staticmethod
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
            "MIXED": "prompts/case_study_prompt.txt"  # Default for MIXED, will be overridden if needed
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
            print(f"❌ Critical error: Prompt file {prompt_file} is missing. This is a critical configuration error.")
            raise FileNotFoundError(f"Prompt template file {prompt_file} is missing. This is a critical configuration error.")
        except Exception as e:
            print(f"❌ Error reading prompt file {prompt_file}: {e}")
            raise ValueError(f"Failed to read prompt file {prompt_file}: {e}")

    @staticmethod
    def create_interview_plan_with_ai(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
        """
        Create a dynamic, AI-generated interview plan based on user selections.
        This function acts as a factory that creates complete interview plans.
        
        Args:
            role (str): The role the user is interviewing for (e.g., "Product Manager", "Software Engineer")
            seniority (str): The seniority level (e.g., "Junior", "Senior", "Manager")
            skills (List[str]): List of skills the user wants to practice
        
        Returns:
            Dict[str, Any]: Complete interview plan with session_id, persona, AI-generated goals, and timing
            
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
            
            # Extract new enhanced fields
            confidence_score = archetype_result.get("confidence_score", 0.8)  # Default confidence
            suggested_focus = archetype_result.get("suggested_focus", "General Skills")
            
            print(f"✅ Selected archetype: {archetype} - {reasoning}")
            print(f"✅ Confidence score: {confidence_score}")
            print(f"✅ Suggested focus: {suggested_focus}")
            
            # Step 2: Load the appropriate prompt template
            print(f"📝 Loading prompt template for archetype: {archetype}")
            prompt_template = InterviewSessionService.load_prompt_template(archetype)
            print(f"🔍 Prompt template type: {type(prompt_template)}")
            print(f"🔍 Prompt template length: {len(prompt_template) if prompt_template else 'None'}")
            
            if not prompt_template:
                raise ValueError("Failed to load prompt template")
            
            # Validate prompt template format
            required_placeholders = ['{role}', '{seniority}', '{skills}', '{PRIMARY_FOCUS_SKILL}']
            missing_placeholders = []
            for placeholder in required_placeholders:
                if placeholder not in prompt_template:
                    missing_placeholders.append(placeholder)
            
            if missing_placeholders:
                print(f"⚠️ Warning: Prompt template missing required placeholders: {missing_placeholders}")
                print(f"🔍 Template preview: {prompt_template[:200]}...")
                # Don't fail here, but log the warning
            
            # Step 3: Format the prompt with user context
            # Ensure skills is a list and handle edge cases
            if not isinstance(skills, list):
                print(f"⚠️ Warning: skills parameter is not a list: {type(skills)}, value: {skills}")
                skills = [str(skills)] if skills else ["General Skills"]
            
            # Clean and validate skills
            cleaned_skills = []
            for skill in skills:
                if skill and isinstance(skill, str) and skill.strip():
                    cleaned_skills.append(skill.strip())
            
            if not cleaned_skills:
                cleaned_skills = ["General Skills"]
            
            print(f"🔍 Skills before formatting: {skills}")
            print(f"🔍 Cleaned skills: {cleaned_skills}")
            
            # Format the prompt with proper skills handling and PRIMARY_FOCUS_SKILL
            try:
                # Use a safer formatting approach that won't interfere with JSON examples
                prompt = prompt_template.replace('{role}', role)
                prompt = prompt.replace('{seniority}', seniority)
                prompt = prompt.replace('{skills}', ', '.join(cleaned_skills))
                prompt = prompt.replace('{PRIMARY_FOCUS_SKILL}', suggested_focus)
                
                # Validate that all placeholders were replaced
                if '{role}' in prompt or '{seniority}' in prompt or '{skills}' in prompt or '{PRIMARY_FOCUS_SKILL}' in prompt:
                    print(f"⚠️ Warning: Some placeholders may not have been replaced properly")
                    print(f"🔍 Remaining placeholders in prompt: {[p for p in ['{role}', '{seniority}', '{skills}', '{PRIMARY_FOCUS_SKILL}'] if p in prompt]}")
                
                print(f"🔍 Formatted prompt length: {len(prompt)}")
                print(f"🔍 PRIMARY_FOCUS_SKILL: {suggested_focus}")
            except Exception as format_error:
                print(f"❌ Error formatting prompt template: {format_error}")
                print(f"🔍 Prompt template: {prompt_template[:200]}...")
                print(f"🔍 Role: {role}, Seniority: {seniority}, Skills: {cleaned_skills}")
                print(f"🔍 PRIMARY_FOCUS_SKILL: {suggested_focus}")
                raise ValueError(f"Failed to format prompt template: {str(format_error)}")
            
            # Configure Gemini client
            try:
                print(f"🤖 Configuring Gemini client...")
                model = InterviewSessionService.get_gemini_client()
                print(f"✅ Gemini client configured successfully")
            except Exception as e:
                print(f"❌ Failed to configure Gemini API: {e}")
                # If we can't configure the Gemini API, this is a critical error
                raise ValueError(f"Failed to configure Gemini API: {str(e)}")

            # Call the Gemini API with temperature 0.8 for creativity and uniqueness
            print(f"🚀 Generating interview plan with temperature 0.8 for {archetype} archetype...")
            
            # Use temperature manager for creative generation (temp 0.8)
            print(f"🌡️ Getting model with CREATIVE_GENERATION config...")
            model = TemperatureManager.get_model_with_config("CREATIVE_GENERATION")
            print(f"✅ Model configured with temperature: {model}")
            
            # Add retry logic for wrong response types
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    print(f"📤 Sending prompt to Gemini API (attempt {attempt + 1}/{max_retries})...")
                    response = model.generate_content(prompt)
                    print(f"✅ Gemini API response received")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"⚠️ Attempt {attempt + 1} failed, retrying...")
            
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
            try:
                ai_generated_plan = json.loads(response_text)
                print(f"✅ JSON parsed successfully")
            except json.JSONDecodeError as json_error:
                print(f"❌ JSON decode error: {json_error}")
                print(f"🔍 Response text that failed to parse: {response_text[:500]}...")
                print(f"🔍 JSON error details: line {json_error.lineno}, column {json_error.colno}")
                print(f"🔍 JSON error message: {json_error.msg}")
                
                # Try to identify the specific issue
                if "', '" in response_text:
                    print(f"🔍 Detected potential string formatting issue with ', '")
                if "\\" in response_text:
                    print(f"🔍 Detected potential escape character issues")
                
                # If we can't parse the AI response, this is a critical error
                raise ValueError(f"Failed to parse AI response as JSON: {str(json_error)}")
            
            # Validate the structure
            if not isinstance(ai_generated_plan, dict):
                raise ValueError("Response is not a valid JSON object")
            
            # Check for required fields
            if "topic_graph" not in ai_generated_plan:
                raise ValueError("Response missing required topic_graph field")
            
            # Log the response type for debugging
            # The system now supports both case study and pure topic responses
            if "session_narrative" in ai_generated_plan and ai_generated_plan["session_narrative"] is not None:
                print(f"✅ AI generated a case study response with narrative")
                print(f"🔍 Session narrative preview: {str(ai_generated_plan['session_narrative'])[:200]}...")
            else:
                print(f"✅ AI generated a pure topic-based response")
            
            # Validate topic_graph is a list and not empty
            if not isinstance(ai_generated_plan["topic_graph"], list):
                raise ValueError("topic_graph must be a list")
            
            if len(ai_generated_plan["topic_graph"]) == 0:
                raise ValueError("topic_graph cannot be empty")
            
            print(f"✅ Response validation passed")
            
            # Log the AI response structure for debugging
            print(f"🔍 AI response keys: {list(ai_generated_plan.keys())}")
            print(f"🔍 AI response structure: {ai_generated_plan}")
            
            # Extract the topic graph and session narrative
            topic_graph = ai_generated_plan.get("topic_graph", [])
            session_narrative = ai_generated_plan.get("session_narrative", "")
            case_study_details = ai_generated_plan.get("case_study_details", None)
            
            # Handle null values from AI response
            if session_narrative is None:
                session_narrative = ""
            if case_study_details is None:
                case_study_details = {}
            
            print(f"🔍 Topic graph length: {len(topic_graph)}")
            print(f"🔍 Session narrative length: {len(session_narrative)}")
            
            # Validate that we have a meaningful topic graph
            if not topic_graph or len(topic_graph) == 0:
                raise ValueError("AI generated an empty topic graph")
            
            # Transform topic graph into our standardized format
            goals = []
            for topic in topic_graph:
                # Ensure topic is a dictionary and handle null values
                if not isinstance(topic, dict):
                    print(f"⚠️ Warning: Skipping invalid topic: {topic}")
                    continue
                    
                goals.append({
                    "topic_id": topic.get("topic_id", f"topic_{len(goals)}"),
                    "skill": topic.get("primary_skill", "Unknown Skill"),
                    "topic_name": topic.get("topic_name", "Unknown Topic"),
                    "description": topic.get("goal", ""),
                    "status": "pending",
                    "dependencies": topic.get("dependencies", []) if topic.get("dependencies") is not None else [],
                    "keywords": topic.get("probing_questions", []) if topic.get("probing_questions") is not None else [],  # ✅ Updated to use new field
                    "stage": topic.get("stage", "Problem Definition"),  # ✅ Added stage field
                    "probing_questions": topic.get("probing_questions", []) if topic.get("probing_questions") is not None else [],  # ✅ Added probing questions
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
                
                # NEW: Enhanced Archetype Information
                "archetype": archetype,
                "archetype_reasoning": reasoning,
                "archetype_confidence": confidence_score,
                "suggested_skill_focus": suggested_focus,
                "case_study_details": case_study_details,
                
                # NEW: Enhanced Case Study Features
                "dynamic_events": ai_generated_plan.get("dynamic_events", []),
                "interviewer_briefing_doc": ai_generated_plan.get("interviewer_briefing_doc", {}),
                
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

    @staticmethod
    def create_interview_plan(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
        """
        Wrapper function that calls the AI-powered plan generator.
        Maintains backward compatibility with existing code.
        """
        return InterviewSessionService.create_interview_plan_with_ai(role, seniority, skills)

    @staticmethod
    def get_initial_plan_summary(interview_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get the initial summary of the interview plan for display purposes.
        This function only provides the initial plan data, not live progress.
        
        Args:
            interview_plan (Dict[str, Any]): The interview plan
        
        Returns:
            Dict[str, Any]: Initial plan summary (no live state)
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
                "status": goal.get("status", "pending")  # Initial status only
            })
        
        return {
            "session_id": interview_plan.get("session_id"),
            "role": interview_plan.get("role"),
            "seniority": interview_plan.get("seniority"),
            "persona": interview_plan.get("persona"),
            "total_goals": interview_plan.get("total_goals", 0),
            "estimated_duration": interview_plan.get("estimated_duration_minutes", 0),
            "status": interview_plan.get("status"),
            "skills_breakdown": goals_by_skill,
            "session_narrative": interview_plan.get("session_narrative", ""),
            "current_topic_id": interview_plan.get("current_topic_id"),
            # NEW: Enhanced Archetype and case study information
            "archetype": interview_plan.get("archetype", "CASE_STUDY"),
            "archetype_reasoning": interview_plan.get("archetype_reasoning", ""),
            "archetype_confidence": interview_plan.get("archetype_confidence", 0.8),
            "suggested_skill_focus": interview_plan.get("suggested_skill_focus"),
            "case_study_details": interview_plan.get("case_study_details", None)
        }


# Backward compatibility functions (deprecated - use InterviewSessionService class methods)
def get_gemini_client():
    """Backward compatibility function - use InterviewSessionService.get_gemini_client()"""
    return InterviewSessionService.get_gemini_client()

def load_prompt_template(archetype: str) -> str:
    """Backward compatibility function - use InterviewSessionService.load_prompt_template()"""
    return InterviewSessionService.load_prompt_template(archetype)

def create_interview_plan_with_ai(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
    """Backward compatibility function - use InterviewSessionService.create_interview_plan_with_ai()"""
    return InterviewSessionService.create_interview_plan_with_ai(role, seniority, skills)

def create_interview_plan(role: str, seniority: str, skills: List[str]) -> Dict[str, Any]:
    """Backward compatibility function - use InterviewSessionService.create_interview_plan()"""
    return InterviewSessionService.create_interview_plan(role, seniority, skills)

def get_initial_plan_summary(interview_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Backward compatibility function - use InterviewSessionService.get_initial_plan_summary()"""
    return InterviewSessionService.get_initial_plan_summary(interview_plan)
