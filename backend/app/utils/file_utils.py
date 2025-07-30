import os
import shutil
from typing import List

class FileUtils:
    @staticmethod
    def ensure_directory_exists(directory: str):
        """Ensure directory exists, create if not"""
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def delete_directory(directory: str):
        """Delete directory and all contents"""
        if os.path.exists(directory):
            shutil.rmtree(directory)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(file_path)
    
    @staticmethod
    def is_pdf_file(filename: str) -> bool:
        """Check if file is a PDF"""
        return filename.lower().endswith('.pdf')
    
    @staticmethod
    def validate_uploaded_files(uploaded_files, max_size_mb: int = 10) -> List[str]:
        """Validate uploaded files"""
        errors = []
        
        for file in uploaded_files:
            # Check if it's a PDF
            if not FileUtils.is_pdf_file(file.name):
                errors.append(f"File '{file.name}' is not a PDF")
            
            # Check file size
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                errors.append(f"File '{file.name}' is too large ({file_size_mb:.1f}MB > {max_size_mb}MB)")
        
        return errors
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe storage"""
        # Remove or replace unsafe characters
        unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename