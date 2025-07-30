import uuid
from datetime import datetime
from ..database.schemas import Summary

class SummaryModel:
    @staticmethod
    def create_summary(user_id: str, chat_session_id: str, content: str) -> Summary:
        """Create a new summary record"""
        return Summary(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chat_session_id=chat_session_id,
            content=content,
            created_at=datetime.now()
        )