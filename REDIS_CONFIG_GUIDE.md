# 🔴 Redis Configuration Guide for PrepAI

## ✅ **Great News!**
You already have Redis running on Render with URL: `redis://red-d2ibkjbipnbc73bjnab0:6379`

## 🚀 **Deployment Steps**

### **Step 1: Use Full Redis Setup**
Since you have Redis, use these files:
- ✅ **Keep** `celery_app.py` (original version)
- ✅ **Use** `requirements-render.txt` (comprehensive)
- ✅ **Use** `render.yaml` (updated for Redis)

### **Step 2: Render Service Configuration**

#### **Web Service Setup**
- **Build Command**: `pip install -r requirements-render.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### **Environment Variables**
| Variable | Value | Source |
|----------|-------|---------|
| `DATABASE_URL` | Auto-filled from PostgreSQL | Database service |
| `REDIS_URL` | `redis://red-d2ibkjbipnbc73bjnab0:6379` | Your existing Redis |
| `GOOGLE_API_KEY` | Your actual API key | Manual entry |
| `PYTHON_VERSION` | 3.11.9 | Fixed value |
| `ENVIRONMENT` | production | Fixed value |

### **Step 3: Service Creation Order**
1. **PostgreSQL Database** (if not already created)
2. **Web Service** (connect to existing Redis)

## 🔧 **Redis URL Configuration**

Your Redis URL: `redis://red-d2ibkjbipnbc73bjnab0:6379`

**Format Breakdown:**
- **Protocol**: `redis://`
- **Host**: `red-d2ibkjbipnbc73bjnab0`
- **Port**: `6379`
- **Database**: `0` (default)

## 📋 **Deployment Checklist**

### ✅ **Pre-Deployment**
- [ ] Use `requirements-render.txt` (not simple version)
- [ ] Keep original `celery_app.py`
- [ ] Use updated `render.yaml`

### ✅ **Render Setup**
- [ ] Create PostgreSQL database (if needed)
- [ ] Create web service
- [ ] Set `REDIS_URL` to your existing Redis
- [ ] Set `GOOGLE_API_KEY`
- [ ] Deploy

### ✅ **Post-Deployment**
- [ ] Test `/health` endpoint
- [ ] Test Redis connection
- [ ] Test Celery tasks
- [ ] Test full interview flow

## 🆘 **Troubleshooting**

### **Redis Connection Issues**
- Verify Redis service is running
- Check if Redis URL is accessible from web service
- Ensure both services are in same region

### **Build Failures**
- Check `requirements-render.txt` has all dependencies
- Verify Python version compatibility
- Check for syntax errors

### **Runtime Errors**
- Check service logs for specific Redis errors
- Verify environment variables are set correctly
- Test Redis connection manually

## 🎯 **Expected Result**

With Redis properly configured, your app should:
- ✅ Start successfully without import errors
- ✅ Connect to Redis for session management
- ✅ Run Celery tasks for interview orchestration
- ✅ Provide full functionality

## 📚 **Next Steps**

1. **Deploy with full Redis setup**
2. **Test all functionality**
3. **Monitor Redis usage**
4. **Scale if needed**

---

**Your Redis is ready!** Just deploy with the full requirements and proper configuration.
