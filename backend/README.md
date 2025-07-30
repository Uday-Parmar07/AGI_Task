# 🤖 AGI Task - AI-Powered PDF Chat Application

A comprehensive full-stack application for intelligent document processing, technical skill extraction, and AI-powered conversations with PDF documents. Built with Flask (backend) and React (frontend).

## 🌟 Features

### 📄 Document Processing
- **Multi-PDF Upload**: Upload and process multiple PDF documents simultaneously
- **Smart Text Extraction**: Extract and chunk text content for optimal AI processing
- **Vector Database Storage**: Store document embeddings in Pinecone for semantic search
- **Session Management**: Organize documents by user sessions

### 🧠 AI-Powered Information Extraction
- **Comprehensive User Information Extraction**:
  - Full Name and Contact Details
  - Email Address and Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Educational Background
  - Work Experience
- **Ultra-Aggressive Tech Stack Detection**:
  - Programming Languages (Python, JavaScript, C++, Java, etc.)
  - Frameworks and Libraries (React, Flask, Django, Spring, etc.)
  - Databases (MySQL, PostgreSQL, MongoDB, etc.)
  - Tools and Platforms (Docker, AWS, Git, etc.)
  - Explicit skills section parsing
  - Experience-based technology extraction

### 💼 Technical Interview Assistance
- **Adaptive Question Generation**: Create technical interview questions based on extracted skills
- **Multiple Difficulty Levels**: Easy, Medium, and Hard question sets
- **Technology-Specific Questions**: Tailored questions for specific tech stacks
- **Interview Tips and Guidelines**: Best practices for technical interviews

### 💬 Intelligent Chat Interface
- **Context-Aware Conversations**: Ask questions about uploaded documents
- **Session-Based Chat**: Maintain conversation history within sessions
- **Real-time Responses**: Powered by Google Gemini AI model
- **Formatted Responses**: Rich text formatting with lists, code blocks, and structured content

### 📊 Advanced History Management
- **Session Overview**: View all chat sessions with metadata
- **Interactive Session Cards**: Click-to-view detailed history
- **Conversation Tracking**: Complete question-answer pairs with timestamps
- **Cross-Session Navigation**: Switch between different chat sessions
- **Responsive History UI**: Beautiful card-based design for all devices

### 🔐 User Authentication & Security
- **User Registration and Login**: Secure user account management
- **Session-Based Security**: Protected API endpoints
- **Data Isolation**: User-specific data separation
- **CORS Configuration**: Secure cross-origin requests

## 🏗️ Architecture

### Backend (Flask)
- **RESTful API**: Clean, organized endpoint structure
- **Modular Design**: Separated services, models, and routes
- **Vector Search**: Pinecone integration for semantic search
- **AI Integration**: Google Gemini AI model
- **Database**: SQLite for user and session management

### Frontend (React)
- **Modern React**: Hooks-based functional components
- **Responsive Design**: Mobile-first CSS with flexbox/grid
- **Real-time Updates**: Dynamic state management
- **Interactive UI**: Smooth transitions and hover effects
- **File Upload**: Drag-and-drop PDF upload interface

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Google AI API Key** (for Gemini)
- **Pinecone API Key** (for vector database)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AGI_Task
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `backend/` directory:

```env
# Google AI Configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Pinecone Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=pdf
PINECONE_ENVIRONMENT=us-east-1

# Flask Configuration
SECRET_KEY=your-secure-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=true

# Database Configuration
DATABASE_URL=sqlite:///chat_pdf.db

# Upload Settings
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=16777216
```

#### Start the Backend Server
```bash
# From the project root directory
cd AGI_Task
python backend/app.py
```

The backend will start on `http://localhost:5000`

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd frontend/client
npm install
```

#### Start the Frontend Development Server
```bash
npm start
```

The frontend will start on `http://localhost:3000` (or next available port)

### 4. Access the Application

1. Open your browser and navigate to `http://localhost:3000`
2. Register a new account or login
3. Create a new session
4. Upload PDF documents
5. Start chatting and explore the history feature!

