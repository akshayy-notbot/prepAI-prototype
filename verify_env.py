#!/usr/bin/env python3
"""
Environment Configuration Verifier
This script helps verify that your .env file is properly configured for Render deployment.
"""

import os
from dotenv import load_dotenv
import re

def load_and_verify_env():
    """Load .env file and verify configuration"""
    print("🔧 Environment Configuration Verifier")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please create a .env file in your project root directory.")
        return False
    
    # Load environment variables
    load_dotenv()
    print("✅ .env file loaded successfully")
    
    # Define required variables and their patterns
    required_vars = {
        'RENDER_API_URL': {
            'pattern': r'^https://.*\.onrender\.com$',
            'description': 'Your Render API service URL'
        },
        'DATABASE_URL': {
            'pattern': r'^postgresql://.*@.*:.*/.*$',
            'description': 'Your Render PostgreSQL database URL'
        },
        'REDIS_URL': {
            'pattern': r'^redis://.*@.*:.*$',
            'description': 'Your Render Redis service URL'
        },
        'GOOGLE_API_KEY': {
            'pattern': r'^AIza[A-Za-z0-9_-]{35}$',
            'description': 'Your Google Gemini API key'
        }
    }
    
    print("\n📋 Checking Required Environment Variables:")
    print("-" * 40)
    
    all_valid = True
    validation_results = {}
    
    for var_name, config in required_vars.items():
        value = os.getenv(var_name)
        
        if not value:
            print(f"❌ {var_name}: Not set")
            all_valid = False
            validation_results[var_name] = False
            continue
        
        # Check if value matches expected pattern
        pattern = config['pattern']
        if re.match(pattern, value):
            print(f"✅ {var_name}: Valid format")
            validation_results[var_name] = True
            
            # Show masked value for security
            if 'API_KEY' in var_name:
                masked_value = value[:10] + "..." + value[-4:]
            else:
                masked_value = value[:30] + "..." if len(value) > 30 else value
            print(f"   Value: {masked_value}")
            
        else:
            print(f"⚠️  {var_name}: Format may be incorrect")
            print(f"   Expected pattern: {pattern}")
            print(f"   Current value: {value[:50]}...")
            validation_results[var_name] = False
            all_valid = False
    
    # Additional validation
    print("\n🔍 Additional Validation:")
    print("-" * 30)
    
    # Check RENDER_API_URL format
    render_url = os.getenv('RENDER_API_URL')
    if render_url:
        if 'onrender.com' in render_url:
            print("✅ RENDER_API_URL contains correct domain")
        else:
            print("⚠️  RENDER_API_URL may not be a Render service")
    
    # Check DATABASE_URL format
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        if 'render.com' in db_url:
            print("✅ DATABASE_URL contains Render host")
        else:
            print("⚠️  DATABASE_URL may not be a Render database")
    
    # Check REDIS_URL format
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        if 'render.com' in redis_url:
            print("✅ REDIS_URL contains Render host")
        else:
            print("⚠️  REDIS_URL may not be a Render Redis service")
    
    # Check GOOGLE_API_KEY format
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        if api_key.startswith('AIza') and len(api_key) == 39:
            print("✅ GOOGLE_API_KEY format looks correct")
        else:
            print("⚠️  GOOGLE_API_KEY format may be incorrect")
    
    # Summary
    print("\n📊 Validation Summary:")
    print("=" * 30)
    
    valid_count = sum(validation_results.values())
    total_count = len(required_vars)
    
    print(f"✅ Valid: {valid_count}/{total_count}")
    
    if all_valid:
        print("🎉 All environment variables are properly configured!")
        print("   You're ready to run tests against your Render deployment.")
        return True
    else:
        print("❌ Some environment variables need attention.")
        print("   Please fix the issues above before proceeding.")
        return False

def show_env_template():
    """Show a template for the .env file"""
    print("\n📝 .env File Template:")
    print("=" * 30)
    print("""# ========================================
# RENDER DEPLOYMENT CREDENTIALS
# ========================================

# 1. YOUR RENDER API SERVICE
RENDER_API_URL=https://your-api-service-name.onrender.com

# 2. YOUR RENDER POSTGRESQL DATABASE
DATABASE_URL=postgresql://username:password@host:port/database_name

# 3. YOUR RENDER REDIS SERVICE  
REDIS_URL=redis://username:password@host:port

# 4. GOOGLE GEMINI API KEY
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# ========================================
# OPTIONAL: ADDITIONAL CONFIGURATION
# ========================================

# Environment indicator
ENVIRONMENT=production

# Logging level
LOG_LEVEL=INFO""")

def show_help():
    """Show help information"""
    print("\n💡 How to Get Your Render Credentials:")
    print("=" * 40)
    print("1. Go to https://dashboard.render.com/")
    print("2. Navigate to your services (API, Database, Redis)")
    print("3. Click on each service to get connection details")
    print("4. Copy the External URLs from the Connections tab")
    print("5. For Google API key, go to https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    try:
        success = load_and_verify_env()
        
        if not success:
            show_env_template()
            show_help()
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        print("Please check your .env file format and try again.")
