from celery import Celery
import os
import json
import redis
from typing import Dict, Any, List

# Import agent functions
from agents.evaluation import evaluate_answer
from agents.persona import generate_ai_question

# Get the Redis URL from environment variables, defaulting to localhost
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create the Celery instance
celery = Celery(
    __name__,
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Create Redis client for synchronous operations
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@celery.task
def orchestrate_next_turn(session_id: str, user_answer: str) -> Dict[str, Any]:
    """
    Orchestrator task that manages the interview flow.
    
    This task runs completely in the background and contains the main application logic.
    It ensures the user's interface remains fast and responsive.
    
    Args:
        session_id (str): The session ID to identify which interview to work on
        user_answer (str): The user's answer to the previous question
    
    Returns:
        Dict[str, Any]: Result of the orchestration process
    """
    try:
        print(f"🎯 Starting orchestration for session {session_id}")
        
        # A. Fetch the Current State from Redis
        print("📥 Fetching current state from Redis...")
        
        # Get the interview plan
        plan_json = redis_client.get(f"plan:{session_id}")
        if not plan_json:
            error_msg = f"No interview plan found for session {session_id}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
        
        plan = json.loads(plan_json)
        print(f"✅ Retrieved interview plan with {len(plan.get('goals', []))} goals")
        
        # Get the conversation history
        history_json = redis_client.get(f"history:{session_id}")
        if not history_json:
            error_msg = f"No conversation history found for session {session_id}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
        
        conversation_history = json.loads(history_json)
        print(f"✅ Retrieved conversation history with {len(conversation_history)} turns")
        
        # B. Update the Conversation History
        print("📝 Updating conversation history with user's answer...")
        
        if not conversation_history:
            error_msg = "Conversation history is empty"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
        
        # Update the last turn's answer
        last_turn = conversation_history[-1]
        last_turn["answer"] = user_answer
        print(f"✅ Updated last turn with user's answer: {user_answer[:50]}...")
        
        # C. Call the Evaluation Agent
        print("🔍 Calling evaluation agent...")
        
        # Get the current goal from the plan
        current_goal = None
        for goal in plan.get("goals", []):
            if goal.get("status") == "pending":
                current_goal = goal
                break
        
        if not current_goal:
            error_msg = "No pending goals found in interview plan"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
        
        # Get the last question for context
        last_question = last_turn.get("question", "")
        
        # Evaluate the user's answer
        skills_to_assess = [current_goal.get("skill", "General")]
        evaluation_result = evaluate_answer(
            answer=user_answer,
            question=last_question,
            skills_to_assess=skills_to_assess
        )
        
        if "error" in evaluation_result:
            print(f"⚠️ Evaluation failed: {evaluation_result['error']}")
            # Continue with default scores to avoid breaking the flow
            evaluation_result = {
                "scores": {skill: {"score": 3, "feedback": "Evaluation unavailable"} for skill in skills_to_assess},
                "overall_score": 3,
                "overall_feedback": "Evaluation temporarily unavailable"
            }
        
        print(f"✅ Evaluation completed with overall score: {evaluation_result.get('overall_score', 'N/A')}")
        
        # D. Update the Interview Plan
        print("📊 Updating interview plan based on evaluation...")
        
        # Simple goal processing logic (from LLM code)
        if current_goal:
            score = evaluation_result.get("scores", {}).get(current_goal["skill"], {}).get("score", 0)
            if score >= 3:  # Consider a score of 3+ a successful probe
                current_goal["probes_needed"] -= 1
                print(f"✅ Decremented probes for {current_goal['skill']}: {current_goal['probes_needed'] + 1} -> {current_goal['probes_needed']}")
                
                if current_goal["probes_needed"] <= 0:
                    current_goal["status"] = "covered"
                    print(f"🎯 Goal '{current_goal['skill']}' marked as covered")
        
        # E. Determine the Next Action
        print("🎯 Determining next action...")
        
        # Simple goal determination logic (from LLM code)
        next_goal = next((g for g in plan.get("goals", []) if g.get("status") == "pending"), None)
        
        if not next_goal:
            # All goals are covered, interview is complete
            print("🎉 All interview goals have been covered!")
            new_ai_question = "Thank you, that concludes our interview. We will be in touch regarding the next steps."
        else:
            skill_name = next_goal.get("skill", "the required skills")
            instruction = f"The current goal is to assess '{skill_name}'. Ask a question related to this skill, considering the conversation history."
            print(f"🎯 Next target: {skill_name}")
        
        # F. Call the Persona Agent
        print("🎭 Generating next question with persona agent...")
        
        if not next_goal:
            # Interview is complete, question already set
            print("✅ Interview complete, using final message")
        else:
            # Generate question for pending goal
            persona = plan.get("persona", "Professional Interviewer")
            new_ai_question = generate_ai_question(
                persona=persona,
                instructions=instruction,
                history=conversation_history
            )
            
            if new_ai_question.startswith("Error:"):
                print(f"❌ Failed to generate question: {new_ai_question}")
                # Fallback question
                new_ai_question = f"Could you please elaborate on your experience with {skill_name}?"
            
            print(f"✅ Generated new question: {new_ai_question[:100]}...")
        
        # G. Save State and Publish the New Question
        print("💾 Saving updated state to Redis...")
        
        # Append new turn to history
        new_turn = {
            "question": new_ai_question,
            "answer": None,
            "timestamp": None,  # Will be set by the frontend
            "question_type": "follow_up"
        }
        conversation_history.append(new_turn)
        
        # Save updated plan and history back to Redis
        updated_plan_json = json.dumps(plan)
        updated_history_json = json.dumps(conversation_history)
        
        redis_client.set(f"plan:{session_id}", updated_plan_json, ex=3600)
        redis_client.set(f"history:{session_id}", updated_history_json, ex=3600)
        
        print("✅ Updated plan and history saved to Redis")
        
        # Publish the new question to the user's channel
        channel_name = f"channel:{session_id}"
        redis_client.publish(channel_name, new_ai_question)
        print(f"📢 New question published to channel: {channel_name}")
        
        # Return success result
        result = {
            "success": True,
            "session_id": session_id,
            "new_question": new_ai_question,
            "goals_remaining": len([g for g in plan.get("goals", []) if g.get("status") == "pending"]),
            "total_goals": len(plan.get("goals", [])),
            "evaluation_score": evaluation_result.get("overall_score", "N/A")
        }
        
        print(f"🎉 Orchestration completed successfully for session {session_id}")
        return result
        
    except Exception as e:
        error_msg = f"Orchestration failed for session {session_id}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}

# Optional: Keep the test task for verification
@celery.task
def my_test_task(x, y):
    result = x + y
    print(f"Task executed: {x} + {y} = {result}")
    return result