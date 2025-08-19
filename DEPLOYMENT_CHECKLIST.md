# 🚀 Deployment Checklist for PrepAI-Prototype

This checklist will guide you through deploying your PrepAI project to GitHub and Render manually.

## 📋 Pre-Deployment Preparation

### ✅ Files to Include in GitHub Upload
- [ ] `main.py` - FastAPI backend application
- [ ] `app.js` - Frontend JavaScript code
- [ ] `index.html` - Main HTML file
- [ ] `models.py` - Database models
- [ ] `celery_app.py` - Celery configuration
- [ ] `agents/` folder (all files)
- [ ] `tests/` folder (all files)
- [ ] `requirements.txt` - Python dependencies
- [ ] `requirements-render.txt` - Render-specific requirements
- [ ] `render.yaml` - Render deployment configuration
- [ ] `startup.py` - Startup scripts
- `migrate_database.py` - Database migration script
- `seed.py` - Database seeding script
- `.gitignore` - Git ignore file
- `README.md` - Project documentation
- `DEPLOYMENT_CHECKLIST.md` - This file

### ❌ Files to EXCLUDE from GitHub Upload
- [ ] `venv/` folder (virtual environment)
- [ ] `.env` files (contain sensitive API keys)
- [ ] `__pycache__/` folders
- [ ] Any local configuration files
- [ ] Database files (`.db`, `.sqlite`)

## 🌐 Step 1: GitHub Repository Setup

### 1.1 Create New Repository
- [ ] Go to [GitHub.com](https://github.com)
- [ ] Click the "+" icon → "New repository"
- [ ] Repository name: `PrepAI-Prototype`
- [ ] Description: `AI-Powered Interview Preparation Platform`
- [ ] Make it Public (recommended for portfolio)
- [ ] Don't initialize with README (we'll upload our own)
- [ ] Click "Create repository"

### 1.2 Upload Project Files
- [ ] In your new repository, click "uploading an existing file"
- [ ] Drag and drop all the files from the ✅ list above
- [ ] **Important**: Make sure `.gitignore` is included
- [ ] Add commit message: `Initial commit: PrepAI Interview Platform`
- [ ] Click "Commit changes"

### 1.3 Verify Upload
- [ ] Check that all files are visible in the repository
- [ ] Verify `.gitignore` is present and working
- [ ] Ensure no sensitive files (`.env`, `venv/`) are visible

## 🚀 Step 2: Render Deployment Setup

### 2.1 Connect GitHub Repository
- [ ] Go to [Render Dashboard](https://dashboard.render.com)
- [ ] Sign in with your GitHub account
- [ ] Click "New +" → "Web Service"
- [ ] Connect your GitHub account if not already connected
- [ ] Select your `PrepAI-Prototype` repository
- [ ] Click "Connect"

### 2.2 Configure Web Service
- [ ] **Name**: `prepai-api` (or your preferred name)
- [ ] **Environment**: `Python 3`
- [ ] **Region**: Choose closest to your users (e.g., Oregon)
- [ ] **Branch**: `main` (or your default branch)
- [ ] **Build Command**: `pip install -r requirements-render.txt`
- [ ] **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] **Plan**: Free (for testing)

### 2.3 Set Environment Variables
- [ ] **Add Environment Variable**:
  - Key: `GOOGLE_API_KEY`
  - Value: Your actual Google Gemini API key
  - **Important**: Keep this secret and secure
- [ ] **Add Environment Variable**:
  - Key: `PYTHON_VERSION`
  - Value: `3.11.9`
- [ ] **Add Environment Variable**:
  - Key: `ENVIRONMENT`
  - Value: `production`

### 2.4 Advanced Settings
- [ ] **Health Check Path**: `/health`
- [ ] **Auto-Deploy**: ✅ Enabled
- [ ] Click "Create Web Service"

## 🗄️ Step 3: Database Setup

### 3.1 Create PostgreSQL Database
- [ ] In Render Dashboard, click "New +" → "PostgreSQL"
- [ ] **Name**: `prepai-database`
- [ ] **Database**: `prepai_db`
- [ ] **User**: `prepai_user`
- [ ] **Region**: Same as your web service
- [ ] **Plan**: Free
- [ ] Click "Create Database"

### 3.2 Configure Database Environment Variables
- [ ] Go back to your web service
- [ ] Click "Environment" tab
- [ ] **Add Environment Variable**:
  - Key: `DATABASE_URL`
  - Value: Copy from your PostgreSQL service "Connections" tab
  - Format: `postgresql://username:password@host:port/database`

## 🔧 Step 4: Application Configuration

### 4.1 Update CORS Settings
- [ ] In your `main.py`, verify CORS origins include your Render domain
- [ ] Add your Render URL to the origins list if needed

### 4.2 Health Check Endpoint
- [ ] Verify `/health` endpoint exists in your FastAPI app
- [ ] If not, add a simple health check endpoint

### 4.3 Database Migration
- [ ] Your app should automatically create tables on startup
- [ ] If issues occur, you may need to run migrations manually

## 🚀 Step 5: Deploy and Test

### 5.1 Initial Deployment
- [ ] Render will automatically start building your service
- [ ] Monitor the build logs for any errors
- [ ] Wait for deployment to complete (usually 5-10 minutes)

### 5.2 Verify Deployment
- [ ] Check that your service shows "Live" status
- [ ] Click on your service URL to test
- [ ] Test the `/health` endpoint
- [ ] Verify the main application loads

### 5.3 Test Core Functionality
- [ ] Test the homepage loads
- [ ] Test interview creation flow
- [ ] Test AI question generation
- [ ] Test WebSocket connections (if applicable)

## 🔍 Step 6: Troubleshooting Common Issues

### 6.1 Build Failures
- [ ] Check build logs for Python version compatibility
- [ ] Verify all dependencies are in `requirements-render.txt`
- [ ] Check for syntax errors in Python files

### 6.2 Runtime Errors
- [ ] Check service logs for error messages
- [ ] Verify environment variables are set correctly
- [ ] Check database connection string format

### 6.3 CORS Issues
- [ ] Verify CORS origins include your frontend domain
- [ ] Check browser console for CORS errors
- [ ] Update CORS settings if needed

## 📱 Step 7: Frontend Deployment (Optional)

### 7.1 GitHub Pages (Free)
- [ ] In your GitHub repository, go to Settings → Pages
- [ ] Source: Deploy from a branch
- [ ] Branch: `main` → `/ (root)`
- [ ] Click "Save"

### 7.2 Update API Base URL
- [ ] In your `app.js`, update `API_BASE_URL` to your Render service URL
- [ ] Test the connection between frontend and backend

## ✅ Final Verification

### 8.1 Complete System Test
- [ ] [ ] Frontend loads correctly
- [ ] [ ] Backend API responds
- [ ] [ ] Database connections work
- [ ] [ ] AI integration functions
- [ ] [ ] WebSocket connections (if applicable)
- [ ] [ ] Error handling works properly

### 8.2 Documentation Update
- [ ] Update `README.md` with your actual GitHub and Render URLs
- [ ] Update any hardcoded URLs in your code
- [ ] Test all links and references

## 🎉 Success!

Once all checkboxes are completed, your PrepAI platform will be successfully deployed and accessible online!

### Your URLs:
- **GitHub Repository**: `https://github.com/yourusername/PrepAI-Prototype`
- **Live API**: `https://your-service-name.onrender.com`
- **Frontend**: `https://yourusername.github.io/PrepAI-Prototype` (if using GitHub Pages)

---

**Need Help?** Check the [Issues](https://github.com/yourusername/PrepAI-Prototype/issues) page or create a new issue with detailed error information.
