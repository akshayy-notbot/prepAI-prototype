# PrepAI - AI-Powered Interview Preparation Platform

PrepAI is an intelligent interview preparation platform that uses AI to conduct realistic mock interviews, provide personalized feedback, and help users improve their interview skills.

## 🚀 Features

- **AI-Powered Mock Interviews**: Conduct realistic interviews using Google's Gemini AI
- **Real-time Communication**: WebSocket-based real-time interview sessions
- **Personalized Feedback**: AI-generated feedback based on your responses
- **Multiple Interview Types**: Support for various roles and seniority levels
- **Progress Tracking**: Monitor your interview preparation progress
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

- **Frontend**: Vanilla JavaScript with modern CSS
- **Backend**: FastAPI (Python) with WebSocket support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI Integration**: Google Gemini API for intelligent question generation
- **Task Queue**: Celery for background job processing
- **Real-time**: WebSocket connections for live communication

## 📁 Project Structure

```
PrepAI-Prototype/
├── agents/                 # AI agent modules
│   ├── interview_manager.py
│   ├── persona.py
│   └── evaluation.py
├── tests/                  # Test files
├── main.py                 # FastAPI application
├── models.py               # Database models
├── celery_app.py           # Celery configuration
├── app.js                  # Frontend JavaScript
├── index.html              # Main HTML file
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
└── README.md               # This file
```

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for Celery)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/PrepAI-Prototype.git
   cd PrepAI-Prototype
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Set up database**
   ```bash
   python migrate_database.py
   python seed.py
   ```

6. **Start the application**
   ```bash
   uvicorn main:app --reload
   ```

7. **Start Celery worker** (in another terminal)
   ```bash
   celery -A celery_app worker --loglevel=info
   ```

8. **Open your browser**
   Navigate to `http://localhost:8000`

## 🌐 Deployment

### GitHub Setup

1. Create a new repository on GitHub
2. Upload all project files (excluding `venv/` and `.env`)
3. Make sure `.gitignore` is included

### Render Deployment

1. **Connect GitHub Repository**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Environment Variables**
   - `DATABASE_URL`: PostgreSQL connection string (auto-filled from database service)
   - `GOOGLE_API_KEY`: Your Google Gemini API key
   - `PYTHON_VERSION`: 3.11.9

3. **Deploy**
   - Render will automatically use your `render.yaml` configuration
   - The service will build and deploy automatically

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `PYTHON_VERSION` | Python version | Yes |
| `ENVIRONMENT` | Environment (development/production) | No |

### API Endpoints

- `POST /api/start-interview` - Start a new interview session
- `POST /api/submit-answer` - Submit interview answer
- `GET /api/interview-status/{session_id}` - Get interview status
- `WebSocket /ws/{session_id}` - Real-time communication

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/
```

## 📝 API Documentation

Once deployed, visit `/docs` for interactive API documentation powered by Swagger UI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/PrepAI-Prototype/issues) page
2. Create a new issue with detailed information
3. Include error logs and steps to reproduce

## 🔗 Links

- **Live Demo**: [Your Render URL]
- **GitHub Repository**: [Your GitHub URL]
- **Documentation**: [Your Docs URL]

---

**Note**: Make sure to replace `yourusername` with your actual GitHub username and update the live demo URL once deployed on Render.
