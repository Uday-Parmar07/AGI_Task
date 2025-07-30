import hashlib
import uuid
from datetime import datetime, timedelta
import jwt
import os

class AuthUtils:
    @staticmethod
    def generate_user_id() -> str:
        """Generate unique user ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate unique session ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode = {"user_id": user_id, "exp": expire}
        secret_key = os.getenv("SECRET_KEY", "your-secret-key")
        return jwt.encode(to_encode, secret_key, algorithm="HS256")
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token"""
        try:
            secret_key = os.getenv("SECRET_KEY", "your-secret-key")
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"error": "Invalid token"}