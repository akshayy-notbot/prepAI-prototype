# 🚀 PrepAI Prompt Optimizer

A real-time tool for testing and optimizing your case study and behavioral interview prompts using the Gemini API.

## ✨ Features

- **Real-time Testing**: Test your prompts instantly without code changes
- **Gemini API Integration**: Uses your actual Gemini API through the backend
- **Prompt Templates**: Built-in case study and behavioral prompt templates
- **Local Storage**: Save and load your custom prompt versions
- **Dynamic Skills Management**: Add/remove skills with clickable tags
- **Instant Feedback**: See AI-generated interview structures in real-time

## 🚀 Quick Start

### 1. Backend Setup
```bash
# Option A: Local Development
cd /path/to/your/PrepAI-Prototype
python main.py

# Option B: Use Render Deployment (Recommended)
# Your backend is already running at: https://prepai-api.onrender.com
```

### 2. Open the Tool
```bash
# Open the HTML file in your browser
open prompt_optimizer.html
```

### 3. Configure Parameters
- **Role**: Set the interview role (e.g., Software Engineer, Product Manager)
- **Seniority**: Choose the level (Junior, Senior, Staff, Principal)
- **Primary Focus Skill**: Set the main skill to assess
- **Core Skills**: Add/remove skills to test

### 4. Test Your Prompts
- Select prompt type (Case Study or Behavioral)
- Edit the prompt template as needed
- Click "Generate Interview Structure"
- See real Gemini API responses instantly

## 🔧 How It Works

1. **Frontend**: HTML interface for prompt editing and testing
2. **Backend**: FastAPI endpoint (`/create-interview-plan`) that calls Gemini API
3. **Environment Detection**: Automatically detects local vs Render deployment
4. **API Health Check**: Verifies backend connectivity before testing
5. **AI Generation**: Your custom prompts are sent to Gemini through the backend
6. **Real-time Results**: JSON interview structures are displayed immediately

## 📝 API Endpoint

The tool calls your backend at:
```
POST /create-interview-plan
```

**Request Body:**
```json
{
  "role": "Software Engineer",
  "seniority": "Senior", 
  "skills": ["System Design", "Problem Solving"],
  "custom_prompt": "Your custom prompt text here..."
}
```

**Response:**
```json
{
  "session_narrative": "...",
  "case_study_details": {...},
  "topic_graph": [...]
}
```

## 🎯 Use Cases

### Case Study Prompts
- Test different narrative structures
- Optimize problem complexity for seniority levels
- Refine question patterns and probing questions
- Iterate on company scenarios and business contexts

### Behavioral Prompts  
- Test STAR method implementation
- Optimize competency frameworks
- Refine follow-up question strategies
- Iterate on seniority calibration

## 💡 Tips for Optimization

1. **Start with Default Templates**: Use the built-in templates as a starting point
2. **Test Different Seniorities**: See how prompts adapt to different levels
3. **Iterate on Skills**: Test how different skill combinations affect output
4. **Save Versions**: Use local storage to keep your best prompt versions
5. **Compare Results**: Test multiple prompt variations to see differences

## 🔍 Troubleshooting

### Backend Not Running
- **Local Development**: Ensure your FastAPI server is running on `http://localhost:8000`
- **Render Deployment**: Your backend is automatically available at `https://prepai-api.onrender.com`
- Check console for any error messages
- The tool automatically detects environment and shows API status

### API Errors
- Verify your Gemini API key is configured
- Check backend logs for detailed error information

### Prompt Issues
- Ensure all placeholders are properly formatted
- Check that prompts generate valid JSON responses

## 🚀 Next Steps

1. **Test Default Prompts**: Start with the built-in templates
2. **Customize for Your Needs**: Modify prompts for your specific use cases
3. **Iterate Rapidly**: Use the tool to quickly test variations
4. **Save Best Versions**: Keep your optimized prompts for production use

## 📁 Files

- `prompt_optimizer.html` - Main tool interface
- `main.py` - Backend API endpoint (already added)
- `prompts/case_study_prompt.txt` - Case study template
- `prompts/behavioral_prompt.txt` - Behavioral template

---

**Happy Prompt Optimizing! 🎉**
