from agents.utils import get_gemini_client, get_redis_client
from agents.persona import (
    PersonaAgent,
    RouterAgent,
    GeneratorAgent
)
from agents.interview_manager import (
    create_interview_plan, 
    create_interview_plan_with_ai, 
    update_goal_status, 
    get_plan_summary
)

__all__ = [
    # Core utilities
    'get_gemini_client',
    'get_redis_client',
    
    # Interview Manager functions
    'create_interview_plan',
    'create_interview_plan_with_ai',
    'update_goal_status',
    'get_plan_summary',
    
    # NEW ARCHITECTURE: Persona Agent Classes
    'PersonaAgent',      # Main orchestrator class
    'RouterAgent',       # Fast classifier (Target: < 750ms)
    'GeneratorAgent'     # Powerful interviewer (Target: < 3s)
]
