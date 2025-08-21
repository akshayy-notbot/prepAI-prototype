# Interview Flow Debug Guide

## 🐛 Issue Description

**Problem**: After submitting the first answer in an interview, the AI doesn't respond with the next question.

**Symptoms**:
- User can start an interview and receive the first question
- User can submit an answer successfully (HTTP 202 response)
- The frontend shows "waiting for AI response" but never receives it
- Interview appears to hang indefinitely

## 🔍 Root Cause Analysis

The issue was in the **WebSocket endpoint implementation**. Here's what was happening:

1. **Frontend Flow**: 
   - User submits answer via `POST /api/submit-answer`
   - Backend returns 202 (Accepted) immediately
   - Frontend waits for WebSocket message with next question

2. **Backend Flow**:
   - `submit-answer` endpoint triggers Celery task `orchestrate_next_turn`
   - Celery task processes the answer and generates next question
   - Celery task publishes the question to Redis channel `channel:{session_id}`
   - **PROBLEM**: WebSocket endpoint wasn't listening to Redis channels

3. **The Gap**:
   - Messages were being published to Redis channels ✅
   - WebSocket connections were established ✅
   - But WebSocket wasn't subscribed to the Redis channels ❌
   - Result: AI responses never reached the frontend

## 🛠️ The Fix

### What Was Changed

**File**: `main.py` - WebSocket endpoint (`@app.websocket("/ws/{session_id}")`)

**Before**: WebSocket only handled direct client messages
**After**: WebSocket now:
- Subscribes to Redis channel `channel:{session_id}`
- Listens for messages from Celery tasks
- Forwards AI responses to connected clients
- Maintains both client and Redis message handling

### Key Changes Made

```python
# NEW: Redis pub/sub setup
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.from_url(redis_url)
pubsub = redis_client.pubsub()
channel_name = f"channel:{session_id}"
pubsub.subscribe(channel_name)

# NEW: Redis message handling in main loop
redis_message = pubsub.get_message(timeout=0.1)
if redis_message and redis_message['type'] == 'message':
    ai_question = redis_message['data'].decode('utf-8')
    await websocket.send_text(json.dumps({
        "type": "question",
        "content": ai_question,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }))
```

## 🧪 Testing the Fix

### Option 1: Use the Debug Test HTML

1. Open `interview_debug_test.html` in your browser
2. Click "Run All Tests" to run the automated test suite
3. Or manually test each step:
   - Test configuration
   - Start interview
   - Submit answer
   - Wait for AI response

### Option 2: Use the Python Test Script

```bash
# Install dependencies
pip install websockets requests redis

# Run the test
python test_websocket_fix.py
```

### Option 3: Use the Backend Debug Script

```bash
# Install dependencies
pip install requests redis

# Quick test (just backend health)
python debug_interview_flow.py quick

# Full test (complete interview flow)
python debug_interview_flow.py
```

## 🔧 Manual Testing Steps

1. **Start Interview**:
   ```bash
   curl -X POST "https://prepai-api.onrender.com/api/start-interview" \
     -H "Content-Type: application/json" \
     -d '{"role": "Product Manager", "seniority": "Senior", "skills": ["Product Sense"]}'
   ```

2. **Submit Answer**:
   ```bash
   curl -X POST "https://prepai-api.onrender.com/api/submit-answer" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "YOUR_SESSION_ID", "answer": "My answer here"}'
   ```

3. **Connect WebSocket** and wait for AI response

## 📊 Expected Test Results

### ✅ Success Case
- Interview starts successfully
- WebSocket connects and subscribes to Redis channel
- Answer submission returns HTTP 202
- AI response received via WebSocket within 10-30 seconds
- Next question appears in chat

### ❌ Failure Cases
- **WebSocket Connection Failed**: Check backend URL and CORS settings
- **Redis Connection Failed**: Check Redis configuration and environment variables
- **Answer Submission Failed**: Check backend health and API endpoints
- **No AI Response**: Check Celery task execution and Redis pub/sub

## 🚀 Deployment Notes

### For Local Development
1. Ensure Redis is running locally (`redis-server`)
2. Set `REDIS_URL=redis://localhost:6379/0` in environment
3. Start Celery worker: `celery -A celery_app worker --loglevel=info`

### For Production (Render)
1. Redis URL is automatically set by Render
2. Celery worker should be running as a separate service
3. WebSocket connections use the same domain as the API

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Errors**:
   - Check `REDIS_URL` environment variable
   - Verify Redis service is running
   - Check network connectivity

2. **Celery Task Failures**:
   - Check Celery worker logs
   - Verify Redis broker configuration
   - Check for Python import errors

3. **WebSocket Connection Issues**:
   - Verify CORS settings
   - Check WebSocket URL format
   - Ensure backend is accessible

4. **Message Not Received**:
   - Check Redis pub/sub logs
   - Verify channel naming convention
   - Check WebSocket subscription status

### Debug Commands

```bash
# Check Redis connection
redis-cli ping

# Monitor Redis channels
redis-cli monitor

# Check specific session data
redis-cli get "plan:YOUR_SESSION_ID"
redis-cli get "history:YOUR_SESSION_ID"

# Test Redis pub/sub manually
redis-cli subscribe "channel:YOUR_SESSION_ID"
```

## 📝 Additional Notes

- The fix maintains backward compatibility
- WebSocket still handles client messages for testing
- Redis channels are automatically cleaned up when sessions end
- The solution scales to multiple concurrent interviews

## 🎯 Next Steps

After confirming the fix works:

1. **Test in Production**: Deploy and test with real users
2. **Monitor Logs**: Watch for any Redis or WebSocket errors
3. **Performance**: Monitor WebSocket connection stability
4. **Error Handling**: Add more robust error handling if needed

---

**Status**: ✅ **FIXED** - WebSocket now properly listens to Redis channels for AI responses
**Test Status**: 🧪 **READY FOR TESTING** - Use the provided test tools to verify
