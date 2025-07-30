from ..services.pdf_service import PDFService
from ..services.vector_service import VectorService
from ..services.data_service import DataService
from ..models.document import DocumentModel
from ..models.chat_session import ChatSessionModel
from ..database.connection import save_document_to_db
from typing import List

class DocumentRouter:
    def __init__(self):
        self.pdf_service = PDFService()
        self.vector_service = VectorService()
        self.data_service = DataService()
    
    def upload_documents(self, uploaded_files, user_id: str, session_id: str, base_upload_dir: str) -> str:
        """Upload and process multiple PDF documents"""
        try:
            if not uploaded_files:
                return "❌ No files uploaded."
            
            # Get session upload directory
            upload_dir = self.data_service.get_session_upload_dir(user_id, session_id, base_upload_dir)
            
            # Save uploaded files
            file_paths = self.pdf_service.save_uploaded_files(uploaded_files, upload_dir)
            
            # Extract text from saved PDF files
            text = ""
            for file_path in file_paths:
                pdf_text = self.pdf_service.extract_text_from_pdf(file_path)
                text += pdf_text
            
            if not text.strip():
                return "❌ No text found in uploaded PDFs."
            
            # Split text into chunks
            text_chunks = self.pdf_service.split_text_into_chunks(text)
            
            # Get namespace for this session's documents
            doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
            
            # Store vectors in Pinecone
            self.vector_service.store_document_vectors(text_chunks, doc_namespace)
            
            # Save document records to database
            documents_saved = 0
            for i, uploaded_file in enumerate(uploaded_files):
                success = save_document_to_db(
                    user_id=user_id,
                    chat_session_id=session_id,
                    filename=uploaded_file.filename,
                    file_path=file_paths[i]
                )
                if success:
                    documents_saved += 1
            
            return f"✅ Successfully uploaded and processed {len(uploaded_files)} documents. {documents_saved} saved to database."
            
        except Exception as e:
            return f"❌ Error uploading documents: {str(e)}"
    
    def clear_session_documents(self, user_id: str, session_id: str, base_upload_dir: str) -> str:
        """Clear all documents for a session"""
        doc_namespace = ChatSessionModel.get_session_namespace(user_id, session_id)
        chat_namespace = ChatSessionModel.get_chat_namespace(user_id, session_id)
        
        return self.data_service.clear_session_data(
            user_id, session_id, doc_namespace, chat_namespace, base_upload_dir
        )