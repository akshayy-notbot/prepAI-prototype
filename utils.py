import os
import google.generativeai as genai
import redis
from typing import Optional

# Lazy-initialized clients
_gemini_model = None
_redis_client = None

def get_gemini_client():
    """Get configured Gemini client with API key (lazy initialization)"""
    global _gemini_model
    
    if _gemini_model is None:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        if GOOGLE_API_KEY == "your_gemini_api_key_here" or GOOGLE_API_KEY == "paste_your_google_api_key_here":
            raise ValueError("GOOGLE_API_KEY is set to placeholder value. Please set your actual API key.")
        
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            _gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {str(e)}")
    
    return _gemini_model

def get_redis_client():
    """Get configured Redis client (lazy initialization)"""
    global _redis_client
    
    if _redis_client is None:
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url:
                raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
            _redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            raise ValueError(f"Failed to configure Redis: {str(e)}")
    
    return _redis_client
