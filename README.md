# SayWrite Cloud API

A FastAPI-based local service for text rewriting and speech-to-text transcription using OpenAI.

## Features

- **Text Rewriting**: Rewrite text using OpenAI LLMs with customizable profiles
- **Speech-to-Text**: Transcribe audio files using OpenAI Whisper API
- **API-First Design**: Simple REST API with health checks and structured responses
- **Privacy-Focused**: All processing happens locally, API keys never leave your machine
- **Configurable**: Environment-driven configuration
- **Structured Logging**: JSON logging with optional redaction of sensitive data

## API Endpoints

- `GET /v1/health` - Health check endpoint
- `POST /v1/transcribe` - Transcribe audio to text using Whisper API
- `POST /v1/rewrite` - Rewrite text using LLM with profile-based customization

## Requirements

- Python 3.11+

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/saywrite-cloud.git
   cd saywrite-cloud
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings and API keys
   ```

## Configuration

Configure the service using environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 5175 |
| WHISPER_API_KEY | OpenAI API key for Whisper (falls back to OPENAI_API_KEY if not set) | - |
| WHISPER_MODEL | Whisper model to use | whisper-1 |
| OPENAI_API_KEY | OpenAI API key | - |
| OPENAI_MODEL | OpenAI model to use | gpt-4o-mini |
| ENABLE_REDACTION | Enable redaction of sensitive data in logs | false |
| LOG_LEVEL | Logging level | INFO |

## Running the Service

### Local Development

```bash
uvicorn app.main:app --reload --port 5175
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 5175
```

### Docker

Build and run with Docker:

```bash
docker build -t saywrite-cloud .
docker run -p 5175:5175 --env-file .env saywrite-cloud
```

## API Usage Examples

### Health Check

```bash
curl http://localhost:5175/v1/health
```

### Transcribe Audio

```bash
curl -X POST http://localhost:5175/v1/transcribe \
  -F "audio=@/path/to/audio/file.mp3" \
  -F "language=en"
```

### Rewrite Text

```bash
curl -X POST http://localhost:5175/v1/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "This is a test transcript that needs to be rewritten.",
    "profile": {
      "id": "professional",
      "name": "Professional",
      "tone": "professional and concise",
      "constraints": ["Use active voice", "Be direct"],
      "format": "paragraph",
      "audience": "business professionals",
      "max_words": 100
    },
    "options": {
      "temperature": 0.7
    }
  }'
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.
