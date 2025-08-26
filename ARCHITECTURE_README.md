# PrepAI New Architecture: Two-Loop System

## Overview

This document describes the new two-loop architecture that transforms PrepAI from a single-loop interview system to a sophisticated, performance-optimized interview platform with post-interview analysis capabilities.

## Architecture Overview

### **Part A: Initiation (Happens Once)**
```
User Input → Interview Manager → (Generates topic_graph) → Persists to DB → Persona Agent → (Fetches graph from DB/Cache) → Asks First Question
```

### **Part B: Real-Time Turn-by-Turn Loop (Repeats)**
```
User Answer → ⚡️ Router Agent → Determines 'next_action'
     ↓
IF next_action requires thoughtful question → 🔥 Generator Agent → Crafts Next Question → User
ELSE (simple acknowledgement) → Canned Response/Simple Logic → User
```

### **Part C: Post-Interview Analysis (Loop 2)**
```
Interview Ends → Analysis Orchestrator → Parallel Specialist Agents → Final Report → User
```

## Key Components

### 1. **Interview Manager** (`agents/interview_manager.py`)
- **Purpose**: Generates machine-readable topic_graph blueprints
- **Input**: Role, seniority, skills
- **Output**: Structured JSON with session_narrative and topic_graph
- **Key Feature**: Lean, strategic prompt that creates efficient blueprints for downstream agents

### 2. **Persona Agent** (`agents/persona.py`)
- **Main Class**: `PersonaAgent` - orchestrates the two-prompt system
- **Router Agent**: Fast classifier (Target: < 750ms P95 latency)
- **Generator Agent**: Powerful interviewer (Target: < 3s P95 latency)

### 3. **Database Schema** (`models.py`)
- **InterviewSession**: Enhanced with topic_graph and session state
- **SessionState**: Real-time state management
- **TopicGraph**: Reusable interview blueprints
- **AnalysisOrchestrator**: Post-interview analysis coordination
- **SpecialistAgent**: Individual analysis agents

## Performance Targets

### **Router Agent: The Conductor**
- **Target**: P95 Latency < 750 milliseconds
- **Purpose**: Fast response classification for fluid conversation
- **Usage**: Runs on every user response

### **Generator Agent: The Interviewer**
- **Target**: P95 Latency < 3 seconds
- **Purpose**: High-quality question generation
- **Usage**: Only when Router determines it's needed

## State Management Strategy

### **Redis-Only During Interviews**
- **Real-time state**: All session state, topic progress, and conversation history stored in Redis
- **Performance**: Sub-second response times with no database latency
- **Scalability**: Redis handles high-frequency writes during active interviews
- **Temporary**: State expires after 1 hour (configurable)

### **PostgreSQL for Final Audit**
- **Final state**: Session state persisted to database only after interview completion
- **Audit trail**: Complete record of interview flow and outcomes
- **Analytics**: Historical data for analysis and improvement
- **Permanent**: No data loss, complete interview records

## Database Schema Changes

### New Tables
1. **`interview_sessions`** - Enhanced with topic_graph and final state (not real-time)
2. **`session_states`** - Final session state for completed interviews only
3. **`topic_graphs`** - Reusable interview blueprints
4. **`analysis_orchestrators`** - Post-interview analysis coordination
5. **`specialist_agents`** - Individual analysis agent results

### Key Fields
- **`topic_graph`**: JSONB column storing the machine-readable interview blueprint
- **`session_narrative`**: Text column storing the project scenario backdrop
- **`final_current_topic_id`**: String tracking the final topic when interview ended
- **`final_covered_topic_ids`**: JSONB array of completed topics at interview end

### Qualitative Markers (No Numerical Scoring)
- **`qualitative_markers`**: Array of specific observations about candidate approach
- **Examples**: `["used_circles_framework", "identified_key_user_segment", "considered_tradeoffs"]`
- **Purpose**: Rich, actionable feedback instead of simplistic 1-5 scores
- **Alignment**: Supports the product's core differentiator of deep, qualitative analysis

## Implementation Details

