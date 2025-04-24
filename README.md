# DelightMate Backend

A Flask-based backend for the DelightMate AI assistant platform that provides voice interaction tools and AI agent capabilities.

## Features

- Speech-to-Text using OpenAI Whisper API
- Text-to-Speech using ElevenLabs API
- AI Agent interactions using GPT-4

## API Endpoints

### POST /api/stt
Convert audio to text using OpenAI Whisper.
- Request: `multipart/form-data` with an audio file
- Response: JSON with transcribed text

### POST /api/tts
Convert text to speech using ElevenLabs.
- Request: JSON with text to convert
- Response: Audio stream (MP3)

### POST /api/agent
Interact with GPT-4 powered agent.
- Request: JSON with transcript and optional context
- Response: JSON with AI response and any actions

## Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- ElevenLabs API key

### Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/delightmate_backend.git
cd delightmate_backend
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
FLASK_ENV=development
FLASK_APP=run.py
```

## Running the Application

1. From the project root (delightmate_backend folder):
```
python run.py
```

2. Or using Flask CLI:
```
flask run
```

3. Visit http://localhost:5000 in your browser to see the welcome page.

## Test the API Endpoints

You can test the API endpoints with tools like Postman or curl:

### Example: Testing the Agent API
```bash
curl -X POST http://localhost:5000/api/agent \
     -H "Content-Type: application/json" \
     -d '{"transcript": "What is the weather like today?"}'
```

## Project Structure
```
delightmate_backend/
  ├── app/                           # Application package
  │   ├── templates/                 # HTML templates 
  │   ├── main.py                    # Flask app entry point
  │   ├── routes/                    # API routes
  │   │   ├── voice.py               # STT/TTS endpoints
  │   │   └── agent.py               # Agent endpoints
  │   ├── services/                  # Service integrations
  │   │   ├── whisper.py             # OpenAI Whisper
  │   │   ├── elevenlabs.py          # ElevenLabs TTS
  │   │   └── chat_agent.py          # GPT-4 agent
  │   └── utils/                     # Utilities
  │       └── helpers.py             # Helper functions
  ├── .env                           # Environment variables
  ├── run.py                         # Application entry point
  ├── requirements.txt               # Dependencies
  └── README.md                      # Documentation
```

## Future Enhancements

- Calendar integration
- Email integration
- CRM actions
- Multi-user support
- Persistent conversation history 