# HugDimonXat

<div align="center">
  <img src="frontend/public/logo.png" alt="HugDimonXat Logo" width="200"/>
  <h3>Intelligent Conversational Platform with Voice Capabilities</h3>
  <p>An advanced AI-powered chat application with voice transcription, natural language processing, and multilingual support.</p>

  [![GitHub Stars](https://img.shields.io/github/stars/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/stargazers)
  [![GitHub Issues](https://img.shields.io/github/issues/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/issues)
  [![GitHub Pull Requests](https://img.shields.io/github/issues-pr/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/pulls)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

## 📋 Table of Contents

- [✨ Features](#-features)
- [🖼️ Demo](#-demo)
- [🚀 Quick Start](#-quick-start)
- [📖 Overview](#-overview)
- [🏗️ Architecture](#-architecture)
- [🧠 Tech Stack](#-tech-stack)
- [🤖 AI Stack](#-ai-stack)
- [🛠️ Installation](#-installation)
  - [Prerequisites](#prerequisites)
  - [Setup Steps](#setup-steps)
  - [Configuration](#configuration)
- [▶️ Running the Application](#-running-the-application)
- [📘 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🔍 Monitoring and Metrics](#-monitoring-and-metrics)
- [📦 Media Storage](#-media-storage)
- [🚀 Deployment](#-deployment)
- [❓ Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📚 Additional Documentation](#-additional-documentation)
- [👥 Authors](#-authors)
- [📄 License](#-license)
- [📊 Project Status](#-project-status)
- [📞 Contact](#-contact)

## ✨ Features

- **Voice Transcription**: Record and transcribe voice messages in multiple languages
- **AI-Powered Chat**: Intelligent responses using OpenAI's language models
- **Language Detection**: Automatic detection and processing of multiple languages
- **Retrieval Augmented Generation (RAG)**: Enhanced responses with contextual information
- **Sentiment Analysis**: Analyze the sentiment of user messages
- **Responsive UI**: Modern interface that works across devices
- **Metrics Dashboard**: Real-time monitoring of system performance and health at `/dashboard`

## 🖼️ Demo

*[Add screenshots or GIFs of your application here]*

## 🚀 Quick Start

For those who want to get up and running quickly:

```bash
# Clone the repository
git clone https://github.com/maxkanevskiy/HugDimonXat.git
cd HugDimonXat

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key

# Start all services with a single command
chmod +x *.sh
./start_all_services.sh

# Access the application at http://localhost:5173
```

## 📖 Overview

HugDimonXat is an advanced chat application that integrates voice transcription, natural language processing, and AI-powered conversational capabilities. The project features a microservice architecture that separates frontend, backend, and voice processing services for scalability and maintainability.

## 🏗️ Architecture

HugDimonXat follows a microservice architecture with three main components:

1. **Frontend Service**: React-based user interface
2. **Backend Service**: Flask API with AI processing capabilities
3. **Speech Service**: Voice transcription using Whisper

```
HugDimonXat/
├── backend/               # Flask backend with AI capabilities
│   ├── app/
│   │   ├── ml/            # Machine learning components
│   │   ├── rag/           # Retrieval Augmented Generation
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   └── tests/             # Backend tests
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   └── src/               # React components and logic
├── speech_service/        # Voice transcription service
│   └── transcribe_api.py  # Whisper-based transcription API
├── audio/                 # Storage for audio recordings
├── Dialogs/               # Dialog templates and scripts
├── Prompts/               # AI prompt templates
└── scripts/               # Deployment and utility scripts
```

## 🧠 Tech Stack

### Backend Technologies
- **Flask**: Web framework for the backend API
- **Python 3.8+**: Core programming language
- **OpenAI API**: For advanced language model capabilities
- **Hugging Face Transformers**: For various NLP tasks
- **PyTorch**: Deep learning framework
- **scikit-learn**: For machine learning components
- **NLTK & TextBlob**: For natural language processing
- **pandas & numpy**: For data manipulation
- **langdetect**: For language detection
- **Flask-CORS**: For cross-origin resource sharing
- **Flask-Limiter**: For API rate limiting
- **python-dotenv**: For environment variable management
- **Black & isort**: For code formatting and import sorting
- **mypy**: For static type checking

### Speech Service Technologies
- **faster-whisper**: Optimized implementation of OpenAI's Whisper model
- **Flask**: Web framework for the transcription API

### Frontend Technologies
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and development server
- **TailwindCSS**: Utility-first CSS framework
- **Material-UI**: React component library
- **Jest**: Testing framework
- **ESLint**: Code linting
- **Prettier**: Code formatting

## 🤖 AI Stack

HugDimonXat leverages several AI technologies:

1. **OpenAI GPT Models**: Powers the core conversational capabilities
2. **Whisper**: State-of-the-art speech recognition model for transcription
3. **Retrieval Augmented Generation (RAG)**: Enhances responses with relevant context
4. **Sentiment Analysis**: Analyzes emotional tone of messages
5. **Language Detection**: Identifies the language of user input
6. **Hugging Face Models**: Various NLP tasks including classification and embedding

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git
- OpenAI API key

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/maxkanevskiy/HugDimonXat.git
cd HugDimonXat
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your settings, especially the OPENAI_API_KEY
```

3. **Python environment setup**
```bash
# Create virtual environment at project root
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt

# For development, also install development dependencies
pip install -r requirements-dev.txt
```

4. **Frontend setup**
```bash
cd frontend
npm install
```

### Configuration

The project uses environment variables for configuration. Key variables include:

```ini
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Backend settings
BACKEND_PORT=5001
FLASK_DEBUG=False

# Speech service settings
SPEECH_PORT=5050
AUDIO_DIR=./audio
WHISPER_MODEL_SIZE=small  # Options: tiny, base, small, medium, large
MAX_FILE_SIZE=10485760    # 10MB in bytes
DEFAULT_LANGUAGE=ru       # Default language for transcription

# Frontend settings
VITE_API_URL=http://localhost:5001
```

## ▶️ Running the Application

You can start all services with a single command:

```bash
# Make scripts executable
chmod +x *.sh

# Start all services
./start_all_services.sh
```

This script will:
- Start the backend service on port 5001
- Start the speech service on port 5050
- Start the frontend development server on port 5173

Alternatively, you can start each service individually:

```bash
# Backend
./start_backend_service.sh

# Speech service
./start_transcription_service.sh

# Frontend
./start_frontend_service.sh
```

To stop all services:
```bash
./stop_all_services.sh
```

## 📘 API Documentation

### Backend API

#### Chat Endpoints
- `POST /api/chat`
  - Send a message to the chatbot
  - Request body: `{"message": "Your message here", "conversation_id": "optional-id"}`
  - Response: `{"response": "AI response", "conversation_id": "id"}`

#### Language Processing
- `POST /api/detect-language`
  - Detect the language of a text
  - Request body: `{"text": "Your text here"}`
  - Response: `{"language": "en", "confidence": 0.98}`

#### RAG Endpoints
- `POST /api/rag/query`
  - Query with context enhancement
  - Request body: `{"query": "Your question", "context": "optional context"}`
  - Response: `{"response": "Enhanced response with context"}`

### Speech Service API

#### Transcription
- `POST /transcribe`
  - Transcribe audio to text
  - Request: multipart/form-data with 'audio' file
  - Supported formats: WAV, MP3, WEBM, OGG
  - Response: `{"transcript": "Transcribed text", "language": "detected language"}`

#### Health Check
- `GET /health`
  - Check service status
  - Response: `{"status": "ok", "service": "transcription"}`

## 🧪 Testing

HugDimonXat implements a comprehensive testing strategy across all components of the application to ensure reliability, performance, and correctness.

### Testing Strategy

The project follows a multi-layered testing approach:

- **Unit Testing**: Validates individual functions and classes in isolation
- **Integration Testing**: Verifies interactions between components
- **API Testing**: Ensures API endpoints function correctly
- **Performance Testing**: Benchmarks critical paths for performance optimization
- **Frontend Component Testing**: Validates React components and user interactions

### Backend Testing

The backend uses pytest as the primary testing framework with several specialized plugins:

- **pytest**: Core testing framework
- **pytest-cov**: For code coverage reporting
- **pytest-benchmark**: For performance testing
- **pytest-mock**: For mocking dependencies

#### Test Categories

1. **Unit Tests**
   - Located in `backend/tests/unit/`
   - Test individual functions and classes in isolation
   - Mock external dependencies
   - Run with: `pytest -m unit`

2. **Integration Tests**
   - Located in `backend/tests/integration/`
   - Test interactions between components
   - May use test databases or mock external services
   - Run with: `pytest -m integration`

3. **API Tests**
   - Located in `backend/tests/integration/`
   - Test API endpoints using Flask test client
   - Validate request/response cycles
   - Run with: `pytest -m api`

4. **Performance Tests**
   - Located in `backend/tests/performance/`
   - Benchmark critical paths in the application
   - Set performance baselines
   - Run with: `pytest -m performance`

#### Running Backend Tests

```bash
# Run all backend tests
cd backend
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m api
pytest -m performance

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/unit/test_chat_service.py

# Run a specific test function
pytest tests/unit/test_chat_service.py::TestChatService::test_get_response
```

#### Coverage Reports

```bash
# Generate basic coverage report
cd backend
pytest --cov=app

# Generate detailed HTML coverage report
pytest --cov=app --cov-report=html
# Report will be in htmlcov/index.html

# Generate XML coverage report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Frontend Testing

The frontend uses Jest and React Testing Library for component testing:

- **Jest**: JavaScript testing framework
- **React Testing Library**: For testing React components
- **@testing-library/user-event**: For simulating user interactions
- **ts-jest**: For TypeScript support

#### Running Frontend Tests

```bash
# Run frontend tests in watch mode
cd frontend
npm test

# Run tests with coverage
npm test -- --coverage
```

### Continuous Integration

The project uses CI/CD pipelines to automatically run tests on each commit:

- All tests must pass before merging to main branches
- Coverage reports are generated and tracked
- Performance benchmarks are compared against baselines

### Code Formatting and Quality

The project uses several tools to maintain code quality and consistent formatting:

#### Python Code
- **Black**: Automatic code formatting
- **isort**: Import sorting
- **mypy**: Static type checking

```bash
# Format Python code
black backend/ speech_service/ scripts/

# Sort imports
isort backend/ speech_service/ scripts/

# Run type checking
mypy backend/ speech_service/ scripts/
```

#### Frontend Code
- **Prettier**: Code formatting
- **ESLint**: Code linting

```bash
# Format frontend code
cd frontend
npm run format

# Check if code is properly formatted
npm run format:check

# Run linting
npm run lint
```

### Test Documentation

For more detailed information about testing:

- Backend testing guide: `backend/tests/README.md`
- API test examples: `backend/tests/api_example.py`
- Test fixtures: `backend/tests/conftest.py`

## 🔍 Monitoring and Metrics

The application includes monitoring capabilities:

- **Dashboard**: A comprehensive metrics dashboard available at `http://localhost:5173/dashboard` that provides real-time monitoring of system performance, API usage statistics, and service health status
- **Backend Metrics**: Available at `/metrics` endpoint
- **Log Files**: Generated in the project root directory
- **Error Tracking**: Comprehensive error logging

## 📦 Media Storage

### Current Implementation

HugDimonXat currently implements a simple but functional approach to media storage:

1. **Audio Files**: Voice message recordings are stored in the filesystem:
   - Location: `/audio` directory at the project root
   - Implementation: The transcription service in `speech_service/transcribe_api.py` saves audio files with unique filenames based on timestamps and UUIDs
   - Format: Supports various audio formats (WEBM, MP4, OGG, WAV)

2. **Dialog Data**: Conversation data is stored in-memory:
   - Implementation: Python dictionary called `SESSION_STATE` in `Dialogs/restaurant_script_engine.py`
   - Persistence: In-memory only, not persisted between application restarts

### Best Practices for Production

For a production environment handling thousands of messages daily, the following best practices are recommended:

#### 1. Separate Storage from Application

**Recommendation**: Move media storage to a dedicated storage service.

- **Object Storage**: Use a service like AWS S3, Google Cloud Storage, or Azure Blob Storage
- **Benefits**: Scalability, durability, and separation of concerns
- **Implementation**: Replace direct filesystem writes with API calls to cloud storage

#### 2. Database Integration

**Recommendation**: Store metadata in a database, but not the actual media files.

- **Metadata in Database**: Store file paths, timestamps, user IDs, and transcription results
- **Media in Object Storage**: Store the actual audio files in object storage
- **Hybrid Approach**: For very small audio clips, consider storing them directly in a database that supports binary data efficiently (like PostgreSQL with BYTEA type)

#### 3. Retention Policy

**Recommendation**: Establish a clear retention policy for media files.

- **Time-Based Deletion**: Automatically delete files older than X days
- **Usage-Based Retention**: Keep files that are frequently accessed
- **Legal Compliance**: Ensure retention policies comply with relevant regulations

## 🚀 Deployment

### Production Deployment Options

1. **Cloud Deployment**
   - Deploy backend and speech services as separate instances
   - Use a static hosting service for the frontend
   - Set up environment variables in your cloud provider
   - Configure CORS settings for cross-service communication

2. **Serverless Deployment**
   - Deploy backend functions to AWS Lambda or similar
   - Host frontend on S3 or similar static hosting
   - Use API Gateway for routing

Note: Docker configuration files have been removed from the project. If you wish to use Docker for deployment, you will need to create your own Dockerfile and docker-compose.yml files.

### GitHub Synchronization

The project includes scripts to automatically synchronize changes with a GitHub repository:

```bash
# Set up GitHub synchronization
chmod +x scripts/*.sh
./scripts/setup_github_sync.sh <github_repo_url>
./scripts/push_all_to_github.sh
```

For detailed instructions and troubleshooting, see the [GitHub Synchronization Scripts README](scripts/README.md).

## ❓ Troubleshooting

### Common Issues and Solutions

1. **API Key Issues**
   - **Problem**: "Invalid API key" or "Authentication error" when using OpenAI services
   - **Solution**: Verify your OpenAI API key in the `.env` file and ensure it has sufficient credits

2. **Audio Transcription Problems**
   - **Problem**: Transcription service fails to process audio
   - **Solution**: Check that the audio file format is supported (WAV, MP3, WEBM, OGG) and file size is under the limit (10MB by default)

3. **Frontend Connection Issues**
   - **Problem**: Frontend cannot connect to backend services
   - **Solution**: Verify that all services are running and check CORS settings in the backend

4. **Memory Issues**
   - **Problem**: Application crashes with out-of-memory errors
   - **Solution**: Reduce the Whisper model size in the configuration (try "small" or "base" instead of "medium" or "large")

### Getting Help

If you encounter issues not covered here, please:
1. Check the logs in the terminal where services are running
2. Search for similar issues in the [GitHub Issues](https://github.com/maxkanevskiy/HugDimonXat/issues)
3. Create a new issue with detailed information about your problem

## 🤝 Contributing

We welcome contributions to HugDimonXat! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

Please make sure your code follows our style guidelines and passes all tests.

## 📚 Additional Documentation

- [Voice Recording Guide](VOICE_RECORDING_README.md) - Setup, usage, troubleshooting, and technical details for the voice recording feature
- [Testing Documentation](TESTS.md) - Comprehensive overview of all tests in the project, including backend and frontend tests

## 👥 Authors

- **Max Kanevskiy** - *Initial work and maintenance*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📊 Project Status

[![GitHub Stars](https://img.shields.io/github/stars/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/maxkanevskiy/HugDimonXat)](https://github.com/maxkanevskiy/HugDimonXat/pulls)

## 📞 Contact

Max Kanevskiy - [GitHub Profile](https://github.com/maxkanevskiy)

Project Link: [https://github.com/maxkanevskiy/HugDimonXat](https://github.com/maxkanevskiy/HugDimonXat)