## 📱 How to Use

### Getting Started
1. **Register/Login**: Create an account or login with existing credentials
2. **Create Session**: Click "Create Session" to start a new chat session
3. **Upload Documents**: Select and upload one or more PDF files
4. **Wait for Processing**: Documents will be processed and stored in the vector database

### Core Features

#### Document Analysis
- **Extract User Info**: Get comprehensive user information from resumes
- **Extract Tech Stack**: Identify all technical skills and technologies
- **Generate Questions**: Create technical interview questions based on skills

#### Chat Interface
- **Ask Questions**: Type questions about the uploaded documents
- **View Responses**: Get AI-powered answers with proper formatting
- **Continue Conversations**: Build upon previous questions and answers

#### History Management
- **Switch to History View**: Click "History View" in the sidebar
- **Browse Sessions**: See all your chat sessions as interactive cards
- **View Session Details**: Click on any session card to see full conversation history
- **Session Information**: See creation date, document count, and session ID
- **Return to Chat**: Click "Chat View" to return to active conversation

### Advanced Usage

#### Technical Question Generation
1. Upload a technical resume
2. Click "Extract Tech Stack"
3. Click "Generate Questions"
4. Choose difficulty level (Easy/Medium/Hard)
5. Review generated interview questions

#### Multi-Session Management
1. Use "New Session" to start fresh conversations
2. Upload different documents in different sessions
3. Use History View to switch between sessions
4. Each session maintains its own document context

## 🔧 API Reference

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword"
}
```

### Session Management

#### Create Session
```http
POST /api/sessions/create
Content-Type: application/json

{
  "user_id": "user_uuid",
  "session_name": "Resume Analysis Session"
}
```

### Document Management

#### Upload Documents
```http
POST /api/documents/upload
Content-Type: multipart/form-data

files: [file1.pdf, file2.pdf]
user_id: user_uuid
session_id: session_uuid
```

#### Clear Session Documents
```http
POST /api/documents/clear
Content-Type: application/json

{
  "user_id": "user_uuid",
  "session_id": "session_uuid"
}
```

### Information Extraction

#### Extract User Information
```http
POST /api/extract/user-info
Content-Type: application/json

{
  "user_id": "user_uuid",
  "session_id": "session_uuid"
}
```

#### Extract Tech Stack
```http
POST /api/extract/tech-stack
Content-Type: application/json

{
  "user_id": "user_uuid",
  "session_id": "session_uuid"
}
```

### Question Generation

#### Generate Technical Questions
```http
POST /api/questions/generate
Content-Type: application/json

{
  "tech_stack": "Python, React, PostgreSQL, Docker",
  "difficulty": "medium"
}
```

### Chat Interface

#### Ask Question
```http
POST /api/chat/ask
Content-Type: application/json

