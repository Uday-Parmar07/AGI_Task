#!/usr/bin/env python3
"""
Main Flask Application for AGI Task Backend
This file serves as the entry point for the Flask backend application.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Import our services and models
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService
from app.services.vector_service import VectorService
from app.services.data_service import DataService
from app.routes.document import DocumentRouter
from app.routes.chat import ChatRouter
from app.routes.history import HistoryRouter
from app.models.chat_session import ChatSessionModel
from app.models.user import UserModel
from app.database.connection import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    
    # Enable CORS for all domains and routes
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize services
    ai_service = AIService()
    document_router = DocumentRouter()
    chat_router = ChatRouter()
    history_router = HistoryRouter()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'AGI Task Backend is running',
            'version': '1.0.0'
        })
    
    # Authentication endpoints
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """User registration"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            if not all([username, email, password]):
                return jsonify({'error': 'Username, email, and password are required'}), 400
            
            # Create user (implement in UserModel)
            user = UserModel.create_user(username=username, email=email, password=password)
            
            return jsonify({
                'message': 'User registered successfully',
                'user_id': user.id
            }), 201
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """User login"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            if not all([username, password]):
                return jsonify({'error': 'Username and password are required'}), 400
            
            # Authenticate user (implement in UserModel)
            user = UserModel.authenticate_user(username=username, password=password)
            
            if not user:
                return jsonify({'error': 'Invalid credentials'}), 401
            
            return jsonify({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            }), 200
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Session management endpoints
    @app.route('/api/sessions/create', methods=['POST'])
    def create_session():
        """Create a new chat session"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            session_name = data.get('session_name', 'New Session')
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            session = ChatSessionModel.create_session(user_id=user_id, title=session_name)
            
            # Save session to database
            from app.database.connection import save_session_to_db
            saved = save_session_to_db(user_id, session.id, session.title)
            
            if not saved:
                logger.warning("Failed to save session to database, but continuing")
            
            return jsonify({
                'message': 'Session created successfully',
                'session_id': session.id,
                'session_name': session.title
            }), 201
            
        except Exception as e:
            logger.error(f"Session creation error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Document management endpoints
    @app.route('/api/documents/upload', methods=['POST'])
    def upload_documents():
        """Upload PDF documents"""
        try:
            user_id = request.form.get('user_id')
            session_id = request.form.get('session_id')
            
            if not all([user_id, session_id]):
                return jsonify({'error': 'User ID and Session ID are required'}), 400
            
            if 'files' not in request.files:
                return jsonify({'error': 'No files uploaded'}), 400
            
            files = request.files.getlist('files')
            
            if not files or all(file.filename == '' for file in files):
                return jsonify({'error': 'No files selected'}), 400
            
            # Process uploaded files
            result = document_router.upload_documents(
                uploaded_files=files,
                user_id=user_id,
                session_id=session_id,
                base_upload_dir=app.config['UPLOAD_FOLDER']
            )
            
            return jsonify({'message': result}), 200
            
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/documents/clear', methods=['POST'])
    def clear_documents():
        """Clear all documents for a session"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not all([user_id, session_id]):
                return jsonify({'error': 'User ID and Session ID are required'}), 400
            
            result = document_router.clear_session_documents(
                user_id=user_id,
                session_id=session_id,
                base_upload_dir=app.config['UPLOAD_FOLDER']
            )
            
            return jsonify({'message': result}), 200
            
        except Exception as e:
            logger.error(f"Document clear error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Information extraction endpoints
    @app.route('/api/extract/user-info', methods=['POST'])
    def extract_user_info():
        """Extract user information from uploaded documents"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not all([user_id, session_id]):
                return jsonify({'error': 'User ID and Session ID are required'}), 400
            
            # Get namespace for this session's documents
            doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
            
            # Extract user information
            result = ai_service.extract_user_information(doc_namespace)
            
            return jsonify({'extracted_info': result}), 200
            
        except Exception as e:
            logger.error(f"User info extraction error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/extract/tech-stack', methods=['POST'])
    def extract_tech_stack():
        """Extract tech stack from uploaded documents"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not all([user_id, session_id]):
                return jsonify({'error': 'User ID and Session ID are required'}), 400
            
            # Get namespace for this session's documents
            doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
            
            # Extract tech stack
            result = ai_service.extract_tech_stack_only(doc_namespace)
            
            return jsonify({'tech_stack': result}), 200
            
        except Exception as e:
            logger.error(f"Tech stack extraction error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Technical questions generation endpoint
    @app.route('/api/questions/generate', methods=['POST'])
    def generate_technical_questions():
        """Generate technical questions based on tech stack"""
        try:
            data = request.get_json()
            tech_stack = data.get('tech_stack')
            difficulty = data.get('difficulty', 'medium')
            
            if not tech_stack:
                return jsonify({'error': 'Tech stack is required'}), 400
            
            # Validate difficulty
            valid_difficulties = ['easy', 'medium', 'hard']
            if difficulty.lower() not in valid_difficulties:
                return jsonify({'error': f'Invalid difficulty. Choose from: {", ".join(valid_difficulties)}'}), 400
            
            # Generate questions
            result = ai_service.generate_technical_questions(tech_stack, difficulty)
            
            return jsonify({'questions': result}), 200
            
        except Exception as e:
            logger.error(f"Question generation error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Chat endpoints
    @app.route('/api/chat/ask', methods=['POST'])
    def ask_question():
        """Ask a question about the uploaded documents"""
        try:
            data = request.get_json()
            question = data.get('question')
            user_id = data.get('user_id')
            session_id = data.get('session_id')
            
            if not all([question, user_id, session_id]):
                return jsonify({'error': 'Question, User ID, and Session ID are required'}), 400
            
            # Get answer from chat router
            result = chat_router.ask_question(question, user_id, session_id)
            
            return jsonify({'answer': result}), 200
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # History endpoints
    @app.route('/api/history/sessions', methods=['GET'])
    def get_user_sessions():
        """Get all sessions for a user"""
        try:
            user_id = request.args.get('user_id')
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            sessions = history_router.get_all_user_sessions(user_id)
            logger.info(f"Found {len(sessions)} sessions for user {user_id}")
            
            return jsonify({'sessions': sessions}), 200
            
        except Exception as e:
            logger.error(f"Get sessions error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/history/chat', methods=['GET'])
    def get_chat_history():
        """Get chat history for a user and optional session"""
        try:
            user_id = request.args.get('user_id')
            session_id = request.args.get('session_id')
            
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            logger.info(f"Getting chat history for user {user_id}, session {session_id}")
            history = history_router.get_chat_history(user_id, session_id)
            logger.info(f"Found {len(history)} chat history items")
            
            return jsonify({'history': history}), 200
            
        except Exception as e:
            logger.error(f"Get chat history error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/debug/chat-messages', methods=['GET'])
    def debug_chat_messages():
        """Debug endpoint to see raw chat messages in namespace"""
        try:
            user_id = request.args.get('user_id')
            session_id = request.args.get('session_id')
            
            if not user_id or not session_id:
                return jsonify({'error': 'User ID and Session ID are required'}), 400
            
            from app.models.chat_session import ChatSessionModel
            chat_namespace = ChatSessionModel.get_chat_namespace(user_id, session_id)
            
            # Get raw documents from vector service
            docs = ai_service.vector_service.get_chat_history(chat_namespace, k=100)
            
            debug_data = []
            for doc in docs:
                debug_data.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata if hasattr(doc, 'metadata') else {},
                    'content_length': len(doc.page_content)
                })
            
            return jsonify({
                'namespace': chat_namespace,
                'total_messages': len(debug_data),
                'messages': debug_data
            }), 200
            
        except Exception as e:
            logger.error(f"Debug chat messages error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    logger.info("Starting AGI Task Backend...")
    
    # Check environment variables
    required_env_vars = ['GOOGLE_API_KEY', 'PINECONE_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Some features may not work properly.")
    
    # Run the application
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    
    logger.info(f"Starting server on port {port} (debug={debug_mode})")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
