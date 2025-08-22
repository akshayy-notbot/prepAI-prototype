"""
Temperature Manager for Gemini API calls
Manages temperature settings based on task type and requirements
"""

from typing import Dict, Any
import google.generativeai as genai

class TemperatureManager:
    """Manages temperature settings for different AI tasks"""
    
    # Temperature presets for different task types
    TEMPERATURE_PRESETS = {
        "CLASSIFICATION": 0.3,      # Archetype selection, intent classification
        "EVALUATION": 0.2,          # Answer evaluation, scoring
        "CREATIVE_GENERATION": 0.8, # Case studies, unique scenarios
        "CONVERSATIONAL": 0.6,      # General conversation, follow-ups
        "TECHNICAL": 0.4,           # Technical explanations, factual content
        "BEHAVIORAL": 0.5,          # Behavioral questions, situational responses
        "ANALYSIS": 0.4,            # Problem analysis, strategic thinking
    }
    
    @classmethod
    def get_temperature(cls, task_type: str) -> float:
        """
        Get the appropriate temperature for a given task type
        
        Args:
            task_type (str): The type of task being performed
            
        Returns:
            float: The temperature value (0.0 to 1.0)
        """
        return cls.TEMPERATURE_PRESETS.get(task_type.upper(), 0.5)
    
    @classmethod
    def get_generation_config(cls, task_type: str, **kwargs) -> genai.types.GenerationConfig:
        """
        Get a GenerationConfig object with appropriate temperature for a task
        
        Args:
            task_type (str): The type of task being performed
            **kwargs: Additional generation parameters
            
        Returns:
            genai.types.GenerationConfig: Configured generation settings
        """
        temperature = cls.get_temperature(task_type)
        
        # Default generation config
        config = {
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Override with any provided kwargs
        config.update(kwargs)
        
        return genai.types.GenerationConfig(**config)
    
    @classmethod
    def get_model_with_config(cls, task_type: str, **kwargs):
        """
        Get a Gemini model configured with appropriate temperature for a task
        
        Args:
            task_type (str): The type of task being performed
            **kwargs: Additional model configuration
            
        Returns:
            genai.GenerativeModel: Configured model
        """
        import os
        
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        try:
            genai.configure(api_key=GOOGLE_API_KEY)
            
            # Get generation config for this task
            generation_config = cls.get_generation_config(task_type, **kwargs)
            
            # Create model with the config
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                generation_config=generation_config
            )
            
            return model
            
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {str(e)}")

# Convenience functions for common use cases
def get_classification_model():
    """Get a model optimized for classification tasks (temp 0.3)"""
    return TemperatureManager.get_model_with_config("CLASSIFICATION")

def get_creative_model():
    """Get a model optimized for creative generation (temp 0.8)"""
    return TemperatureManager.get_model_with_config("CREATIVE_GENERATION")

def get_conversational_model():
    """Get a model optimized for conversation (temp 0.6)"""
    return TemperatureManager.get_model_with_config("CONVERSATIONAL")

def get_evaluation_model():
    """Get a model optimized for evaluation (temp 0.2)"""
    return TemperatureManager.get_model_with_config("EVALUATION")
