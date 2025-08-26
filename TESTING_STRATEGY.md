# 🧪 Testing Strategy for PrepAI Two-Loop Architecture

## **Overview**
This testing strategy is designed to work with your Render deployment (API, DB & Redis) and minimize local setup requirements. The goal is to provide comprehensive testing coverage for the new two-loop architecture.

## **🎯 Testing Levels**

### **Level 1: Automated Unit Tests (My Responsibility)**
- **What**: Test individual components in isolation
- **Where**: Run automatically during development
- **Coverage**: RouterAgent, GeneratorAgent, PersonaAgent, InterviewManager
- **Output**: Detailed pass/fail reports with performance metrics

### **Level 2: Integration Tests (My Responsibility)**
- **What**: Test component interactions and data flow
- **Where**: Run against your Render infrastructure
- **Coverage**: End-to-end interview flow, Redis state management, PostgreSQL persistence
- **Output**: API response validation and performance benchmarks

### **Level 3: Performance Tests (My Responsibility)**
- **What**: Verify latency targets and scalability
- **Where**: Run against your Render infrastructure
- **Coverage**: Router Agent < 750ms, Generator Agent < 3s
- **Output**: Latency distribution and performance reports

### **Level 4: Manual Validation (Your Responsibility)**
- **What**: Real-world interview simulation
- **Where**: Your live application
- **Coverage**: User experience, edge cases, business logic
- **Output**: Feedback on interview quality and system behavior

## **🚀 Testing Implementation**

### **1. Automated Test Suite (`test_new_architecture.py`)**
```bash
# Run all tests
python3 test_new_architecture.py

# Run specific test categories
python3 test_new_architecture.py --unit
python3 test_new_architecture.py --integration
python3 test_new_architecture.py --performance
```

### **2. Test Categories**

#### **A. Unit Tests (Local/CI)**
- **RouterAgent**: Response classification, latency measurement
- **GeneratorAgent**: Question generation, persona consistency
- **PersonaAgent**: State management, Redis operations
- **InterviewManager**: Topic graph generation, plan creation

#### **B. Integration Tests (Render)**
- **API Endpoints**: Start interview, submit answer, get status
- **Data Flow**: Interview Manager → Topic Graph → Persona Agent
- **State Management**: Redis session state, PostgreSQL persistence
- **Error Handling**: Invalid inputs, network failures, API limits

#### **C. Performance Tests (Render)**
- **Latency Benchmarks**: Router < 750ms, Generator < 3s
- **Concurrency**: Multiple simultaneous interviews
- **Memory Usage**: Redis state management efficiency
- **Database Performance**: PostgreSQL write operations

## **🔧 Testing Infrastructure**

### **Environment Variables Required**
```bash
# Render API
RENDER_API_URL=https://your-api.onrender.com

# Database (PostgreSQL on Render)
DATABASE_URL=postgresql://user:pass@host:port/db

# Redis (Redis on Render)
REDIS_URL=redis://user:pass@host:port

# Gemini API
GOOGLE_API_KEY=your_actual_key
```

### **Test Data Management**
- **Clean State**: Each test starts with fresh database/Redis
- **Isolation**: Tests don't interfere with each other
- **Cleanup**: Automatic cleanup after each test
- **Mocking**: Minimal external dependencies

## **📊 Test Execution Flow**

### **Phase 1: Pre-Test Setup**
1. **Environment Check**: Verify all required services are accessible
2. **Database Reset**: Clean slate for testing
3. **Redis Flush**: Clear any existing session data
4. **API Health Check**: Ensure Render services are responding

### **Phase 2: Test Execution**
1. **Unit Tests**: Fast, isolated component testing
2. **Integration Tests**: End-to-end flow validation
3. **Performance Tests**: Latency and throughput measurement
4. **Error Tests**: Edge case and failure scenario validation

### **Phase 3: Results & Cleanup**
1. **Report Generation**: Detailed pass/fail summary
2. **Performance Metrics**: Latency distribution, success rates
3. **Database Cleanup**: Remove test data
4. **Redis Cleanup**: Clear test sessions

## **🎭 Test Scenarios**

### **1. Happy Path Testing**
- **Complete Interview Flow**: Start → Questions → Complete
- **Topic Progression**: Logical flow through topic graph
- **State Persistence**: Redis → PostgreSQL transition
- **Performance Targets**: Meet latency requirements

### **2. Edge Case Testing**
- **Invalid Inputs**: Malformed requests, missing data
- **Network Issues**: Timeout handling, retry logic
- **Resource Limits**: API rate limits, memory constraints
- **Concurrent Users**: Multiple simultaneous interviews

### **3. Failure Recovery Testing**
- **Service Outages**: Redis/PostgreSQL unavailable
- **API Failures**: Gemini API errors, timeout handling
- **Data Corruption**: Invalid state, corrupted topic graphs
- **Rollback Scenarios**: Failed interview completion

## **📈 Success Metrics**

### **Performance Targets**
- **Router Agent**: P95 < 750ms
- **Generator Agent**: P95 < 3s
- **API Response**: P95 < 2s
- **Database Operations**: < 100ms

### **Reliability Targets**
- **Test Pass Rate**: > 95%
- **Error Handling**: Graceful degradation
- **Data Consistency**: No data loss or corruption
- **State Management**: Accurate session tracking

### **Quality Targets**
- **Interview Flow**: Logical topic progression
- **Question Quality**: Relevant, challenging questions
- **Persona Consistency**: Maintains interviewer character
- **User Experience**: Smooth, realistic conversation

## **🔄 Continuous Testing**

### **Automated Triggers**
- **Code Changes**: Run tests on every commit
- **Deployment**: Pre-deployment validation
- **Scheduled**: Daily health checks
- **Manual**: On-demand testing

### **Test Results**
- **Immediate Feedback**: Pass/fail status
- **Detailed Reports**: Performance metrics, error details
- **Trend Analysis**: Performance over time
- **Alerting**: Failures trigger notifications

## **🚨 Troubleshooting Guide**

### **Common Issues**
1. **Environment Variables**: Missing or incorrect API keys
2. **Network Connectivity**: Render services unreachable
3. **Rate Limits**: API quota exceeded
4. **Data Consistency**: Test data conflicts

### **Debug Steps**
1. **Health Check**: Verify all services are running
2. **Log Analysis**: Check application and test logs
3. **Manual Validation**: Test endpoints manually
4. **Environment Reset**: Clear and reconfigure

## **📋 Next Steps**

### **Immediate Actions**
1. **Review Test Strategy**: Ensure alignment with your needs
2. **Environment Setup**: Configure test environment variables
3. **Test Execution**: Run initial test suite
4. **Results Review**: Analyze performance and reliability

### **Ongoing Maintenance**
1. **Regular Testing**: Automated test execution
2. **Performance Monitoring**: Track latency trends
3. **Test Updates**: Adapt tests to new features
4. **Documentation**: Keep testing procedures current

---

**🎯 Goal**: Ensure your new two-loop architecture is robust, performant, and reliable in production on Render.
