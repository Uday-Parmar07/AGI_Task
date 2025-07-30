from ..services.ai_service import AIService
from ..models.chat_session import ChatSessionModel
from ..models.message import MessageModel

class ChatRouter:
    def __init__(self):
        self.ai_service = AIService()
    
    def ask_question(self, question: str, user_id: str, session_id: str) -> str:
        """Ask a question about the documents"""
        try:
            # Get namespaces
            doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
            chat_namespace = ChatSessionModel.get_chat_namespace(user_id, session_id)
            
            # Create user message
            user_message = MessageModel.create_message(
                user_id=user_id,
                chat_session_id=session_id,
                role="user",
                content=question
            )
            
            # Get AI response using the simplified method
            doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
            response = self.ai_service.ask_question(question, doc_namespace)
            
            # Create assistant message
            assistant_message = MessageModel.create_message(
                user_id=user_id,
                chat_session_id=session_id,
                role="assistant",
                content=response
            )
            
            return response
            
        except Exception as e:
            return f"❌ Error processing question: {str(e)}"