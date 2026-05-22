import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path("data/app.db")

def init_db():
    """Initialize database with required tables"""
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_text TEXT,
            file_path TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Analysis results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            summary TEXT,
            glossary TEXT,
            metrics TEXT,
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    ''')
    
    # Chat history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            document_id INTEGER,
            question TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    ''')
    
    # Cached files table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_hash TEXT UNIQUE NOT NULL,
            extracted_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

class Database:
    """Database operations wrapper"""
    
    @staticmethod
    def create_user(username, email, password_hash):
        """Create new user"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    @staticmethod
    def save_document(user_id, filename, text, file_path, file_size):
        """Save uploaded document"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO documents (user_id, filename, original_text, file_path, file_size) VALUES (?, ?, ?, ?, ?)',
            (user_id, filename, text, file_path, file_size)
        )
        conn.commit()
        doc_id = cursor.lastrowid
        conn.close()
        return doc_id
    
    @staticmethod
    def save_analysis(document_id, summary, glossary, metrics, language):
        """Save analysis results"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO analyses (document_id, summary, glossary, metrics, language) VALUES (?, ?, ?, ?, ?)',
            (document_id, summary, json.dumps(glossary), json.dumps(metrics), language)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def save_chat(user_id, document_id, question, answer):
        """Save chat message"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO chat_history (user_id, document_id, question, answer) VALUES (?, ?, ?, ?)',
            (user_id, document_id, question, answer)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_documents(user_id):
        """Get all documents for user"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents WHERE user_id = ? ORDER BY upload_date DESC', (user_id,))
        docs = cursor.fetchall()
        conn.close()
        return docs
    
    @staticmethod
    def get_user_chat_history(user_id, limit=20):
        """Get chat history for user"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        )
        chats = cursor.fetchall()
        conn.close()
        return chats
    
    @staticmethod
    def save_cache(file_hash, extracted_text, expires_at=None):
        """Save file to cache"""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO cache (file_hash, extracted_text, expires_at) VALUES (?, ?, ?)',
                (file_hash, extracted_text, expires_at)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute(
                'UPDATE cache SET extracted_text = ?, expires_at = ? WHERE file_hash = ?',
                (extracted_text, expires_at, file_hash)
            )
            conn.commit()
        conn.close()
    
    @staticmethod
    def get_cache(file_hash):
        """Get cached file"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT extracted_text FROM cache WHERE file_hash = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)',
            (file_hash,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

# Initialize database on import
init_db()