### Topic Graph Structure
```json
{
  "session_narrative": "Brief project scenario description",
  "topic_graph": [
    {
      "topic_id": "PM_01_Problem_Definition",
      "primary_skill": "Problem Framing",
      "topic_name": "Defining User Personas",
      "goal": "Assess structured thinking in problem framing.",
      "dependencies": [],
      "keywords_for_persona_agent": ["user personas", "problem definition", "user research"]
    }
  ]
}
```

### Session State Management
```json
{
  "current_topic_id": "PM_02_User_Segmentation",
  "covered_topic_ids": ["PM_01_Problem_Definition"],
  "conversation_history": [last 3-4 turns],
  "topic_progress": {
    "PM_01_Problem_Definition": {
      "status": "completed", 
      "qualitative_markers": ["used_circles_framework", "identified_key_user_segment"]
    },
    "PM_02_User_Segmentation": {
      "status": "in_progress", 
      "attempts": 1,
      "qualitative_markers": []
    }
  }
}
```

**Important**: All real-time state management happens in Redis only. PostgreSQL is only written to after the interview completes for audit purposes.

## Setup Instructions

### 1. **Database Recreation**
```bash
# Run the database recreation script
python recreate_database.py
```

### 2. **Environment Variables**
Ensure these are set in your `.env` file:
```bash
DATABASE_URL=postgresql://username:password@localhost/database
GOOGLE_API_KEY=your_gemini_api_key
REDIS_URL=redis://localhost:6379/0
```

### 3. **Testing the New Architecture**
```bash
# Run the comprehensive test suite
python test_new_architecture.py
```

## API Endpoints

### **Start Interview** (`POST /api/start-interview`)
- Creates topic_graph and initializes session
- Returns first question and topic information

### **Submit Answer** (`POST /api/submit-answer`)
- Processes user response using new PersonaAgent system
- Returns next question with performance metrics

### **Get Status** (`GET /api/interview/{session_id}/status`)
- Returns current topic and progress information
- Includes topic_graph summary

## Benefits of New Architecture

### 1. **Performance**
- Fast Router Agent ensures sub-second response times
- Expensive Generator Agent only used when needed

### 2. **Scalability**
- Topic graph provides predictable, structured interview flow
- Clear separation between planning and execution

### 3. **Maintainability**
- Modular design with clear responsibilities
- Easy to modify interview structure without changing execution logic

### 4. **Auditability**
- Complete record of intended vs. actual interview flow
- Performance metrics for each agent type

### 5. **Cost Efficiency**
- Strategic use of expensive AI models
- Fast classification reduces overall API costs

## Migration from Legacy System

### **Backward Compatibility**
- Legacy functions maintained for smooth transition
- Fallback mechanisms ensure system reliability
- Gradual migration path available

### **Data Migration**
- New schema includes all legacy fields
- Existing data can be migrated using provided scripts
- No data loss during transition

## Error Handling

### **Graceful Degradation**
- Fallback to legacy system if new components fail
- Comprehensive error logging and monitoring
- User-friendly error messages

### **Performance Monitoring**
- Latency tracking for both agents
- Success/failure rate monitoring
- Automatic fallback triggers

## Future Enhancements

### **Phase 2: Analysis Orchestrator**
- Parallel specialist agent execution
- Comprehensive post-interview analysis
- Multi-faceted feedback generation

### **Phase 3: Advanced Topic Graphs**
- Dynamic topic generation based on user performance
- Adaptive difficulty adjustment
- Personalized interview paths

## Troubleshooting

### **Common Issues**

1. **Redis Connection Errors**
   - Verify REDIS_URL environment variable
   - Check Redis service status

2. **Database Schema Issues**
   - Run `recreate_database.py` to reset schema
   - Verify DATABASE_URL configuration

3. **Performance Issues**
   - Check Router Agent latency (< 750ms target)
   - Monitor Generator Agent usage patterns
   - Verify topic_graph structure

### **Debug Mode**
Enable detailed logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## Support

For issues or questions about the new architecture:
1. Check the test suite output
2. Review error logs in the console
3. Verify environment variable configuration
4. Run database recreation if schema issues persist

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Architecture**: Two-Loop System with Topic Graph Navigation