{
  "question": "What programming languages does the candidate know?",
  "user_id": "user_uuid",
  "session_id": "session_uuid"
}
```

### History Management

#### Get User Sessions
```http
GET /api/history/sessions?user_id=user_uuid
```

#### Get Chat History
```http
GET /api/history/chat?user_id=user_uuid&session_id=session_uuid
```

## 🏢 Project Structure

```
AGI_Task/
├── 📁 backend/                    # Flask Backend Application
│   ├── 📁 app/                    # Main application package
│   │   ├── 📁 database/           # Database configuration
│   │   │   ├── connection.py      # Database connection setup
│   │   │   └── schemas.py         # Database schemas
│   │   ├── 📁 models/             # Data models
│   │   │   ├── user.py           # User model
│   │   │   ├── chat_session.py   # Chat session model
│   │   │   ├── message.py        # Message model
│   │   │   ├── document.py       # Document model
│   │   │   └── summary.py        # Summary model
│   │   ├── 📁 routes/             # API route handlers
│   │   │   ├── chat.py           # Chat-related routes
│   │   │   ├── document.py       # Document handling routes
│   │   │   └── history.py        # History management routes
│   │   ├── 📁 services/           # Business logic services
│   │   │   ├── ai_service.py     # AI/LLM integration
│   │   │   ├── pdf_service.py    # PDF processing
│   │   │   ├── vector_service.py # Vector database operations
│   │   │   └── data_service.py   # Data management
│   │   └── 📁 utils/              # Utility functions
│   │       ├── auth_utils.py     # Authentication utilities
│   │       ├── file_utils.py     # File handling utilities
│   │       └── pinecone_utils.py # Pinecone configuration
│   ├── 📁 instance/               # Instance-specific files
│   │   └── chat_pdf.db           # SQLite database
│   ├── 📁 uploads/               # Uploaded files storage
│   ├── .env                      # Environment variables
│   ├── app.py                    # Main Flask application
│   └── requirements.txt          # Python dependencies
├── 📁 frontend/                   # React Frontend Application
│   └── 📁 client/                # React app
│       ├── 📁 public/            # Static assets
│       ├── 📁 src/               # Source code
│       │   ├── App.jsx           # Main application component
│       │   ├── App.css           # Application styles
│       │   ├── AuthComponent.jsx # Authentication component
│       │   ├── index.js          # Application entry point
│       │   └── index.css         # Global styles
│       ├── package.json          # Node dependencies
│       └── package-lock.json     # Lock file
├── .gitignore                    # Git ignore rules
├── LICENSE                       # Project license
└── requirements.txt              # Root Python dependencies
```

## 🛠️ Technology Stack

### Backend Technologies
- **Flask 2.3+**: Modern Python web framework
- **LangChain**: AI/LLM integration framework
- **Google Generative AI**: Gemini model integration
- **Pinecone**: Vector database for semantic search
- **SQLite**: Lightweight database for user data
- **PyPDF2/PyMuPDF**: PDF processing libraries
- **Flask-CORS**: Cross-origin resource sharing
- **Python-dotenv**: Environment variable management

### Frontend Technologies
- **React 18+**: Modern JavaScript library
- **Axios**: HTTP client for API requests
- **CSS3**: Modern styling with flexbox/grid
- **HTML5**: Semantic markup
- **JavaScript ES6+**: Modern JavaScript features

### AI & ML Technologies
- **Google Gemini**: Advanced language model
- **Vector Embeddings**: Document similarity search
- **Semantic Search**: Context-aware information retrieval
- **Natural Language Processing**: Text analysis and extraction

### Infrastructure
- **Node.js**: JavaScript runtime for frontend
- **npm**: Package manager for frontend dependencies
- **pip**: Python package manager
- **Git**: Version control system

## 🔧 Configuration

### Environment Variables

#### Required Variables
```env
GOOGLE_API_KEY=          # Google AI API key for Gemini model
PINECONE_API_KEY=        # Pinecone vector database API key
PINECONE_INDEX_NAME=pdf  # Pinecone index name
PINECONE_ENVIRONMENT=    # Pinecone environment (e.g., us-east-1)
```

#### Optional Variables
```env
SECRET_KEY=              # Flask secret key (auto-generated if not set)
FLASK_ENV=development    # Flask environment mode
FLASK_DEBUG=true         # Enable Flask debug mode
DATABASE_URL=            # Database connection string (SQLite default)
UPLOAD_FOLDER=uploads    # Upload directory path
MAX_FILE_SIZE=16777216   # Max file size in bytes (16MB default)
PORT=5000               # Backend server port
```

### API Keys Setup

#### Google AI API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing
3. Generate an API key
4. Add to `.env` file as `GOOGLE_API_KEY`

#### Pinecone API Key
1. Sign up at [Pinecone](https://www.pinecone.io/)
2. Create a new project
3. Create an index named "pdf"
4. Get your API key from the dashboard
5. Add to `.env` file as `PINECONE_API_KEY`

## 🔍 Troubleshooting

### Common Issues

#### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'X'`
```bash
# Solution: Install missing dependencies
pip install -r requirements.txt
```

