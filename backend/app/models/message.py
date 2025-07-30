import uuid
from datetime import datetime
from ..database.schemas import ChatMessage

class MessageModel:
    @staticmethod
    def create_message(user_id: str, chat_session_id: str, role: str, content: str) -> ChatMessage:
        """Create a new chat message"""
        return ChatMessage(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chat_session_id=chat_session_id,
            role=role,
            content=content,
            timestamp=datetime.now()
        )