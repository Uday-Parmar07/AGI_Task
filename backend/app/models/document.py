import uuid
from datetime import datetime
from ..database.schemas import Document

class DocumentModel:
    @staticmethod
    def create_document(user_id: str, chat_session_id: str, filename: str, file_path: str) -> Document:
        """Create a new document record"""
        return Document(
            id=str(uuid.uuid4()),
            user_id=user_id,
            chat_session_id=chat_session_id,
            filename=filename,
            file_path=file_path,
            uploaded_at=datetime.now()
        )
    