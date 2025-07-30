from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    id: str
    user_id: str
    chat_session_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    
class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    document_count: int
    
class Document(BaseModel):
    id: str
    user_id: str
    chat_session_id: str
    filename: str
    file_path: str
    uploaded_at: datetime
    
class Summary(BaseModel):
    id: str
    user_id: str
    chat_session_id: str
    content: str
    created_at: datetime
    
class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: datetime