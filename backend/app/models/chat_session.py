import uuid
from datetime import datetime
from ..database.schemas import ChatSession

class ChatSessionModel:
    @staticmethod
    def create_session(user_id: str, title: str = "New Chat") -> ChatSession:
        """Create a new chat session"""
        return ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            document_count=0
        )
    
    @staticmethod
    def get_session_namespace(user_id: str, session_id: str) -> str:
        """Get namespace for session's documents"""
        return f"user_{user_id}_session_{session_id}"
    
    @staticmethod
    def get_chat_namespace(user_id: str, session_id: str) -> str:
        """Get namespace for session's chat history"""
        return f"chat_{user_id}_{session_id}"