**Issue**: `Error: Google API key not found`
```bash
# Solution: Check .env file configuration
# Ensure GOOGLE_API_KEY is set correctly
```

**Issue**: `Pinecone authentication failed`
```bash
# Solution: Verify Pinecone configuration
# Check PINECONE_API_KEY and PINECONE_INDEX_NAME
```

**Issue**: `Port 5000 already in use`
```bash
# Solution: Change port in app.py or kill existing process
# For Windows:
netstat -ano | findstr :5000
taskkill /F /PID <process_id>

# For macOS/Linux:
lsof -i :5000
kill -9 <process_id>
```

#### Frontend Issues

**Issue**: `npm: command not found`
```bash
# Solution: Install Node.js from https://nodejs.org/
```

**Issue**: `CORS policy error`
```bash
# Solution: Ensure backend is running and CORS is configured
# Check backend/app.py CORS settings
```

**Issue**: `Module not found: Can't resolve 'X'`
```bash
# Solution: Install missing npm packages
cd frontend/client
npm install
```

#### File Upload Issues

**Issue**: `File too large`
```bash
# Solution: Check MAX_FILE_SIZE in .env
# Increase value if needed (in bytes)
```

**Issue**: `Upload failed`
```bash
# Solution: Check upload directory permissions
# Ensure uploads/ directory exists and is writable
```

### Debug Mode

Enable debug mode for detailed error information:

```env
FLASK_DEBUG=true
FLASK_ENV=development
```

### Logging

Check console output for detailed logs:
- Backend: Terminal running `python backend/app.py`
- Frontend: Terminal running `npm start`
- Browser: Developer Tools Console (F12)

## 🧪 Testing

### Backend Testing
```bash
# Test API endpoints
cd backend
python -c "from app.services.ai_service import AIService; ai = AIService(); print('AI Service initialized successfully')"
```

### Frontend Testing
```bash
# Check React compilation
cd frontend/client
npm run build
```

### End-to-End Testing
1. Start both backend and frontend
2. Register a new user account
3. Upload a PDF document
4. Extract user information
5. Generate technical questions
6. Test chat functionality
7. Verify history feature

## 🔐 Security Considerations

### Production Deployment

#### Environment Variables
- Use strong, unique `SECRET_KEY`
- Secure API keys (never commit to version control)
- Use environment-specific configurations

#### File Upload Security
- Validate file types (PDF only)
- Implement file size limits
- Scan uploaded files for malware
- Use secure file storage

#### API Security
- Implement rate limiting
- Add request validation
- Use HTTPS in production
- Implement proper authentication tokens

#### Database Security
- Use PostgreSQL for production (instead of SQLite)
- Implement database connection pooling
- Use database migrations
- Regular backups

## 📈 Performance Optimization

### Backend Optimization
- Implement caching for frequently accessed data
- Use database connection pooling
- Optimize vector search queries
- Implement async processing for large files

### Frontend Optimization
- Implement code splitting
- Use React.memo for expensive components
- Optimize bundle size
- Implement lazy loading

### Infrastructure
- Use CDN for static assets
- Implement load balancing
- Use Redis for session storage
- Monitor performance metrics

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Backend: Follow PEP 8 Python style guide
- Frontend: Use Prettier for code formatting
- Comments: Document complex logic
- Testing: Write tests for new features

### Bug Reports
Please include:
- Operating system and version
- Python/Node.js versions
- Steps to reproduce
- Expected vs actual behavior
- Console/log output

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI**: For providing the Gemini language model
- **Pinecone**: For vector database services
- **React Team**: For the amazing frontend framework
- **Flask Team**: For the lightweight backend framework
- **LangChain**: For AI/LLM integration tools

## 📞 Support

For support and questions:
- Check the troubleshooting section above
- Review console logs for error details
- Ensure all environment variables are properly configured
- Verify API keys are valid and have sufficient quota

---

**Happy coding! 🚀**
