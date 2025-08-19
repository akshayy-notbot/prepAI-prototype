# 🔴 **REDIS CONNECTION TROUBLESHOOTING GUIDE**

## ❌ **Current Issue**
Your app is deployed but getting Redis connection errors:
```
❌ Failed to save plan to Redis: Error 111 connecting to localhost:6379. Connection refused.
```

## 🔍 **Root Cause**
The app is falling back to `localhost:6379` because the `REDIS_URL` environment variable isn't being read properly from Render.

## 🛠️ **IMMEDIATE FIXES APPLIED**

### **1. Updated Redis Connection Logic** ✅
- **Before**: `os.environ.get('REDIS_URL', 'redis://localhost:6379/0')`
- **After**: `os.environ.get('REDIS_URL')` with proper error handling
- **Impact**: No more fallback to localhost

### **2. Added Connection Testing** ✅
- **Before**: Direct Redis operations without connection test
- **After**: `redis_client.ping()` to verify connection before use
- **Impact**: Clear error messages when Redis is unavailable

### **3. Enhanced Error Logging** ✅
- **Before**: Generic Redis errors
- **After**: Detailed logging showing `REDIS_URL` value and connection status
- **Impact**: Better debugging information

## 🔧 **VERIFICATION STEPS**

### **Step 1: Check Render Environment Variables**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your `prepai-api` service
3. Click **Environment** tab
4. Verify `REDIS_URL` is set and shows your Redis service URL

### **Step 2: Test Redis Connection**
Visit your `/test-redis` endpoint:
```
https://your-service-name.onrender.com/test-redis
```

**Expected Response**:
```json
{
  "status": "success",
  "message": "Redis read/write operations successful",
  "redis_url": "redis://red-...",
  "operations": {
    "write": "success",
    "read": "success",
    "delete": "success",
    "ping": "success"
  }
}
```

### **Step 3: Check Application Logs**
In Render dashboard, check the logs for:
- ✅ `🔗 Connecting to Redis: redis://red-...`
- ✅ `✅ Redis connection successful`
- ❌ `❌ REDIS_URL environment variable not set`

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **Issue 1: REDIS_URL Not Set**
**Symptoms**: `❌ REDIS_URL environment variable not set`
**Solution**: 
1. Check Render environment variables
2. Ensure Redis service is running
3. Verify service connection in render.yaml

### **Issue 2: Redis Service Down**
**Symptoms**: Connection refused or timeout
**Solution**:
1. Check Redis service status in Render
2. Verify Redis service is in same region
3. Check Redis service logs

### **Issue 3: Network Configuration**
**Symptoms**: Connection errors between services
**Solution**:
1. Ensure all services are in same region
2. Check Render service networking
3. Verify service dependencies

## 📋 **RENDER CONFIGURATION CHECKLIST**

### **✅ Redis Service**
- [ ] Service name: `prepai-redis`
- [ ] Status: Running
- [ ] Region: Same as web service
- [ ] Plan: Free (or higher)

### **✅ Web Service Environment**
- [ ] `REDIS_URL`: Auto-filled from Redis service
- [ ] `DATABASE_URL`: Your existing secret
- [ ] `GOOGLE_API_KEY`: Your existing secret
- [ ] `PYTHON_VERSION`: 3.11.9

### **✅ Service Dependencies**
- [ ] Web service depends on Redis service
- [ ] Both services in same region
- [ ] Auto-deploy enabled

## 🔄 **TESTING AFTER FIXES**

### **1. Health Check**
```
GET /health
```
Should show Redis connection status

### **2. Redis Test**
```
GET /test-redis
```
Should show successful Redis operations

### **3. Interview Creation**
```
POST /api/start-interview
```
Should save to Redis without errors

## 🎯 **EXPECTED RESULT**

After fixes:
- ✅ **Redis Connection**: Successful to your Render Redis service
- ✅ **Data Storage**: Interview plans saved to Redis
- ✅ **Session Management**: Working properly
- ✅ **Full Functionality**: Complete interview platform

## 📱 **MONITORING**

### **Watch for These Log Messages**:
```
🔗 Connecting to Redis: redis://red-...
✅ Redis connection successful
✅ Interview plan saved to Redis with key: plan:...
```

### **Avoid These Messages**:
```
❌ REDIS_URL environment variable not set
❌ Failed to save plan to Redis
Error 111 connecting to localhost:6379
```

## 🆘 **IF ISSUE PERSISTS**

1. **Check Render Logs**: Look for detailed error messages
2. **Verify Environment Variables**: Ensure REDIS_URL is set
3. **Test Redis Service**: Verify Redis service is running
4. **Check Service Dependencies**: Ensure proper service order

---

**Status**: 🟡 **FIXES APPLIED - TESTING REQUIRED**
**Next Action**: Test Redis connection and verify environment variables
**Expected Result**: Successful Redis connection and full functionality
