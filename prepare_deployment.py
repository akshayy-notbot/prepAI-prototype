#!/usr/bin/env python3
"""
Deployment Preparation Script for PrepAI-Prototype
This script helps prepare your project for GitHub and Render deployment.
"""

import os
import shutil
import glob
from pathlib import Path

def create_deployment_package():
    """Create a clean deployment package by excluding unnecessary files."""
    
    # Files and folders to exclude from deployment
    exclude_patterns = [
        'venv/',
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.env*',
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        '.DS_Store',
        'Thumbs.db',
        'celerybeat-schedule',
        'celerybeat.pid',
        '*.log',
        'logs/',
        '.pytest_cache/',
        'htmlcov/',
        '.coverage',
        '.mypy_cache/',
        '.pyre/',
        '.pytype/',
        'cython_debug/',
        'build/',
        'dist/',
        '*.egg-info/',
        'node_modules/',
        'package-lock.json',
        'yarn.lock'
    ]
    
    # Create deployment directory
    deployment_dir = Path('deployment_package')
    if deployment_dir.exists():
        shutil.rmtree(deployment_dir)
    deployment_dir.mkdir()
    
    print("🚀 Creating deployment package...")
    
    # Copy all files and folders, excluding unwanted ones
    for item in Path('.').iterdir():
        if item.name == 'deployment_package':
            continue
            
        # Check if item should be excluded
        should_exclude = False
        for pattern in exclude_patterns:
            if pattern.endswith('/') and item.is_dir() and item.name == pattern.rstrip('/'):
                should_exclude = True
                break
            elif pattern.startswith('*') and item.name.endswith(pattern[1:]):
                should_exclude = True
                break
            elif pattern.startswith('.') and item.name.startswith('.'):
                should_exclude = True
                break
            elif item.name == pattern:
                should_exclude = True
                break
        
        if should_exclude:
            print(f"❌ Excluding: {item.name}")
            continue
            
        # Copy the item
        if item.is_file():
            shutil.copy2(item, deployment_dir / item.name)
            print(f"✅ Copied file: {item.name}")
        elif item.is_dir():
            shutil.copytree(item, deployment_dir / item.name)
            print(f"✅ Copied folder: {item.name}")
    
    print(f"\n🎉 Deployment package created in '{deployment_dir}' directory!")
    print("📋 Files ready for GitHub upload:")
    
    # List all files in deployment package
    for item in deployment_dir.rglob('*'):
        if item.is_file():
            print(f"   📄 {item.relative_to(deployment_dir)}")
    
    print(f"\n📁 Total files: {len(list(deployment_dir.rglob('*')))}")
    print("\n🚀 Next steps:")
    print("1. Upload all files from 'deployment_package' folder to GitHub")
    print("2. Make sure to include the .gitignore file")
    print("3. Follow the DEPLOYMENT_CHECKLIST.md for Render setup")

def check_sensitive_files():
    """Check for potentially sensitive files that shouldn't be deployed."""
    
    sensitive_patterns = [
        '.env*',
        'secrets.py',
        'config.py',
        'credentials.json',
        '*.key',
        '*.pem',
        '*.p12',
        '*.pfx'
    ]
    
    print("🔍 Checking for sensitive files...")
    found_sensitive = False
    
    for pattern in sensitive_patterns:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if os.path.isfile(match):
                print(f"⚠️  WARNING: Potentially sensitive file found: {match}")
                found_sensitive = True
    
    if not found_sensitive:
        print("✅ No sensitive files found")
    else:
        print("\n⚠️  Please review these files before deployment!")

def main():
    """Main function to run deployment preparation."""
    
    print("=" * 60)
    print("🚀 PrepAI-Prototype Deployment Preparation")
    print("=" * 60)
    
    # Check for sensitive files first
    check_sensitive_files()
    print()
    
    # Create deployment package
    create_deployment_package()
    
    print("\n" + "=" * 60)
    print("✅ Deployment preparation complete!")
    print("📚 See DEPLOYMENT_CHECKLIST.md for next steps")
    print("=" * 60)

if __name__ == "__main__":
    main()
