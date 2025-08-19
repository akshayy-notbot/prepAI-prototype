# 🚀 Quick Start: Deploy PrepAI to GitHub & Render

## ⚡ 5-Minute Setup

### 1. **Prepare Files** (2 minutes)
```bash
python prepare_deployment.py
```
This creates a clean `deployment_package/` folder with only the files you need.

### 2. **Upload to GitHub** (2 minutes)
- Go to [GitHub.com](https://github.com)
- Create new repository: `PrepAI-Prototype`
- Upload ALL files from `deployment_package/` folder
- **Important**: Include `.gitignore` file

### 3. **Deploy on Render** (1 minute)
- Go to [Render Dashboard](https://dashboard.render.com)
- Connect GitHub repo
- Create PostgreSQL database
- Set environment variables:
  - `GOOGLE_API_KEY`: Your Gemini API key
  - `DATABASE_URL`: From PostgreSQL service
- Deploy!

## 🔑 Required Environment Variables

| Variable | Value | Source |
|----------|-------|---------|
| `GOOGLE_API_KEY` | Your actual API key | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `DATABASE_URL` | Auto-filled | Render PostgreSQL service |
| `PYTHON_VERSION` | 3.11.9 | Fixed value |

## 📱 Frontend Options

### Option A: GitHub Pages (Free)
- Repository Settings → Pages
- Source: Deploy from `main` branch
- Your site: `https://username.github.io/PrepAI-Prototype`

### Option B: Render Static Site
- Upload frontend files to Render
- Connect to your backend API

## 🔗 Update URLs

After deployment, update these files with your actual URLs:
- `config.js` - Update Render service URLs
- `README.md` - Update GitHub and Render links

## ✅ Test Your Deployment

1. **Health Check**: Visit `/health` endpoint
2. **Main App**: Test the interview flow
3. **AI Integration**: Verify question generation works
4. **Database**: Check if data is being stored

## 🆘 Common Issues

- **Build Failures**: Check Python version compatibility
- **CORS Errors**: Verify origins in `main.py`
- **Database Issues**: Check connection string format
- **API Errors**: Verify environment variables are set

## 📚 Full Documentation

See `DEPLOYMENT_CHECKLIST.md` for detailed step-by-step instructions.

---

**Need Help?** Check the Issues page in your GitHub repository or refer to the full deployment checklist.
