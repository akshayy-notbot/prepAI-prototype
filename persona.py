import os
import json
import google.generativeai as genai
from typing import List, Dict, Any

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

def generate_ai_question(persona: str, instructions: str, history: List[Dict[str, Any]]) -> str:
    """
    Generate an AI interviewer question based on persona, instructions, and conversation history.
    
    Args:
        persona (str): The interviewer persona (e.g., "Senior Product Manager at Google")
        instructions (str): Specific instructions from the orchestrator (e.g., "Ask a follow-up about tradeoffs")
        history (List[Dict[str, Any]]): List of conversation turns with 'question' and 'answer' keys
    
    Returns:
        str: The generated question text
    """
    
    # Configure Gemini client
    try:
        model = get_gemini_client()
    except Exception as e:
        return f"Error: Unable to generate question due to API configuration failure: {str(e)}"
    
    # Format conversation history for context
    conversation_context = ""
    if history:
        conversation_context = "**CONVERSATION HISTORY:**\n"
        for i, turn in enumerate(history, 1):
            question = turn.get('question', 'No question provided')
            answer = turn.get('answer', 'No answer provided')
            conversation_context += f"Turn {i}:\n"
            conversation_context += f"Interviewer: {question}\n"
            conversation_context += f"Candidate: {answer}\n\n"
    
    # Craft the persona prompt
    prompt = f"""You are an AI interviewer acting as a {persona} evaluating the user for this role.

{conversation_context}

**YOUR TASK:** {instructions}

**INTERVIEWER RULES:**
1. Ask only ONE question - be direct and professional
2. Maintain the tone and style of a {persona}
3. Ask questions that build upon the conversation history
4. Focus on the specific skills and competencies relevant to this role
5. Be challenging but fair - this is a professional interview
6. Keep questions clear and actionable
7. Do not repeat questions that have already been asked
8. Do not provide answers or hints - just ask the question

**OUTPUT:** Return ONLY the question text. Do not include any explanations, formatting, or additional text. Just the question itself.

Generate your question now:"""

    try:
        # Call the Gemini API
        response = model.generate_content(prompt)
        question_text = response.text.strip()
        
        # Clean up the response - remove any markdown or extra formatting
        if question_text.startswith('"') and question_text.endswith('"'):
            question_text = question_text[1:-1]  # Remove quotes if present
        
        # Remove any markdown code blocks
        if question_text.startswith('```'):
            lines = question_text.split('\n')
            question_text = '\n'.join(lines[1:-1])  # Remove first and last lines
        
        return question_text.strip()
        
    except Exception as e:
        return f"Error: Failed to generate question due to API error: {str(e)}"

def generate_follow_up_question(persona: str, last_answer: str, skills_focus: List[str]) -> str:
    """
    Generate a follow-up question based on the candidate's last answer and specific skills to focus on.
    
    Args:
        persona (str): The interviewer persona
        last_answer (str): The candidate's most recent answer
        skills_focus (List[str]): Skills to focus on in the follow-up
    
    Returns:
        str: The generated follow-up question
    """
    
    instructions = f"Ask a follow-up question that probes deeper into the candidate's response, focusing on these skills: {', '.join(skills_focus)}. Make it challenging and relevant to their previous answer."
    
    # Create a minimal history with just the last exchange
    history = [{"question": "Previous question", "answer": last_answer}]
    
    return generate_ai_question(persona, instructions, history)

def generate_skill_specific_question(persona: str, skill: str, difficulty: str = "intermediate") -> str:
    """
    Generate a question specifically designed to test a particular skill.
    
    Args:
        persona (str): The interviewer persona
        skill (str): The specific skill to test
        difficulty (str): Question difficulty level (beginner, intermediate, advanced)
    
    Returns:
        str: The generated skill-specific question
    """
    
    instructions = f"Generate a {difficulty}-level question specifically designed to test the candidate's {skill} abilities. Make it realistic and commonly asked in {persona} interviews."
    
    return generate_ai_question(persona, instructions, [])
