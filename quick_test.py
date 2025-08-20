#!/usr/bin/env python3
"""
Quick Test Script for PrepAI Backend
Run this to quickly test your backend endpoints
"""

import requests
import json
import sys
import time
from urllib.parse import urljoin

def print_status(message, status="INFO"):
    """Print a formatted status message"""
    timestamp = time.strftime("%H:%M:%S")
    status_colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    color = status_colors.get(status, status_colors["INFO"])
    print(f"{color}[{timestamp}] {status}: {message}{status_colors['RESET']}")

def test_endpoint(base_url, endpoint, method="GET", data=None, expected_status=200):
    """Test a single endpoint"""
    url = urljoin(base_url, endpoint)
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print_status(f"Unsupported method: {method}", "ERROR")
            return False
            
        if response.status_code == expected_status:
            print_status(f"✅ {endpoint} - {response.status_code}", "SUCCESS")
            if response.content:
                try:
                    result = response.json()
                    print(f"   Response: {json.dumps(result, indent=2)}")
                except:
                    print(f"   Response: {response.text[:200]}...")
            return True
        else:
            print_status(f"❌ {endpoint} - Expected {expected_status}, got {response.status_code}", "ERROR")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print_status(f"❌ {endpoint} - Connection failed (server not running?)", "ERROR")
        return False
    except requests.exceptions.Timeout:
        print_status(f"❌ {endpoint} - Request timeout", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ {endpoint} - Error: {str(e)}", "ERROR")
        return False

def test_websocket(base_url):
    """Test WebSocket connection (basic check)"""
    try:
        import websocket
        
        # Convert HTTP URL to WebSocket URL
        ws_url = base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        ws_url = f"{ws_url}/ws/test-session"
        
        print_status(f"Testing WebSocket connection to: {ws_url}", "INFO")
        
        # Create a test WebSocket connection
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.close()
        
        print_status("✅ WebSocket connection successful", "SUCCESS")
        return True
        
    except ImportError:
        print_status("⚠️ websocket-client not installed, skipping WebSocket test", "WARNING")
        print_status("Install with: pip install websocket-client", "INFO")
        return False
    except Exception as e:
        print_status(f"❌ WebSocket test failed: {str(e)}", "ERROR")
        return False

def run_comprehensive_test(base_url):
    """Run all tests"""
    print_status("🚀 Starting comprehensive backend test", "INFO")
    print_status(f"Testing backend at: {base_url}", "INFO")
    print("=" * 60)
    
    test_results = []
    
    # Infrastructure tests
    print_status("🔧 Testing Infrastructure", "INFO")
    test_results.append(("Health Check", test_endpoint(base_url, "/health")))
    test_results.append(("Redis Test", test_endpoint(base_url, "/test-redis")))
    test_results.append(("Celery Test", test_endpoint(base_url, "/test-celery")))
    
    print()
    
    # API tests
    print_status("🌐 Testing API Endpoints", "INFO")
    
    # Test start interview
    interview_data = {
        "role": "Software Engineer",
        "seniority": "Junior",
        "skills": ["Python", "JavaScript"]
    }
    start_success = test_endpoint(base_url, "/api/start-interview", "POST", interview_data, 200)
    test_results.append(("Start Interview", start_success))
    
    if start_success:
        # Try to get the session ID from the response
        try:
            response = requests.post(urljoin(base_url, "/api/start-interview"), json=interview_data)
            if response.ok:
                data = response.json()
                session_id = data.get('session_id')
                if session_id:
                    print_status(f"📝 Got session ID: {session_id}", "SUCCESS")
                    
                    # Test submit answer
                    answer_data = {
                        "session_id": session_id,
                        "answer": "This is a test answer for testing purposes."
                    }
                    submit_success = test_endpoint(base_url, "/api/submit-answer", "POST", answer_data, 202)
                    test_results.append(("Submit Answer", submit_success))
                else:
                    print_status("⚠️ No session ID in response", "WARNING")
                    test_results.append(("Submit Answer", False))
            else:
                test_results.append(("Submit Answer", False))
        except Exception as e:
            print_status(f"❌ Error testing submit answer: {str(e)}", "ERROR")
            test_results.append(("Submit Answer", False))
    else:
        test_results.append(("Submit Answer", False))
    
    print()
    
    # WebSocket test
    print_status("🔌 Testing WebSocket", "INFO")
    ws_success = test_websocket(base_url)
    test_results.append(("WebSocket", ws_success))
    
    print()
    
    # Summary
    print_status("📊 Test Summary", "INFO")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print_status("🎉 Backend is working well!", "SUCCESS")
    elif success_rate >= 60:
        print_status("⚠️ Backend has some issues", "WARNING")
    else:
        print_status("❌ Backend has significant issues", "ERROR")
    
    return success_rate >= 60

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Default to local development
        base_url = "http://localhost:8000"
    
    print_status("🧪 PrepAI Backend Quick Test Suite", "INFO")
    print_status("This script tests your backend endpoints quickly", "INFO")
    print()
    
    try:
        success = run_comprehensive_test(base_url)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("Test interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
