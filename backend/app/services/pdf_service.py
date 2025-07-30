from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os

class PDFService:
    @staticmethod
    def extract_text_from_pdfs(pdf_docs) -> str:
        """Extract text from multiple PDF files"""
        text = ""
        for pdf in pdf_docs:
            try:
                pdf_reader = PdfReader(pdf)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            except Exception as e:
                print(f"Error reading PDF: {str(e)}")
                continue
        return text
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from a single PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
        except Exception as e:
            print(f"Error reading PDF {file_path}: {str(e)}")
        return text
    
    @staticmethod
    def split_text_into_chunks(text: str, chunk_size: int = 10000, chunk_overlap: int = 1000) -> List[str]:
        """Split text into chunks for processing"""
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap
            )
            return splitter.split_text(text)
        except Exception as e:
            print(f"Error splitting text: {str(e)}")
            # Fallback: simple splitting
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    
    @staticmethod
    def save_uploaded_files(uploaded_files, upload_dir: str) -> List[str]:
        """Save uploaded files to disk and return file paths"""
        os.makedirs(upload_dir, exist_ok=True)
        file_paths = []
        
        for uploaded_file in uploaded_files:
            # Use secure filename for Flask file uploads
            from werkzeug.utils import secure_filename
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)
            file_paths.append(file_path)
            
        return file_paths