from .vector_service import VectorService
import os
import shutil

class DataService:
    def __init__(self):
        self.vector_service = VectorService()
    
    def clear_session_data(self, user_id: str, session_id: str, doc_namespace: str, chat_namespace: str, upload_dir: str) -> str:
        """Clear all data for a specific session"""
        try:
            # Clear document vectors
            self.vector_service.clear_namespace(doc_namespace)
            
            # Clear uploaded files
            session_upload_dir = os.path.join(upload_dir, f"{user_id}_{session_id}")
            if os.path.exists(session_upload_dir):
                shutil.rmtree(session_upload_dir)
            
            return "✅ Session data cleared successfully."
            
        except Exception as e:
            return f"❌ Error clearing session data: {str(e)}"
    
    def clear_all_user_data(self, user_id: str, upload_dir: str) -> str:
        """Clear all data for a user"""
        try:
            # Clear all user upload directories
            user_upload_dir = os.path.join(upload_dir, user_id)
            if os.path.exists(user_upload_dir):
                shutil.rmtree(user_upload_dir)
            
            return "✅ All user data cleared successfully."
            
        except Exception as e:
            return f"❌ Error clearing user data: {str(e)}"
    
    def get_session_upload_dir(self, user_id: str, session_id: str, base_upload_dir: str) -> str:
        """Get upload directory for a specific session"""
        session_dir = os.path.join(base_upload_dir, user_id, session_id)
        os.makedirs(session_dir, exist_ok=True)
        return session_dir