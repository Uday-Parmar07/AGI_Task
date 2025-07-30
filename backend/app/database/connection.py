import os
import time
import sqlite3
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat_pdf.db")
DATABASE_PATH = DATABASE_URL.replace("sqlite:///", "").replace("sqlite://", "")

# Pinecone environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

# Initialize Pinecone
try:
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=PINECONE_API_KEY)
except ImportError:
    print("⚠ Pinecone not installed. Vector operations will not work.")
    pc = None
    ServerlessSpec = None
except Exception as e:
    print(f"⚠ Pinecone initialization failed: {e}")
    pc = None
    ServerlessSpec = None

# === SQLite Database Initialization ===
def init_db():
    """Initialize SQLite database with required tables"""
    try:
        # Ensure the directory exists
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                password_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chat_sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                chat_session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                chat_session_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        # Create summaries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                chat_session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (chat_session_id) REFERENCES chat_sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ SQLite database initialized successfully")
        return True
        
    except Exception as e:
        print(f"✗ SQLite database initialization failed: {e}")
        return False

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        return None

def get_user_sessions_from_db(user_id: str):
    """Get all sessions for a user from the database with document counts"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        
        # Get sessions with document counts
        cursor.execute('''
            SELECT 
                cs.id,
                cs.session_name,
                cs.created_at,
                cs.updated_at,
                COUNT(d.id) as document_count
            FROM chat_sessions cs
            LEFT JOIN documents d ON cs.id = d.chat_session_id
            WHERE cs.user_id = ?
            GROUP BY cs.id, cs.session_name, cs.created_at, cs.updated_at
            ORDER BY cs.updated_at DESC
        ''', (user_id,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "session_id": row["id"],
                "title": row["session_name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "document_count": row["document_count"]
            })
        
        conn.close()
        return sessions
        
    except Exception as e:
        print(f"✗ Failed to get user sessions: {e}")
        return []

def get_session_document_count(session_id: str) -> int:
    """Get the number of documents in a session"""
    try:
        conn = get_db_connection()
        if not conn:
            return 0
        
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM documents WHERE chat_session_id = ?', (session_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result["count"] if result else 0
        
    except Exception as e:
        print(f"✗ Failed to get document count: {e}")
        return 0

def save_document_to_db(user_id: str, chat_session_id: str, filename: str, file_path: str) -> bool:
    """Save a document record to the database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        document_id = str(__import__('uuid').uuid4())
        
        cursor.execute('''
            INSERT INTO documents (id, user_id, chat_session_id, filename, file_path, uploaded_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (document_id, user_id, chat_session_id, filename, file_path))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to save document: {e}")
        return False

def save_session_to_db(user_id: str, session_id: str, session_name: str) -> bool:
    """Save a chat session to the database"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if session already exists
        cursor.execute('SELECT id FROM chat_sessions WHERE id = ?', (session_id,))
        if cursor.fetchone():
            # Session exists, just update the timestamp
            cursor.execute('''
                UPDATE chat_sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (session_id,))
        else:
            # Create new session
            cursor.execute('''
                INSERT INTO chat_sessions (id, user_id, session_name, created_at, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (session_id, user_id, session_name))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Failed to save session: {e}")
        return False

# === Environment Validation ===
def validate_environment():
    required_vars = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "PINECONE_INDEX_NAME": PINECONE_INDEX_NAME
    }
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}")
    print("✓ All required environment variables are set.")

# === Ensure Index ===
def ensure_index_exists():
    if not pc:
        print("⚠ Pinecone not initialized. Skipping index creation.")
        return False
        
    try:
        index_names = pc.list_indexes().names()
        if PINECONE_INDEX_NAME not in index_names:
            print(f"Creating index: {PINECONE_INDEX_NAME}")
            try:
                pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION)
                )
                print(f"✓ Created index in AWS region: {PINECONE_REGION}")
            except Exception as aws_error:
                print(f"AWS failed: {aws_error}, trying GCP...")
                pc.create_index(
                    name=PINECONE_INDEX_NAME,
                    dimension=768,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="gcp", region="us-central1")
                )
                print("✓ Created index in GCP region: us-central1")

            # Wait for readiness (optional, often skipped in async setups)
            print("⏳ Waiting for index readiness...")
            for i in range(30):
                try:
                    status = pc.describe_index(PINECONE_INDEX_NAME).status
                    if status.get("ready", False):
                        print("✓ Index is ready!")
                        break
                except:
                    pass
                time.sleep(2)
            else:
                print("⚠ Index may not be ready yet, continuing anyway.")
        else:
            print(f"✓ Index '{PINECONE_INDEX_NAME}' already exists.")
    except Exception as e:
        print(f"✗ Failed to ensure index: {e}")
        raise

# === Connection Check ===
def test_pinecone_connection():
    if not pc:
        print("⚠ Pinecone not initialized.")
        return False
        
    try:
        index_names = pc.list_indexes().names()
        print(f"✓ Connected to Pinecone. Indexes: {index_names}")
        return True
    except Exception as e:
        print(f"✗ Pinecone connection failed: {e}")
        return False

# === Stats (using Langchain wrapper) ===
def get_index_stats():
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = LangchainPinecone.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        stats = vectorstore.index.describe_index_stats()
        print(f"📊 Index stats: {stats}")
        return stats
    except Exception as e:
        print(f"✗ Failed to fetch stats: {e}")
        return None

def get_index():
    if not pc:
        print("⚠ Pinecone not initialized.")
        return None
        
    try:
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print("✗ Pinecone index not found.")
            return None
        return pc.Index(PINECONE_INDEX_NAME)
    except Exception as e:
        print(f"✗ Failed to get Pinecone index: {e}")
        return None


# === Run Validation and Setup ===
if __name__ == "__main__":
    print("🔍 Checking environment...")
    try:
        validate_environment()
    except ValueError as e:
        print(f"⚠ {e}")
        exit(1)

    print("🔌 Testing Pinecone connection...")
    if test_pinecone_connection():
        try:
            ensure_index_exists()
            get_index_stats()
        except Exception as e:
            print(f"✗ Index setup failed: {e}")
    else:
        print("✗ Cannot proceed due to Pinecone connection failure.")
