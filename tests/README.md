# PrepAI Tests

This folder contains all test files for the PrepAI system.

## Test Files

### Core Agent Tests
- **`test_evaluation.py`** - Tests the Evaluation Agent (AI-powered answer scoring)
- **`test_persona.py`** - Tests the Persona Agent (AI-powered question generation)
- **`test_interview_manager.py`** - Tests the Interview Manager (AI-powered plan creation)

### Integration Tests
- **`test_api_integration.py`** - Tests the FastAPI endpoints integration

## Running Tests

### Prerequisites
1. Make sure your environment variables are set (especially `GOOGLE_API_KEY`)
2. Install required dependencies: `pip install -r requirements.txt`

### Individual Agent Tests
```bash
# Test Evaluation Agent
python tests/test_evaluation.py

# Test Persona Agent  
python tests/test_persona.py

# Test Interview Manager
python tests/test_interview_manager.py
```

### API Integration Tests
```bash
# Start your FastAPI server first
uvicorn main:app --reload

# Then run the API tests
python tests/test_api_integration.py
```

## Test Structure

Each test file follows a similar pattern:
1. **Setup** - Load environment variables and imports
2. **Test Cases** - Multiple test scenarios with clear output
3. **Error Handling** - Tests for failure cases
4. **Clean Output** - Clear success/failure indicators

## Expected Output

Tests will show:
- ✅ Success indicators for passed tests
- ❌ Error indicators for failed tests
- 📝 Clear test descriptions
- 📊 Detailed results and data

## Troubleshooting

- **Import Errors**: Make sure you're running from the project root directory
- **API Key Errors**: Check your `GOOGLE_API_KEY` environment variable
- **Connection Errors**: Ensure your FastAPI server is running for API tests
