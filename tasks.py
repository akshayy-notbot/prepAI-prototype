# In tasks.py
import os
import json
from celery import Celery
import models
import google.generativeai as genai

# In tasks.py
import os

# Use the REDIS_URL from the environment, with a local default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)

# --- Configuration ---
# WARNING: Hardcoding keys is not secure for production.
# This is for local testing only.

# Comment out or delete the environment variable line:
# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') 

# Add your key directly here:
GOOGLE_API_KEY = "AIzaSyAx-lbk6L--IuSvKPSrSd6G1JzC-nKvPAg" 

genai.configure(api_key=GOOGLE_API_KEY)

# Configure Celery
celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@celery.task
def analyze_interview_task(interview_id: int, transcript: list):
    """
    This is the background task that runs the REAL AI analysis.
    """
    print(f"Starting REAL analysis for interview_id: {interview_id}")
    db = models.SessionLocal()
    
    try:
        interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Interview {interview_id} not found.")

        interview.status = 'generating-report'
        db.commit()

        # --- 1. Format the Transcript and Build the Master Prompt ---
        formatted_transcript = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in transcript])

        master_prompt = f"""
        You are an expert hiring manager at a FAANG company, specializing in Product Management. Your task is to analyze an interview transcript and provide a structured, objective evaluation based on a strict rubric. Do not be friendly or conversational; be an analytical evaluator.

        **INTERVIEW CONTEXT:**
        - Role: {interview.role}
        - Seniority: {interview.seniority}
        - Skills Tested: {', '.join(interview.skills)}

        **EVALUATION RUBRIC:**
        For each criterion below, provide a score from 1 (Poor) to 5 (Excellent) and a concise one-sentence justification for that score.
        1.  **Problem Framing:** Did the user clarify the goal and define a specific user segment?
        2.  **Solution Ideation:** Did the user generate multiple, creative ideas?
        3.  **Tradeoff Analysis:** Did the user discuss the pros and cons of their chosen solution?
        4.  **Metrics Definition:** Did the user define clear success metrics?

        **INTERVIEW TRANSCRIPT:**
        ---
        {formatted_transcript}
        ---

        **OUTPUT INSTRUCTIONS:**
        Your response MUST be a single, valid JSON object. Do not include any text before or after the JSON. The JSON object must follow this exact schema:
        {{
          "overall_summary": "A 2-3 sentence summary of the candidate's performance.",
          "scores": [
            {{"criterion": "Problem Framing", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Solution Ideation", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Tradeoff Analysis", "score": <integer>, "justification": "<string>"}},
            {{"criterion": "Metrics Definition", "score": <integer>, "justification": "<string>"}}
          ],
          "key_strengths": ["<A bullet point of a key strength>"],
          "areas_for_improvement": ["<A bullet point of a key area for improvement>"]
        }}
        """

        # --- 2. Call the LLM ---
        print("Calling Gemini API...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(master_prompt)
        
        # Clean up the response to get a pure JSON string
        json_response_text = response.text.strip().replace('```json', '').replace('```', '')

        # --- 3. Save the Results ---
        # Parse the JSON response from the LLM.
        report_data = json.loads(json_response_text)
        print("Successfully parsed report from Gemini.")

        # In a full application, you would save this 'report_data' to a 'reports' table.
        # For now, we'll store it in the Interview model's 'skills' JSON field as a hack.
        # NOTE: This is a temporary solution for the MVP.
        interview.skills = report_data # Re-using the skills field to store the report

        # --- 4. Update Status ---
        interview.status = 'report-ready'
        db.commit()
        print(f"Analysis complete for interview_id: {interview_id}. Report is ready.")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        if 'interview' in locals() and interview:
            interview.status = 'failed'
            db.commit()
    finally:
        db.close()

    return {"status": "complete", "interview_id": interview_id}