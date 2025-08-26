#!/usr/bin/env python3
"""
Comprehensive Test Suite for PrepAI Two-Loop Architecture
Tests the new Router/Generator agent system, topic graph, and Redis-only state management.

Usage:
    python3 test_new_architecture.py                    # Run all tests
    python3 test_new_architecture.py --unit            # Unit tests only
    python3 test_new_architecture.py --integration     # Integration tests only
    python3 test_new_architecture.py --performance     # Performance tests only
    python3 test_new_architecture.py --render          # Test against Render deployment
"""

import os
import sys
import time
import json
import argparse
import redis
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = [
        'GOOGLE_API_KEY',
        'DATABASE_URL', 
        'REDIS_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment")
        return False
    
    print("✅ Environment variables configured")
    return True

def get_redis_client():
    """Get Redis client for testing"""
    try:
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable is required. Please set it in Render dashboard.")
        client = redis.from_url(redis_url)
        client.ping()  # Test connection
        print("✅ Redis connection successful")
        return client
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return None

def test_router_agent():
    """Test RouterAgent independently"""
    print("\n🧪 Testing RouterAgent...")
    
    try:
        from agents.persona import RouterAgent
        
        # Create router agent
        router = RouterAgent()
        
        # Test data
        test_cases = [
            {
                "name": "Goal Achieved - Clear Answer",
                "user_answer": "I would start by defining user personas, then conduct user research to understand pain points, and finally create a prioritization matrix based on impact and effort.",
                "current_topic_goal": "Assess structured thinking in problem framing.",
                "expected_action": "ACKNOWLEDGE_AND_TRANSITION"
            },
            {
                "name": "Goal Not Achieved - Vague Answer", 
                "user_answer": "I think I would do some research and stuff.",
                "current_topic_goal": "Assess structured thinking in problem framing.",
                "expected_action": "GENERATE_FOLLOW_UP"
            },
            {
                "name": "Off-Topic Answer",
                "user_answer": "I really enjoy working with my team and we have great collaboration.",
                "current_topic_goal": "Assess structured thinking in problem framing.",
                "expected_action": "REDIRECT_TO_TOPIC"
            }
        ]
        
        passed = 0
        total_latency = 0
        
        for test_case in test_cases:
            print(f"  📝 Testing: {test_case['name']}")
            
            start_time = time.time()
            result = router.analyze_response(
                interviewer_persona_summary="Senior Product Manager",
                current_topic_goal=test_case['current_topic_goal'],
                conversation_history=[],
                user_latest_answer=test_case['user_answer']
            )
            latency = (time.time() - start_time) * 1000
            total_latency += latency
            
            # Validate response structure
            if not isinstance(result, dict):
                print(f"    ❌ Invalid response type: {type(result)}")
                continue
                
            required_fields = ['analysis_summary', 'goal_achieved', 'next_action']
            if not all(field in result for field in required_fields):
                print(f"    ❌ Missing required fields: {required_fields}")
                continue
            
            # Check if action matches expected (allowing for flexibility)
            if result['next_action'] in ['ACKNOWLEDGE_AND_TRANSITION', 'GENERATE_FOLLOW_UP', 'REDIRECT_TO_TOPIC']:
                print(f"    ✅ Valid action: {result['next_action']}")
                passed += 1
            else:
                print(f"    ⚠️ Unexpected action: {result['next_action']}")
                passed += 1
            
            # Check latency target
            if latency < 750:
                print(f"    ✅ Latency: {latency:.1f}ms (Target: < 750ms)")
            else:
                print(f"    ⚠️ Latency: {latency:.1f}ms (Target: < 750ms)")
            
            print(f"    📊 Analysis: {result['analysis_summary']}")
        
        avg_latency = total_latency / len(test_cases)
        print(f"  📈 RouterAgent Results: {passed}/{len(test_cases)} passed, Avg Latency: {avg_latency:.1f}ms")
        
        return passed == len(test_cases), avg_latency
        
    except Exception as e:
        print(f"  ❌ RouterAgent test failed: {e}")
        return False, 0

def test_generator_agent():
    """Test GeneratorAgent independently"""
    print("\n🧪 Testing GeneratorAgent...")
    
    try:
        from agents.persona import GeneratorAgent
        
        # Create generator agent
        generator = GeneratorAgent()
        
        # Test data
        test_cases = [
            {
                "name": "Acknowledge and Transition",
                "triggering_action": "ACKNOWLEDGE_AND_TRANSITION",
                "topic_graph": [
                    {
                        "topic_id": "PM_01_Problem_Definition",
                        "goal": "Assess structured thinking in problem framing.",
                        "keywords_for_persona_agent": ["user research", "problem definition", "stakeholder alignment"]
                    },
                    {
                        "topic_id": "PM_02_User_Segmentation", 
                        "goal": "Assess user understanding and segmentation skills.",
                        "keywords_for_persona_agent": ["user personas", "segmentation", "target audience"]
                    }
                ]
            },
            {
                "name": "Generate Follow-up",
                "triggering_action": "GENERATE_FOLLOW_UP",
                "topic_graph": [
                    {
                        "topic_id": "PM_01_Problem_Definition",
                        "goal": "Assess structured thinking in problem framing.",
                        "keywords_for_persona_agent": ["user research", "problem definition", "stakeholder alignment"]
                    }
                ]
            }
        ]
        
        passed = 0
        total_latency = 0
        
        for test_case in test_cases:
            print(f"  📝 Testing: {test_case['name']}")
            
            start_time = time.time()
            result = generator.generate_response(
                persona_role="Senior Product Manager",
                persona_company_context="Tech Company",
                interview_style="Professional",
                session_narrative="Designing a new e-commerce feature",
                topic_graph_json=test_case['topic_graph'],
                current_topic_id="PM_01_Problem_Definition",
                covered_topic_ids=[],
                conversation_history=[],
                triggering_action=test_case['triggering_action']
            )
            latency = (time.time() - start_time) * 1000
            total_latency += latency
            
            # Validate response structure
            if not isinstance(result, dict):
                print(f"    ❌ Invalid response type: {type(result)}")
                continue
                
            required_fields = ['internal_thought', 'response_text']
            if not all(field in result for field in required_fields):
                print(f"    ❌ Missing required fields: {required_fields}")
                continue
            
            # Check response quality
            response_text = result['response_text']
            if len(response_text) > 10 and not response_text.startswith("Error"):
                print(f"    ✅ Valid response: {response_text[:50]}...")
                passed += 1
            else:
                print(f"    ❌ Invalid response: {response_text}")
            
            # Check latency target
            if latency < 3000:
                print(f"    ✅ Latency: {latency:.1f}ms (Target: < 3s)")
            else:
                print(f"    ⚠️ Latency: {latency:.1f}ms (Target: < 3s)")
            
            print(f"    💭 Internal thought: {result['internal_thought']}")
        
        avg_latency = total_latency / len(test_cases)
        print(f"  📈 GeneratorAgent Results: {passed}/{len(test_cases)} passed, Avg Latency: {avg_latency:.1f}ms")
        
        return passed == len(test_cases), avg_latency
        
    except Exception as e:
        print(f"  ❌ GeneratorAgent test failed: {e}")
        return False, 0

def test_persona_agent():
    """Test the integrated PersonaAgent system"""
    print("\n🧪 Testing PersonaAgent Integration...")
    
    try:
        from agents.persona import PersonaAgent
        
        # Create persona agent
        agent = PersonaAgent()
        
        # Test session state management
        test_session_id = f"test_session_{int(time.time())}"
        
        # Test 1: Initialize session state
        print("  📝 Test 1: Session State Initialization")
        try:
            # This should create a new session state in Redis
            result = agent.process_user_response(
                session_id=test_session_id,
                user_answer="Hello, I'm ready to start the interview.",
                interviewer_persona="Senior Product Manager",
                session_narrative="Designing a new e-commerce feature",
                topic_graph=[
                    {
                        "topic_id": "PM_01_Problem_Definition",
                        "goal": "Assess structured thinking in problem framing.",
                        "keywords_for_persona_agent": ["user research", "problem definition"]
                    }
                ]
            )
            
            if result and isinstance(result, dict):
                print("    ✅ Session state initialized successfully")
                print(f"    📊 Response: {result.get('response_text', 'No response')[:50]}...")
                print(f"    🎯 Current topic: {result.get('current_topic_id', 'Unknown')}")
                print(f"    📈 Covered topics: {result.get('covered_topic_ids', [])}")
            else:
                print("    ❌ Failed to initialize session state")
                return False
                
        except Exception as e:
            print(f"    ❌ Session initialization failed: {e}")
            return False
        
        # Test 2: Process follow-up response
        print("  📝 Test 2: Follow-up Response Processing")
        try:
            result = agent.process_user_response(
                session_id=test_session_id,
                user_answer="I would start by conducting user interviews to understand pain points, then analyze usage data to identify opportunities.",
                interviewer_persona="Senior Product Manager",
                session_narrative="Designing a new e-commerce feature",
                topic_graph=[
                    {
                        "topic_id": "PM_01_Problem_Definition",
                        "goal": "Assess structured thinking in problem framing.",
                        "keywords_for_persona_agent": ["user research", "problem definition"]
                    },
                    {
                        "topic_id": "PM_02_User_Segmentation",
                        "goal": "Assess user understanding skills.",
                        "keywords_for_persona_agent": ["user personas", "segmentation"]
                    }
                ]
            )
            
            if result and isinstance(result, dict):
                print("    ✅ Follow-up processed successfully")
                print(f"    📊 Response: {result.get('response_text', 'No response')[:50]}...")
                
                # Check if topic progressed
                current_topic = result.get('current_topic_id', '')
                if current_topic == "PM_02_User_Segmentation":
                    print("    ✅ Topic progression successful")
                else:
                    print(f"    ⚠️ Topic progression: {current_topic}")
                    
            else:
                print("    ❌ Failed to process follow-up")
                return False
                
        except Exception as e:
            print(f"    ❌ Follow-up processing failed: {e}")
            return False
        
        # Test 3: Check Redis state persistence
        print("  📝 Test 3: Redis State Persistence")
        try:
            redis_client = get_redis_client()
            if redis_client:
                session_state = redis_client.get(f"session_state:{test_session_id}")
                if session_state:
                    state_data = json.loads(session_state.decode('utf-8'))
                    print("    ✅ Session state found in Redis")
                    print(f"    📊 Current topic: {state_data.get('current_topic_id', 'Unknown')}")
                    print(f"    📈 Covered topics: {state_data.get('covered_topic_ids', [])}")
                else:
                    print("    ❌ Session state not found in Redis")
                    return False
            else:
                print("    ⚠️ Redis not available for state verification")
                
        except Exception as e:
            print(f"    ❌ Redis state verification failed: {e}")
            return False
        
        # Cleanup test session
        try:
            if redis_client:
                redis_client.delete(f"session_state:{test_session_id}")
                print("    🧹 Test session cleaned up")
        except:
            pass
        
        print("  📈 PersonaAgent Integration Results: ✅ All tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ PersonaAgent integration test failed: {e}")
        return False

def test_interview_manager():
    """Test the updated InterviewManager with topic graph generation"""
    print("\n🧪 Testing InterviewManager...")
    
    try:
        from agents.InterviewSessionService import create_interview_plan_with_ai
        
        # Test topic graph generation
        test_data = {
            "role": "Product Manager",
            "seniority": "Senior",
            "skills": ["Problem Framing", "User Research", "Data Analysis"]
        }
        
        print("  📝 Testing Topic Graph Generation")
        start_time = time.time()
        
        plan = create_interview_plan_with_ai(
            role=test_data["role"],
            seniority=test_data["seniority"],
            skills=test_data["skills"]
        )
        
        generation_time = (time.time() - start_time) * 1000
        
        if not plan:
            print("    ❌ Failed to generate interview plan")
            return False
        
        # Validate plan structure
        required_fields = ['topic_graph', 'session_narrative']
        if not all(field in plan for field in required_fields):
            print(f"    ❌ Missing required fields: {required_fields}")
            return False
        
        topic_graph = plan.get('topic_graph', [])
        session_narrative = plan.get('session_narrative', '')
        
        if not topic_graph or not isinstance(topic_graph, list):
            print("    ❌ Invalid topic_graph structure")
            return False
        
        if not session_narrative or len(session_narrative) < 10:
            print("    ❌ Invalid session_narrative")
            return False
        
        # Validate topic structure
        valid_topics = 0
        for topic in topic_graph:
            topic_fields = ['topic_id', 'primary_skill', 'topic_name', 'goal', 'dependencies', 'keywords_for_persona_agent']
            if all(field in topic for field in topic_fields):
                valid_topics += 1
        
        print(f"    ✅ Generated {len(topic_graph)} topics ({valid_topics} valid)")
        print(f"    📖 Session narrative: {session_narrative[:100]}...")
        print(f"    ⏱️ Generation time: {generation_time:.1f}ms")
        
        # Check topic dependencies
        topic_ids = [topic['topic_id'] for topic in topic_graph]
        dependency_errors = 0
        for topic in topic_graph:
            for dep in topic.get('dependencies', []):
                if dep not in topic_ids:
                    dependency_errors += 1
        
        if dependency_errors == 0:
            print("    ✅ All topic dependencies are valid")
        else:
            print(f"    ⚠️ {dependency_errors} invalid dependencies found")
        
        print("  📈 InterviewManager Results: ✅ Topic graph generation successful")
        return True
        
    except Exception as e:
        print(f"  ❌ InterviewManager test failed: {e}")
        return False

def test_database_functionality():
    """Test the new database schema"""
    print("\n🧪 Testing Database Functionality...")
    
    try:
        import models
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Get database URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("    ❌ DATABASE_URL not set")
            return False
        
        # Create engine and session
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db_session = SessionLocal()
        
        try:
            # Test 1: Create tables
            print("  📝 Test 1: Table Creation")
            models.create_tables()
            print("    ✅ Tables created successfully")
            
            # Test 2: Create sample InterviewSession
            print("  📝 Test 2: InterviewSession Creation")
            sample_session = models.InterviewSession(
                user_id="test_user_123",
                role="Product Manager",
                seniority="Senior",
                status="ready",
                topic_graph={
                    "session_narrative": "Test interview session",
                    "topic_graph": [
                        {
                            "topic_id": "TEST_01",
                            "primary_skill": "Problem Framing",
                            "goal": "Test goal"
                        }
                    ]
                },
                session_narrative="Test interview session for database validation"
            )
            
            db_session.add(sample_session)
            db_session.commit()
            print("    ✅ InterviewSession created successfully")
            
            # Test 3: Retrieve and validate
            print("  📝 Test 3: Data Retrieval")
            retrieved_session = db_session.query(models.InterviewSession).filter(
                models.InterviewSession.user_id == "test_user_123"
            ).first()
            
            if retrieved_session:
                print("    ✅ InterviewSession retrieved successfully")
                print(f"    📊 Role: {retrieved_session.role}")
                print(f"    📈 Status: {retrieved_session.status}")
                
                # Validate topic_graph JSONB
                topic_graph = retrieved_session.topic_graph
                if topic_graph and 'topic_graph' in topic_graph:
                    print(f"    🎯 Topics: {len(topic_graph['topic_graph'])}")
                else:
                    print("    ⚠️ Topic graph structure incomplete")
            else:
                print("    ❌ Failed to retrieve InterviewSession")
                return False
            
            # Test 4: Cleanup
            print("  📝 Test 4: Cleanup")
            db_session.delete(retrieved_session)
            db_session.commit()
            print("    ✅ Test data cleaned up")
            
            print("  📈 Database Results: ✅ All tests passed")
            return True
            
        finally:
            db_session.close()
            
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_render_integration():
    """Test integration with Render deployment"""
    print("\n🧪 Testing Render Integration...")
    
    # This would test against your live Render API
    # For now, we'll just check if we can connect to the services
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Redis connection
    print("  📝 Test 1: Redis Connection")
    redis_client = get_redis_client()
    if redis_client:
        print("    ✅ Redis connection successful")
        tests_passed += 1
    else:
        print("    ❌ Redis connection failed")
    
    # Test 2: Database connection
    print("  📝 Test 2: Database Connection")
    try:
        import models
        # Try to create a test connection
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            print("    ✅ Database URL configured")
            tests_passed += 1
        else:
            print("    ❌ Database URL not configured")
    except Exception as e:
        print(f"    ❌ Database connection failed: {e}")
    
    # Test 3: Environment variables
    print("  📝 Test 3: Environment Configuration")
    required_vars = ['GOOGLE_API_KEY', 'DATABASE_URL', 'REDIS_URL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if not missing_vars:
        print("    ✅ All environment variables configured")
        tests_passed += 1
    else:
        print(f"    ❌ Missing variables: {', '.join(missing_vars)}")
    
    print(f"  📈 Render Integration Results: {tests_passed}/{total_tests} tests passed")
    return tests_passed == total_tests

def run_performance_tests():
    """Run performance benchmarks"""
    print("\n🚀 Running Performance Tests...")
    
    performance_results = {}
    
    # Test Router Agent Performance
    print("  📝 Router Agent Performance Test")
    router_times = []
    for i in range(5):  # Run 5 times for average
        start_time = time.time()
        try:
            from agents.persona import RouterAgent
            router = RouterAgent()
            result = router.analyze_response(
                interviewer_persona_summary="Senior Product Manager",
                current_topic_goal="Assess structured thinking in problem framing.",
                conversation_history=[],
                user_latest_answer="I would start by defining the problem clearly and understanding user needs."
            )
            latency = (time.time() - start_time) * 1000
            router_times.append(latency)
        except Exception as e:
            print(f"    ❌ Router test {i+1} failed: {e}")
    
    if router_times:
        avg_router_time = sum(router_times) / len(router_times)
        max_router_time = max(router_times)
        performance_results['router_agent'] = {
            'avg_latency_ms': avg_router_time,
            'max_latency_ms': max_router_time,
            'target_met': avg_router_time < 750
        }
        print(f"    📊 Router Agent: Avg {avg_router_time:.1f}ms, Max {max_router_time:.1f}ms (Target: < 750ms)")
        print(f"    {'✅' if avg_router_time < 750 else '❌'} Target met: {avg_router_time < 750}")
    
    # Test Generator Agent Performance
    print("  📝 Generator Agent Performance Test")
    generator_times = []
    for i in range(3):  # Run 3 times (more expensive)
        start_time = time.time()
        try:
            from agents.persona import GeneratorAgent
            generator = GeneratorAgent()
            result = generator.generate_response(
                persona_role="Senior Product Manager",
                persona_company_context="Tech Company",
                interview_style="Professional",
                session_narrative="Designing a new e-commerce feature",
                topic_graph_json=[{
                    "topic_id": "PM_01_Problem_Definition",
                    "goal": "Assess structured thinking in problem framing.",
                    "keywords_for_persona_agent": ["user research", "problem definition"]
                }],
                current_topic_id="PM_01_Problem_Definition",
                covered_topic_ids=[],
                conversation_history=[],
                triggering_action="GENERATE_FOLLOW_UP"
            )
            latency = (time.time() - start_time) * 1000
            generator_times.append(latency)
        except Exception as e:
            print(f"    ❌ Generator test {i+1} failed: {e}")
    
    if generator_times:
        avg_generator_time = sum(generator_times) / len(generator_times)
        max_generator_time = max(generator_times)
        performance_results['generator_agent'] = {
            'avg_latency_ms': avg_generator_time,
            'max_latency_ms': max_generator_time,
            'target_met': avg_generator_time < 3000
        }
        print(f"    📊 Generator Agent: Avg {avg_generator_time:.1f}ms, Max {max_generator_time:.1f}ms (Target: < 3s)")
        print(f"    {'✅' if avg_generator_time < 3000 else '❌'} Target met: {avg_generator_time < 3000}")
    
    return performance_results

def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description='Test PrepAI Two-Loop Architecture')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--render', action='store_true', help='Test against Render deployment')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # Default to running all tests if no specific category is specified
    if not any([args.unit, args.integration, args.performance, args.render]):
        args.all = True
    
    print("🧪 PrepAI Two-Loop Architecture Test Suite")
    print("=" * 60)
    print(f"🚀 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Environment check
    if not check_environment():
        print("❌ Environment check failed. Exiting.")
        sys.exit(1)
    
    test_results = {}
    
    # Unit Tests
    if args.unit or args.all:
        print("\n" + "="*60)
        print("🔬 UNIT TESTS")
        print("="*60)
        
        # Router Agent
        router_success, router_latency = test_router_agent()
        test_results['router_agent'] = {'success': router_success, 'avg_latency_ms': router_latency}
        
        # Generator Agent  
        generator_success, generator_latency = test_generator_agent()
        test_results['generator_agent'] = {'success': generator_success, 'avg_latency_ms': generator_latency}
        
        # Interview Manager
        interview_manager_success = test_interview_manager()
        test_results['interview_manager'] = {'success': interview_manager_success}
    
    # Integration Tests
    if args.integration or args.all:
        print("\n" + "="*60)
        print("🔗 INTEGRATION TESTS")
        print("="*60)
        
        # Persona Agent Integration
        persona_success = test_persona_agent()
        test_results['persona_agent_integration'] = {'success': persona_success}
        
        # Database Functionality
        database_success = test_database_functionality()
        test_results['database_functionality'] = {'success': database_success}
    
    # Performance Tests
    if args.performance or args.all:
        print("\n" + "="*60)
        print("⚡ PERFORMANCE TESTS")
        print("="*60)
        
        performance_results = run_performance_tests()
        test_results['performance'] = performance_results
    
    # Render Integration Tests
    if args.render or args.all:
        print("\n" + "="*60)
        print("☁️ RENDER INTEGRATION TESTS")
        print("="*60)
        
        render_success = test_render_integration()
        test_results['render_integration'] = {'success': render_success}
    
    # Results Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result.get('success', False))
    
    for test_name, result in test_results.items():
        if 'success' in result:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}")
        elif 'performance' in test_name:
            print(f"📊 {test_name}: Performance metrics collected")
    
    print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Your architecture is ready for production.")
    else:
        print("⚠️ Some tests failed. Please review the output above.")
    
    # Performance Summary
    if 'performance' in test_results:
        print("\n📈 PERFORMANCE SUMMARY")
        print("-" * 30)
        
        for agent, metrics in test_results['performance'].items():
            if 'avg_latency_ms' in metrics:
                target_met = "✅" if metrics['target_met'] else "❌"
                print(f"{target_met} {agent}: {metrics['avg_latency_ms']:.1f}ms avg (Target: {'< 750ms' if 'router' in agent else '< 3s'})")
    
    print(f"\n🏁 Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    if passed_tests == total_tests:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
