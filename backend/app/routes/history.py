from ..services.vector_service import VectorService
from ..models.chat_session import ChatSessionModel
from ..database.connection import get_user_sessions_from_db, get_session_document_count
from typing import List, Dict

class HistoryRouter:
    def __init__(self):
        self.vector_service = VectorService()

    def get_chat_history(self, user_id: str, session_id: str = None) -> List[Dict]:
        """Get chat history for one session or all sessions if session_id not provided"""
        try:
            session_ids = []

            if session_id:
                session_ids = [session_id]
                print(f"Getting history for specific session: {session_id}")
            else:
                all_sessions = self.get_all_user_sessions(user_id)
                session_ids = [s["session_id"] for s in all_sessions]
                print(f"Getting history for all sessions: {session_ids}")

            full_history = []

            for sid in session_ids:
                chat_namespace = ChatSessionModel.get_chat_namespace(user_id, sid)
                print(f"Looking for chat history in namespace: {chat_namespace}")
                docs = self.vector_service.get_chat_history(chat_namespace, k=100)
                print(f"Found {len(docs)} documents in namespace {chat_namespace}")

                # Process individual messages instead of Q&A pairs
                messages = []
                for doc in docs:
                    content = doc.page_content
                    metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                    
                    print(f"Processing message: {content[:50]}... with metadata: {metadata}")
                    
                    # Extract role and timestamp from metadata
                    role = metadata.get('role', 'unknown')
                    timestamp = metadata.get('timestamp', None)
                    message_type = metadata.get('type', 'unknown')
                    
                    if role in ['user', 'assistant'] and content.strip():
                        message = {
                            "user_id": user_id,
                            "session_id": sid,
                            "role": role,
                            "content": content.strip(),
                            "timestamp": timestamp,
                            "type": message_type
                        }
                        messages.append(message)
                        print(f"Added {role} message to history")

                # Sort messages by timestamp to maintain conversation order
                messages.sort(key=lambda x: x.get('timestamp', ''))
                
                # Group messages into conversation pairs for display
                i = 0
                while i < len(messages):
                    if i + 1 < len(messages) and messages[i]['role'] == 'user' and messages[i + 1]['role'] == 'assistant':
                        # Found a question-answer pair
                        full_history.append({
                            "user_id": user_id,
                            "session_id": sid,
                            "question": messages[i]['content'],
                            "answer": messages[i + 1]['content'],
                            "timestamp": messages[i + 1]['timestamp']  # Use answer timestamp
                        })
                        print(f"Created Q&A pair: {messages[i]['content'][:30]}...")
                        i += 2  # Skip both messages
                    else:
                        # Handle orphaned messages (shouldn't happen in normal flow)
                        if messages[i]['role'] == 'user':
                            full_history.append({
                                "user_id": user_id,
                                "session_id": sid,
                                "question": messages[i]['content'],
                                "answer": "No response recorded",
                                "timestamp": messages[i]['timestamp']
                            })
                        i += 1

            print(f"Total history items found: {len(full_history)}")
            return full_history

        except Exception as e:
            print(f"Error in get_chat_history: {str(e)}")
            return [{"error": f"Error loading chat history: {str(e)}"}]

    def get_all_user_sessions(self, user_id: str) -> List[Dict]:
        """Return all sessions for the user from the database"""
        try:
            # Get sessions from database
            sessions = get_user_sessions_from_db(user_id)
            
            # If no sessions found, return empty list
            if not sessions:
                return []
            
            return sessions
            
        except Exception as e:
            print(f"Error loading sessions: {str(e)}")
            return [{"error": f"Error loading sessions: {str(e)}"}]
