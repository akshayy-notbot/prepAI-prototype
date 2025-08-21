# Interview Flow Debug Guide

## 🐛 Issue
After submitting the first answer in an interview, the AI doesn't respond with the next question.

## 🔍 Root Cause
The WebSocket endpoint wasn't listening to Redis channels where Celery tasks publish AI responses.

## 🛠️ Fix Applied
Updated `main.py` WebSocket endpoint to:
- Subscribe to Redis channel `channel:{session_id}`
- Listen for messages from Celery tasks
- Forward AI responses to connected clients

## 🧪 Testing Tools

### 1. HTML Debug Test
Open `interview_debug_test.html` in browser to test step-by-step.

### 2. Python Test Script
```bash
pip install websockets requests redis
python test_websocket_fix.py
```

### 3. Backend Debug Script
```bash
pip install requests redis
python debug_interview_flow.py
```

## 🔧 Manual Test
1. Start interview via API
2. Submit answer via API  
3. Connect WebSocket and wait for AI response
4. Should receive next question within 10-30 seconds

## 📊 Expected Results
- ✅ Interview starts
- ✅ WebSocket connects to Redis channel
- ✅ Answer submission accepted (HTTP 202)
- ✅ AI response received via WebSocket
- ✅ Next question appears in chat

## 🚀 Status
**FIXED** - WebSocket now properly listens to Redis channels
**READY FOR TESTING** - Use provided tools to verify
