import uuid
import hashlib
from datetime import datetime
from ..database.schemas import User

class UserModel:
    @staticmethod
    def create_user(username: str, email: str = None, password: str = None) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        hashed_password = None
        
        if password:
            # Simple password hashing (in production, use bcrypt or similar)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        return User(
            id=user_id,
            username=username,
            email=email,
            password_hash=hashed_password,
            created_at=datetime.now()
        )
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """Authenticate a user (simplified implementation)"""
        # In a real application, this would query the database
        # For now, create a dummy user for testing
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if username and password:
            return User(
                id=str(uuid.uuid4()),
                username=username,
                email=f"{username}@example.com",
                password_hash=hashed_password,
                created_at=datetime.now()
            )
        return None
    
    @staticmethod
    def get_user_namespace(user_id: str) -> str:
        """Get namespace for user's data"""
        return f"user_{user_id}"