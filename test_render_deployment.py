#!/usr/bin/env python3
"""
Quick Render Deployment Test Script
Run this after deployment to verify everything is working
"""

import requests
import json
import time
import os

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    print(f"🔍 Testing health endpoint: {base_url}/health")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_database_operations(base_url):
    """Test basic database operations"""
    print(f"\n🗄️ Testing database operations: {base_url}")
    
    # Test creating a simple interview session
    test_data = {
        "role": "Product Manager",
        "seniority": "Senior",
        "skills": ["Product Design", "User Empathy"]
    }
    
    try:
        # This would test the interview creation endpoint
        # Adjust the endpoint based on your actual API
        response = requests.post(
            f"{base_url}/create-interview",
            json=test_data,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("✅ Database write operation successful")
            return True
        else:
            print(f"⚠️ Database operation status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database operation error: {e}")
        return False

def test_redis_functionality(base_url):
    """Test Redis functionality through the API"""
    print(f"\n🔴 Testing Redis functionality: {base_url}")
    
    try:
        # Test session state management
        # This would test creating and retrieving session state
        response = requests.get(f"{base_url}/test-redis", timeout=10)
        
        if response.status_code == 200:
            print("✅ Redis operations working through API")
            return True
        else:
            print(f"⚠️ Redis test status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Redis test error: {e}")
        return False

def test_performance_metrics(base_url):
    """Test performance metrics"""
    print(f"\n⚡ Testing performance metrics: {base_url}")
    
    try:
        # Test response time
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if response_time < 1000:  # Less than 1 second
            print(f"✅ Response time: {response_time:.2f}ms (Good)")
        elif response_time < 3000:  # Less than 3 seconds
            print(f"⚠️ Response time: {response_time:.2f}ms (Acceptable)")
        else:
            print(f"❌ Response time: {response_time:.2f}ms (Too slow)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def generate_deployment_report(base_url, results):
    """Generate deployment test report"""
    print(f"\n📋 Render Deployment Test Report")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Base URL: {base_url}")
    print(f"Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results: {passed}/{total} tests passed")
    
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Deployment is successful!")
        print(f"📋 Next Steps:")
        print(f"   1. Monitor application logs")
        print(f"   2. Test full interview flow")
        print(f"   3. Check performance under load")
        print(f"   4. Verify Redis session management")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the issues above.")
        print(f"📋 Troubleshooting:")
        print(f"   1. Check Render service logs")
        print(f"   2. Verify environment variables")
        print(f"   3. Check database and Redis connections")
        print(f"   4. Run verify_render_deployment.py locally")

def main():
    """Run all deployment tests"""
    print("🚀 PrepAI Render Deployment Test")
    print("=" * 40)
    
    # Get base URL from user or environment
    base_url = os.getenv('PREPAI_BASE_URL')
    if not base_url:
        base_url = input("Enter your Render app base URL (e.g., https://prepai-api.onrender.com): ").strip()
    
    if not base_url:
        print("❌ No base URL provided. Exiting.")
        return
    
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    
    print(f"Testing deployment at: {base_url}")
    
    # Run all tests
    tests = {
        "Health Endpoint": lambda: test_health_endpoint(base_url),
        "Database Operations": lambda: test_database_operations(base_url),
        "Redis Functionality": lambda: test_redis_functionality(base_url),
        "Performance Metrics": lambda: test_performance_metrics(base_url)
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Generate report
    generate_deployment_report(base_url, results)
    
    # Return exit code
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        print(f"\n✅ Deployment validation successful!")
        return True
    else:
        print(f"\n❌ Deployment validation failed!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
