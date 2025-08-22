#!/usr/bin/env python3
"""
Debug script to isolate the import issue with PersonaAgent
"""

import sys
import os

def test_imports():
    """Test imports step by step to isolate the issue"""
    print("🔍 Debugging Import Issues")
    print("=" * 50)
    
    # Test 1: Basic Python imports
    print("📝 Test 1: Basic Python imports")
    try:
        import json
        import time
        import redis
        from datetime import datetime
        print("   ✅ Basic imports successful")
    except Exception as e:
        print(f"   ❌ Basic imports failed: {e}")
        return False
    
    # Test 2: Google GenerativeAI
    print("📝 Test 2: Google GenerativeAI import")
    try:
        import google.generativeai as genai
        print("   ✅ Google GenerativeAI imported successfully")
    except Exception as e:
        print(f"   ❌ Google GenerativeAI import failed: {e}")
        return False
    
    # Test 3: Agents package import
    print("📝 Test 3: Agents package import")
    try:
        import agents
        print("   ✅ Agents package imported successfully")
        print(f"   📊 Available in agents: {dir(agents)}")
    except Exception as e:
        print(f"   ❌ Agents package import failed: {e}")
        return False
    
    # Test 4: Individual agent imports
    print("📝 Test 4: Individual agent imports")
    try:
        from agents.persona import RouterAgent
        print("   ✅ RouterAgent imported successfully")
    except Exception as e:
        print(f"   ❌ RouterAgent import failed: {e}")
        return False
    
    try:
        from agents.persona import GeneratorAgent
        print("   ✅ GeneratorAgent imported successfully")
    except Exception as e:
        print(f"   ❌ GeneratorAgent import failed: {e}")
        return False
    
    try:
        from agents.persona import PersonaAgent
        print("   ✅ PersonaAgent imported successfully")
    except Exception as e:
        print(f"   ❌ PersonaAgent import failed: {e}")
        return False
    
    # Test 5: Check file contents
    print("📝 Test 5: File content verification")
    try:
        persona_file = "agents/persona.py"
        if os.path.exists(persona_file):
            with open(persona_file, 'r') as f:
                content = f.read()
                if "class PersonaAgent:" in content:
                    print("   ✅ PersonaAgent class found in file")
                else:
                    print("   ❌ PersonaAgent class NOT found in file")
                    return False
        else:
            print(f"   ❌ File not found: {persona_file}")
            return False
    except Exception as e:
        print(f"   ❌ File read failed: {e}")
        return False
    
    # Test 6: Check __init__.py
    print("📝 Test 6: __init__.py verification")
    try:
        init_file = "agents/__init__.py"
        if os.path.exists(init_file):
            with open(init_file, 'r') as f:
                content = f.read()
                if "PersonaAgent" in content:
                    print("   ✅ PersonaAgent found in __init__.py")
                else:
                    print("   ❌ PersonaAgent NOT found in __init__.py")
                    return False
        else:
            print(f"   ❌ __init__.py not found: {init_file}")
            return False
    except Exception as e:
        print(f"   ❌ __init__.py read failed: {e}")
        return False
    
    print("\n🎉 All import tests passed!")
    return True

def test_syntax():
    """Test syntax of key files"""
    print("\n🔍 Testing File Syntax")
    print("=" * 30)
    
    files_to_test = [
        "agents/persona.py",
        "agents/__init__.py",
        "main.py"
    ]
    
    for file_path in files_to_test:
        print(f"📝 Testing syntax: {file_path}")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                compile(content, file_path, 'exec')
                print(f"   ✅ {file_path} syntax is valid")
        except Exception as e:
            print(f"   ❌ {file_path} syntax error: {e}")
            return False
    
    print("🎉 All syntax tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Import Debug Session")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"📂 Files in current directory: {os.listdir('.')}")
    
    # Run import tests
    import_success = test_imports()
    
    # Run syntax tests
    syntax_success = test_syntax()
    
    # Summary
    print("\n📊 Debug Summary")
    print("=" * 30)
    print(f"Import tests: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"Syntax tests: {'✅ PASS' if syntax_success else '❌ FAIL'}")
    
    if import_success and syntax_success:
        print("\n🎉 All tests passed! Import issue not found locally.")
        print("The problem might be in the Render deployment environment.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
