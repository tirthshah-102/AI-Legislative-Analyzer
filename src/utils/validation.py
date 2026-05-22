import re
from flask import jsonify

class ValidationError(Exception):
    """Custom validation error"""
    pass

class Validator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username (3-20 chars, alphanumeric + underscore)"""
        if len(username) < 3 or len(username) > 20:
            raise ValidationError("Username must be 3-20 characters")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores")
        return True
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Password must contain at least one number")
        return True
    
    @staticmethod
    def validate_file(file, allowed_ext=['pdf'], max_size=50*1024*1024):
        """Validate uploaded file"""
        if not file:
            raise ValidationError("No file provided")
        
        if file.filename == '':
            raise ValidationError("No file selected")
        
        # Check extension
        if not ('.' in file.filename):
            raise ValidationError("File must have an extension")
        
        ext = file.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_ext:
            raise ValidationError(f"File type must be one of: {', '.join(allowed_ext)}")
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise ValidationError(f"File size must be less than {max_size / (1024*1024):.1f}MB")
        
        return True
    
    @staticmethod
    def validate_text(text, min_length=10, max_length=100000):
        """Validate text input"""
        if not text or not isinstance(text, str):
            raise ValidationError("Text must be a non-empty string")
        
        text = text.strip()
        
        if len(text) < min_length:
            raise ValidationError(f"Text must be at least {min_length} characters")
        
        if len(text) > max_length:
            raise ValidationError(f"Text must not exceed {max_length} characters")
        
        return True
    
    @staticmethod
    def validate_language(language):
        """Validate language selection"""
        allowed_languages = ["English", "Hindi", "Gujarati"]
        if language not in allowed_languages:
            raise ValidationError(f"Language must be one of: {', '.join(allowed_languages)}")
        return True

def handle_validation_error(f):
    """Decorator to handle validation errors"""
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error', 'details': str(e)}), 500
    wrapper.__name__ = f.__name__
    return wrapper

def error_response(message, code=400):
    """Create error response"""
    return jsonify({'error': message}), code

def success_response(data, message="Success", code=200):
    """Create success response"""
    return jsonify({'status': 'success', 'message': message, 'data': data}), code
