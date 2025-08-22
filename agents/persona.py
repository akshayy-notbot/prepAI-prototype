import os
import json
import time
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
import redis
from datetime import datetime
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

def get_redis_client():
    """Get configured Redis client"""
    try:
        redis_url = os.environ.get('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
        return redis.from_url(redis_url, decode_responses=True)
    except Exception as e:
        raise ValueError(f"Failed to configure Redis: {str(e)}")

# --- NEW ARCHITECTURE: Two-Prompt System ---

class RouterAgent:
    """
    Fast, efficient conductor that analyzes user responses and determines next actions.
    Target: P95 Latency < 750ms
    """
    
    def __init__(self):
        self.model = get_gemini_client()
    
    def analyze_response(self, 
                        interviewer_persona_summary: str,
                        current_topic_goal: str,
                        conversation_history: List[Dict[str, Any]],
                        user_latest_answer: str) -> Dict[str, Any]:
        """
        Analyze user's response and determine the immediate next action.
        This is the fast, lightweight classifier that runs on every turn.
        """
        
        start_time = time.time()
        
        # Craft the ultra-efficient Router prompt
        prompt = f"""You are an ultra-efficient AI state analyzer for an interview simulation. Your sole purpose is to analyze the user's latest response and determine the immediate next action required. You are a classifier, not a conversationalist.

**CONTEXT:**
- Interviewer Persona: {interviewer_persona_summary}
- Current Topic Goal: "{current_topic_goal}"
- Conversation History (Last 2 turns): {conversation_history}
- User's Latest Answer: "{user_latest_answer}"

**YOUR TASK:**
Analyze the user's response. Is it a direct attempt to answer your question, or is it a clarifying question back to you? Based on this, decide if the topic goal has been achieved and what the immediate next action should be.

**CRITICAL INSTRUCTIONS:**
- Do NOT generate any interview questions or conversational text.
- Your response MUST be a single, valid JSON object and nothing else.
- Be extremely fast and efficient.
- **IMPORTANT**: If the user asks a question (e.g., "Can you tell me more about...", "What do you mean by...", "I'm not sure I understand..."), classify this as ANSWER_CLARIFICATION.

**OUTPUT SCHEMA:**
{{
  "analysis_summary": "A 5-10 word summary of the user's response.",
  "goal_achieved": <true or false, based on whether they answered the question>,
  "next_action": "<Choose ONE: 'ACKNOWLEDGE_AND_TRANSITION' | 'GENERATE_FOLLOW_UP' | 'REDIRECT_TO_TOPIC' | 'ANSWER_CLARIFICATION'>"
}}

Analyze the user's response and provide the JSON output now."""

        try:
            # Call the Gemini API for fast classification
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse the JSON response
            result = json.loads(response_text.strip())
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Add performance metrics
            result["router_latency_ms"] = round(latency_ms, 2)
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            # Fallback response in case of API failure
            return {
                "analysis_summary": "Error analyzing response",
                "goal_achieved": False,
                "next_action": "GENERATE_FOLLOW_UP",
                "router_latency_ms": 0,
                "error": str(e),
                "timestamp": time.time()
            }

class GeneratorAgent:
    """
    Powerful, thoughtful interviewer that crafts high-quality questions.
    Target: P95 Latency < 3 seconds
    """
    
    def __init__(self):
        self.model = get_gemini_client()
    
    def generate_response(self,
                         persona_role: str,
                         persona_company_context: str,
                         interview_style: str,
                         session_narrative: str,
                         case_study_details: Optional[Dict[str, Any]],
                         topic_graph_json: List[Dict[str, Any]],
                         current_topic_id: str,
                         covered_topic_ids: List[str],
                         conversation_history: List[Dict[str, Any]],
                         triggering_action: str) -> Dict[str, Any]:
        """
        Generate a high-quality, persona-driven response based on the Router's decision.
        This is the expensive, powerful model that's only called when needed.
        """
        
        start_time = time.time()
        
        # Craft the powerful Generator prompt
        prompt = f"""You are an elite-tier AI Interviewer. Your performance must be indistinguishable from a top human interviewer.

**1. YOUR PERSONA (Embody this completely):**
- Role: {persona_role}
- Company Context: {persona_company_context}
- Interview Style: {interview_style}

**2. THE MISSION CONTEXT (The Interview Plan):**
- Session Narrative: "{session_narrative}"
- Case Study Details (if available): {case_study_details}
- Full Topic Graph: {topic_graph_json}
- Session State: {{ "current_topic_id": "{current_topic_id}", "covered_topic_ids": {covered_topic_ids} }}

**3. CONVERSATION HISTORY:**
{conversation_history}

**4. YOUR IMMEDIATE TASK (Triggered by the Router):**
- Your required action is: **{triggering_action}**

**5. RULES OF ENGAGEMENT (Follow these meticulously):**
- **Be the Persona:** Your tone, phrasing, and the substance of your questions must perfectly match your assigned persona and the company context.
- **Navigate the Graph:** Your primary job is to guide the candidate through the `topic_graph`.
- **Ask Open-Ended Questions:** Do not ask trivia. Probe for the 'why' and 'how'. Focus on trade-offs and reasoning.
- **Be Dynamic:** Your questions should feel like natural follow-ups, not a pre-written script.

**EXECUTE YOUR TASK:**
Based on the `triggering_action`, generate your response.

- **IF `triggering_action` is 'START_INTERVIEW'**:
  Your response MUST have three parts, delivered as a single, natural monologue:
  1. A specific greeting: Introduce yourself and the company using the `companyName` from the `case_study_details`.
  2. Set the stage: IF a `session_narrative` exists, present it to the candidate.
  3. Ask the opening question based on the first topic in the graph.

- **IF `triggering_action` is 'ANSWER_CLARIFICATION'**:
  1. Consult the `case_study_details` JSON to find the relevant information to answer the user's question.
  2. Provide a concise, helpful answer based on the facts.
  3. Gently guide the conversation back by re-posing the original question. (e.g., "Does that give you enough context to start? I'm interested to hear your initial approach...").

- **IF `triggering_action` is 'ACKNOWLEDGE_AND_TRANSITION'**:
  Your response MUST have two parts: a brief closing statement for the previous topic and a transition to the next topic's question.

- **IF `triggering_action` is 'GENERATE_FOLLOW_UP'**:
  Ask a deeper, more probing question related to the `current_topic_id`.

- **IF `triggering_action` is 'REDIRECT_TO_TOPIC'**:
  Gently guide the user back to the current topic. Acknowledge their digression briefly then pivot.

**OUTPUT SCHEMA:**
Your response MUST be a single, valid JSON object.

{{
  "internal_thought": "A brief, one-sentence rationale for why you are asking this specific question. This is for system debugging.",
  "response_text": "The exact words you will say to the candidate. This will be converted to speech."
}}"""

        try:
            # Call the Gemini API for powerful question generation
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up the response
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse the JSON response
            result = json.loads(response_text.strip())
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Add performance metrics
            result["generator_latency_ms"] = round(latency_ms, 2)
            result["timestamp"] = time.time()
            
            return result
            
        except Exception as e:
            # Fallback response in case of API failure
            return {
                "internal_thought": "Error generating response, using fallback",
                "response_text": "I appreciate your response. Let me ask a follow-up question to better understand your approach.",
                "generator_latency_ms": 0,
                "error": str(e),
                "timestamp": time.time()
            }

# --- NEW ARCHITECTURE: Main Persona Agent Class ---

class PersonaAgent:
    """
    Main Persona Agent that orchestrates the two-prompt system and manages interview flow.
    All real-time state is managed in Redis only - no PostgreSQL writes during interviews.
    """
    
    def __init__(self):
        self.router_agent = RouterAgent()
        self.generator_agent = GeneratorAgent()
        self.redis_client = get_redis_client()
    
    def process_user_response(self, 
                            session_id: str,
                            user_answer: str,
                            topic_graph: List[Dict[str, Any]],
                            session_narrative: str,
                            interviewer_persona: str) -> Dict[str, Any]:
        """
        Main method that processes a user response using the two-prompt system.
        This is the core of the new architecture.
        """
        
        start_time = time.time()
        
        try:
            # Step 1: Get current session state from Redis (ONLY source of truth during interview)
            session_state = self._get_session_state(session_id)
            if not session_state:
                # Initialize new session state
                session_state = self._initialize_session_state(session_id, topic_graph)
            
            # Step 1.5: Get case study details from Redis (NEW: Case Study Knowledge Base)
            case_study_details = self._get_case_study_details(session_id)
            
            # Step 2: Get current topic information
            current_topic = self._get_current_topic(topic_graph, session_state["current_topic_id"])
            if not current_topic:
                raise ValueError(f"Current topic {session_state['current_topic_id']} not found in topic graph")
            
            # Step 3: Check if this is the first question (no conversation history)
            is_first_question = len(session_state.get("conversation_history", [])) == 0 and not user_answer
            
            if is_first_question:
                # For first question, use START_INTERVIEW action with GeneratorAgent
                generator_result = self.generator_agent.generate_response(
                    persona_role=interviewer_persona,
                    persona_company_context="Tech Company",
                    interview_style="Professional and engaging",
                    session_narrative=session_narrative,
                    case_study_details=case_study_details,  # NEW: Pass case study details
                    topic_graph_json=topic_graph,
                    current_topic_id=session_state["current_topic_id"],
                    covered_topic_ids=session_state.get("covered_topic_ids", []),
                    conversation_history=[],
                    triggering_action="START_INTERVIEW"
                )
                response_text = generator_result["response_text"]
                agent_used = "generator_start_interview"
                agent_latency = generator_result.get("generator_latency_ms", 0)
                
                # Update session state with the opening statement
                session_state = self._update_conversation_history(
                    session_id, 
                    session_state, 
                    "", 
                    response_text
                )
                
                # Save updated session state to Redis
                self._save_session_state(session_id, session_state)
                
                return {
                    "success": True,
                    "response_text": response_text,
                    "agent_used": agent_used,
                    "router_analysis": None,
                    "current_topic_id": session_state["current_topic_id"],
                    "covered_topic_ids": session_state.get("covered_topic_ids", []),
                    "total_latency_ms": round((time.time() - start_time) * 1000, 2),
                    "agent_latency_ms": agent_latency,
                    "session_id": session_id
                }
            
            # Step 4: Prepare conversation history for Router
            conversation_history = self._prepare_conversation_history(session_state.get("conversation_history", []))
            
            # Step 5: Router Agent Analysis (Fast - Target: < 750ms)
            router_result = self.router_agent.analyze_response(
                interviewer_persona_summary=interviewer_persona,
                current_topic_goal=current_topic.get("goal", ""),
                conversation_history=conversation_history,
                user_latest_answer=user_answer
            )
            
            # Step 6: Update session state based on Router analysis (Redis only)
            if router_result.get("goal_achieved", False):
                session_state = self._mark_topic_completed(session_id, session_state, current_topic["topic_id"])
                session_state = self._advance_to_next_topic(session_id, session_state, topic_graph)
            
            # Step 7: Generate response based on Router's decision
            if router_result["next_action"] in ["GENERATE_FOLLOW_UP", "ACKNOWLEDGE_AND_TRANSITION", "ANSWER_CLARIFICATION"]:
                # Use Generator Agent (Expensive - Target: < 3s)
                generator_result = self.generator_agent.generate_response(
                    persona_role=interviewer_persona,
                    persona_company_context="Tech Company",
                    interview_style="Professional and engaging",
                    session_narrative=session_narrative,
                    case_study_details=case_study_details,  # NEW: Pass case study details
                    topic_graph_json=topic_graph,
                    current_topic_id=session_state["current_topic_id"],
                    covered_topic_ids=session_state.get("covered_topic_ids", []),
                    conversation_history=conversation_history,
                    triggering_action=router_result["next_action"]
                )
                response_text = generator_result["response_text"]
                agent_used = "generator"
                agent_latency = generator_result.get("generator_latency_ms", 0)
            else:
                # Use simple logic for other actions
                response_text = self._generate_simple_response(router_result["next_action"], current_topic)
                agent_used = "simple_logic"
                agent_latency = 0
            
            # Step 8: Update session state with new conversation turn (Redis only)
            session_state = self._update_conversation_history(
                session_id, 
                session_state, 
                user_answer, 
                response_text
            )
            
            # Step 9: Save updated session state to Redis (ONLY Redis during interview)
            self._save_session_state(session_id, session_state)
            
            # Calculate total processing time
            total_latency_ms = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response_text": response_text,
                "agent_used": agent_used,
                "router_analysis": router_result,
                "current_topic_id": session_state["current_topic_id"],
                "covered_topic_ids": session_state.get("covered_topic_ids", []),
                "total_latency_ms": round(total_latency_ms, 2),
                "agent_latency_ms": agent_latency,
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_response": "I appreciate your response. Let me ask a follow-up question to better understand your approach.",
                "session_id": session_id
            }
    
    def _get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current session state from Redis (ONLY source of truth during interview)"""
        try:
            state_json = self.redis_client.get(f"session_state:{session_id}")
            return json.loads(state_json) if state_json else None
        except Exception:
            return None
    
    def _initialize_session_state(self, session_id: str, topic_graph: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initialize new session state for a fresh interview (Redis only)"""
        initial_state = {
            "current_topic_id": topic_graph[0]["topic_id"] if topic_graph else "topic_01",
            "covered_topic_ids": [],
            "conversation_history": [],
            "topic_progress": {},
            "router_agent_calls": 0,
            "generator_agent_calls": 0,
            "total_response_time_ms": 0,
            "created_at": time.time(),
            "last_updated": time.time()
        }
        
        # Initialize topic progress with qualitative markers (no numerical scoring)
        for topic in topic_graph:
            initial_state["topic_progress"][topic["topic_id"]] = {
                "status": "pending",
                "attempts": 0,
                "goal_achieved": False,
                "qualitative_markers": []  # Store specific observations, not scores
            }
        
        return initial_state
    
    def _get_current_topic(self, topic_graph: List[Dict[str, Any]], topic_id: str) -> Optional[Dict[str, Any]]:
        """Get current topic information from topic graph"""
        for topic in topic_graph:
            if topic["topic_id"] == topic_id:
                return topic
        return None
    
    def _prepare_conversation_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare conversation history for the agents (last 2-3 turns)"""
        if not history:
            return []
        
        # Take last 2-3 turns for context
        recent_history = history[-3:] if len(history) > 3 else history
        
        # Format for agent consumption
        formatted_history = []
        for turn in recent_history:
            formatted_history.append({
                "question": turn.get("question", ""),
                "answer": turn.get("answer", ""),
                "timestamp": turn.get("timestamp", "")
            })
        
        return formatted_history
    
    def _mark_topic_completed(self, session_id: str, session_state: Dict[str, Any], topic_id: str) -> Dict[str, Any]:
        """Mark a topic as completed and update progress with qualitative markers (Redis only)"""
        if topic_id not in session_state["covered_topic_ids"]:
            session_state["covered_topic_ids"].append(topic_id)
        
        if topic_id in session_state["topic_progress"]:
            session_state["topic_progress"][topic_id]["status"] = "completed"
            session_state["topic_progress"][topic_id]["goal_achieved"] = True
            # Store qualitative markers instead of numerical scores
            session_state["topic_progress"][topic_id]["qualitative_markers"] = []
        
        return session_state
    
    def _advance_to_next_topic(self, session_id: str, session_state: Dict[str, Any], topic_graph: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Advance to the next available topic based on dependencies (Redis only)"""
        current_topic_id = session_state["current_topic_id"]
        covered_topic_ids = session_state.get("covered_topic_ids", [])
        
        # Find next available topic
        for topic in topic_graph:
            if (topic["topic_id"] not in covered_topic_ids and 
                topic["topic_id"] != current_topic_id and
                self._can_start_topic(topic, covered_topic_ids)):
                
                session_state["current_topic_id"] = topic["topic_id"]
                break
        
        return session_state
    
    def _can_start_topic(self, topic: Dict[str, Any], covered_topic_ids: List[str]) -> bool:
        """Check if a topic can be started based on its dependencies"""
        dependencies = topic.get("dependencies", [])
        return all(dep in covered_topic_ids for dep in dependencies)
    
    def _generate_simple_response(self, action: str, current_topic: Dict[str, Any]) -> str:
        """Generate simple responses for non-question actions"""
        if action == "REDIRECT_TO_TOPIC":
            return f"That's an interesting point. Let's focus back on {current_topic.get('topic_name', 'the current topic')}. {current_topic.get('goal', '')}"
        elif action == "ANSWER_CLARIFICATION":
            return "I'm here to help clarify any questions you have about the interview process or the scenario we're discussing."
        else:
            return "Thank you for that response. Let me ask a follow-up question."
    
    def _update_conversation_history(self, session_id: str, session_state: Dict[str, Any], user_answer: str, ai_response: str) -> Dict[str, Any]:
        """Update conversation history with new turn (Redis only)"""
        new_turn = {
            "question": ai_response,
            "answer": user_answer,
            "timestamp": time.time()
        }
        
        if "conversation_history" not in session_state:
            session_state["conversation_history"] = []
        
        session_state["conversation_history"].append(new_turn)
        
        # Keep only last 10 turns to prevent memory bloat
        if len(session_state["conversation_history"]) > 10:
            session_state["conversation_history"] = session_state["conversation_history"][-10:]
        
        session_state["last_updated"] = time.time()
        return session_state
    
    def _save_session_state(self, session_id: str, session_state: Dict[str, Any]):
        """Save updated session state to Redis (ONLY Redis during interview)"""
        try:
            state_json = json.dumps(session_state)
            self.redis_client.set(f"session_state:{session_id}", state_json, ex=3600)  # Expire in 1 hour
        except Exception as e:
            print(f"Warning: Failed to save session state to Redis: {e}")
    
    def persist_final_state_to_postgresql(self, session_id: str, db_session) -> bool:
        """
        Persist final session state to PostgreSQL after interview completion.
        This is the ONLY time we write session state to the database.
        """
        try:
            # Get final state from Redis
            session_state = self._get_session_state(session_id)
            if not session_state:
                print(f"Warning: No session state found in Redis for {session_id}")
                return False
            
            # Import models here to avoid circular imports
            import models
            
            # Create or update SessionState record
            existing_state = db_session.query(models.SessionState).filter(
                models.SessionState.session_id == session_id
            ).first()
            
            if existing_state:
                # Update existing record
                existing_state.final_current_topic_id = session_state["current_topic_id"]
                existing_state.final_covered_topic_ids = session_state.get("covered_topic_ids", [])
                existing_state.final_conversation_history = session_state.get("conversation_history", [])
                existing_state.final_topic_progress = session_state.get("topic_progress", {})
                existing_state.total_router_agent_calls = session_state.get("router_agent_calls", 0)
                existing_state.total_generator_agent_calls = session_state.get("generator_agent_calls", 0)
                existing_state.total_response_time_ms = session_state.get("total_response_time_ms", 0)
                existing_state.interview_completed_at = datetime.utcnow()
            else:
                # Create new record
                final_state = models.SessionState(
                    session_id=session_id,
                    final_current_topic_id=session_state["current_topic_id"],
                    final_covered_topic_ids=session_state.get("covered_topic_ids", []),
                    final_conversation_history=session_state.get("conversation_history", []),
                    final_topic_progress=session_state.get("topic_progress", {}),
                    total_router_agent_calls=session_state.get("router_agent_calls", 0),
                    total_generator_agent_calls=session_state.get("generator_agent_calls", 0),
                    total_response_time_ms=session_state.get("total_response_time_ms", 0),
                    interview_completed_at=datetime.utcnow()
                )
                db_session.add(final_state)
            
            db_session.commit()
            print(f"✅ Final session state persisted to PostgreSQL for session {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to persist final state to PostgreSQL: {e}")
            db_session.rollback()
            return False

    def _get_case_study_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get case study details from Redis for context-aware responses"""
        try:
            case_study_json = self.redis_client.get(f"case_study:{session_id}")
            if case_study_json:
                return json.loads(case_study_json)
            return None
        except Exception as e:
            print(f"Warning: Failed to retrieve case study details: {e}")
            return None


