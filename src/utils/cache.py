import hashlib
from datetime import datetime, timedelta
from src.utils.database import Database

def get_file_hash(file_content):
    """Generate hash of file content"""
    return hashlib.sha256(file_content).hexdigest()

class Cache:
    """Caching utilities for PDF processing"""
    
    @staticmethod
    def get_cached_text(file_content):
        """Get cached extracted text if available"""
        file_hash = get_file_hash(file_content)
        return Database.get_cache(file_hash), file_hash
    
    @staticmethod
    def cache_extracted_text(file_content, extracted_text, expires_hours=30*24):
        """Cache extracted text from PDF"""
        file_hash = get_file_hash(file_content)
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        Database.save_cache(file_hash, extracted_text, expires_at)
        return file_hash
    
    @staticmethod
    def generate_cache_key(user_id, document_id):
        """Generate cache key for processed documents"""
        key = f"{user_id}:{document_id}"
        return hashlib.md5(key.encode()).hexdigest()
