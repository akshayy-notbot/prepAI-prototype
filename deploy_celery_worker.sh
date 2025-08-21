#!/bin/bash

# Deploy Celery Worker Fix to Render
# This script helps deploy the updated render.yaml with the Celery worker service

echo "🚀 Deploying Celery Worker Fix to Render"
echo "=========================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    echo "Please run this script from your project root directory"
    exit 1
fi

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ Error: render.yaml not found"
    echo "Please ensure render.yaml is in the current directory"
    exit 1
fi

# Check git status
echo "📊 Checking git status..."
git status --porcelain

# Ask for confirmation
echo ""
read -p "Do you want to proceed with deployment? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Add render.yaml
echo "📝 Adding render.yaml to git..."
git add render.yaml

# Commit changes
echo "💾 Committing changes..."
git commit -m "Add Celery worker service for background tasks - Fix interview flow issue"

# Push to remote
echo "🚀 Pushing to remote repository..."
git push origin main

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your Render dashboard"
echo "2. Wait for the new 'prepai-celery-worker' service to appear"
echo "3. Wait for deployment to complete (usually 2-5 minutes)"
echo "4. Test the interview flow using your debug tools"
echo ""
echo "🔍 Monitor deployment:"
echo "- Check Render dashboard for new service"
echo "- Look for 'prepai-celery-worker' service status"
echo "- Monitor logs for any errors"
echo ""
echo "🧪 Test after deployment:"
echo "- Use interview_debug_test.html"
echo "- Or run: curl 'https://prepai-api.onrender.com/api/celery-status'"
echo ""
echo "🎯 Expected result: AI should now respond after submitting answers!"
