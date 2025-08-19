# 🔴 Redis Deployment Guide for PrepAI on Render

## 🚨 Current Issue
Your deployment is failing because the `celery` module is missing and your app depends on Redis for session management.

## 🛠️ Solution Options

### Option 1: Full Redis Deployment (Recommended)
Deploy with Redis service on Render for full functionality.

### Option 2: Simplified Deployment (Quick Fix)
Deploy without Redis for basic functionality.

## 🚀 Option 1: Full Redis Deployment

### Step 1: Update Your Repository
1. **Replace `celery_app.py`** with the original version (keep your current one)
2. **Use `requirements-render.txt`** (the comprehensive one I created)
3. **Use the updated `render.yaml`** (includes Redis service)

### Step 2: Render Deployment
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Create **3 services** in this order:

#### Service 1: PostgreSQL Database
- **Type**: PostgreSQL
- **Name**: `prepai-database`
- **Plan**: Free
- **Region**: Oregon (or your preferred region)

#### Service 2: Redis Service
- **Type**: Redis
- **Name**: `prepai-redis`
- **Plan**: Free
- **Region**: Same as database

#### Service 3: Web Service
- **Type**: Web Service
- **Name**: `prepai-api`
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements-render.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Environment Variables
Set these in your web service:

| Variable | Value | Source |
|----------|-------|---------|
| `DATABASE_URL` | Auto-filled from PostgreSQL | Database service |
| `REDIS_URL` | Auto-filled from Redis | Redis service |
| `GOOGLE_API_KEY` | Your actual API key | Manual entry |
| `PYTHON_VERSION` | 3.11.9 | Fixed value |
| `ENVIRONMENT` | production | Fixed value |

## ⚡ Option 2: Simplified Deployment (No Redis)

### Step 1: Use Simplified Files
1. **Rename `celery_app.py`** to `celery_app_backup.py`
2. **Rename `celery_app_simple.py`** to `celery_app.py`
3. **Use `requirements-render-simple.txt`**

### Step 2: Render Deployment
1. Create only **2 services**:
   - PostgreSQL Database
   - Web Service

### Step 3: Environment Variables
| Variable | Value | Source |
|----------|-------|---------|
| `DATABASE_URL` | Auto-filled from PostgreSQL | Database service |
| `GOOGLE_API_KEY` | Your actual API key | Manual entry |
| `PYTHON_VERSION` | 3.11.9 | Fixed value |

## 🔧 Quick Fix Commands

### For Option 1 (Full Redis):
```bash
# In your local project directory
git add .
git commit -m "Add Redis support for Render deployment"
git push origin main
```

### For Option 2 (No Redis):
```bash
# Rename files
mv celery_app.py celery_app_backup.py
mv celery_app_simple.py celery_app.py

# Commit changes
git add .
git commit -m "Simplify deployment without Redis"
git push origin main
```

## 📋 Deployment Checklist

### ✅ Pre-Deployment
- [ ] Choose deployment option (Redis or No Redis)
- [ ] Update repository with correct files
- [ ] Push changes to GitHub

### ✅ Render Setup
- [ ] Create PostgreSQL database service
- [ ] Create Redis service (if using Option 1)
- [ ] Create web service
- [ ] Set environment variables
- [ ] Deploy

### ✅ Post-Deployment
- [ ] Test `/health` endpoint
- [ ] Test main application
- [ ] Verify database connection
- [ ] Test AI integration

## 🆘 Troubleshooting

### Build Failures
- Check Python version compatibility
- Verify requirements file is correct
- Check for syntax errors

### Runtime Errors
- Verify environment variables are set
- Check service logs for specific errors
- Ensure database is accessible

### Redis Connection Issues
- Verify Redis service is running
- Check Redis URL format
- Ensure Redis service is in same region

## 🎯 Recommendation

**Start with Option 2 (No Redis)** to get your app deployed quickly, then upgrade to Option 1 (Full Redis) once the basic deployment is working.

This approach lets you:
1. ✅ Deploy successfully without Redis dependencies
2. ✅ Test your core functionality
3. ✅ Add Redis later for full features
4. ✅ Learn the deployment process step by step

## 📚 Next Steps

1. **Choose your deployment option**
2. **Update your repository**
3. **Deploy on Render**
4. **Test your application**
5. **Add Redis later if needed**

---

**Need Help?** Check the main `DEPLOYMENT_CHECKLIST.md` or create an issue in your GitHub repository.
