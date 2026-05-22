from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from gtts import gTTS
from dotenv import load_dotenv

# Import utilities
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.analyzer import LegislativeAnalyzer
from src.utils.report_gen import ReportGenerator
from src.utils.database import Database, init_db
from src.utils.auth import hash_password, verify_password, create_token, verify_token, login_required
from src.utils.validation import Validator, ValidationError, error_response, success_response
from src.utils.cache import Cache, get_file_hash

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

analyzer = LegislativeAnalyzer()
reporter = ReportGenerator()

# Ensure directories exist
os.makedirs("tmp", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Initialize database
init_db()

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate inputs
        Validator.validate_username(username)
        if not Validator.validate_email(email):
            raise ValidationError("Invalid email format")
        Validator.validate_password(password)
        
        # Check if user exists
        if Database.get_user_by_username(username):
            return error_response("Username already exists", 400)
        
        # Create user
        password_hash = hash_password(password)
        user_id = Database.create_user(username, email, password_hash)
        
        if not user_id:
            return error_response("Email already exists", 400)
        
        token = create_token(user_id, username)
        return success_response({
            'user_id': user_id,
            'username': username,
            'token': token
        }, "User registered successfully")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Registration failed: {str(e)}", 500)

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return error_response("Username and password required", 400)
        
        user = Database.get_user_by_username(username)
        if not user:
            return error_response("Invalid credentials", 401)
        
        user_id, stored_username, email, password_hash, _, _ = user
        
        if not verify_password(password_hash, password):
            return error_response("Invalid credentials", 401)
        
        token = create_token(user_id, username)
        return success_response({
            'user_id': user_id,
            'username': username,
            'email': email,
            'token': token
        }, "Login successful")
        
    except Exception as e:
        return error_response(f"Login failed: {str(e)}", 500)

# ==================== DOCUMENT ENDPOINTS ====================

@app.route('/api/documents/upload', methods=['POST'])
@login_required
def upload_file(user_id):
    """Upload and process PDF"""
    try:
        if 'file' not in request.files:
            return error_response("No file part", 400)
        
        file = request.files['file']
        
        # Validate file
        Validator.validate_file(file)
        
        # Check cache first
        file_content = file.read()
        cached_text, file_hash = Cache.get_cached_text(file_content)
        
        if cached_text:
            # Use cached version
            text = cached_text
        else:
            # Process new file
            temp_path = os.path.join("tmp", file.filename)
            with open(temp_path, "wb") as f:
                f.write(file_content)
            
            text = extract_text_from_pdf(temp_path)
            if not text:
                return error_response("Failed to extract text from PDF", 500)
            
            # Cache the extracted text
            Cache.cache_extracted_text(file_content, text)
        
        # Save to database
        doc_id = Database.save_document(
            user_id=user_id,
            filename=file.filename,
            text=text,
            file_path=os.path.join("tmp", file.filename),
            file_size=len(file_content)
        )
        
        return success_response({
            'document_id': doc_id,
            'filename': file.filename,
            'text_length': len(text),
            'cached': bool(cached_text)
        }, "File uploaded successfully")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Upload failed: {str(e)}", 500)

@app.route('/api/documents/<int:doc_id>', methods=['GET'])
@login_required
def get_document(user_id, doc_id):
    """Get document details"""
    try:
        docs = Database.get_user_documents(user_id)
        doc = next((d for d in docs if d[0] == doc_id), None)
        
        if not doc:
            return error_response("Document not found", 404)
        
        return success_response({
            'id': doc[0],
            'filename': doc[1],
            'upload_date': doc[5],
            'file_size': doc[6]
        })
        
    except Exception as e:
        return error_response(f"Failed to fetch document: {str(e)}", 500)

@app.route('/api/documents', methods=['GET'])
@login_required
def list_documents(user_id):
    """List all user documents"""
    try:
        docs = Database.get_user_documents(user_id)
        
        return success_response({
            'documents': [
                {
                    'id': d[0],
                    'filename': d[1],
                    'upload_date': d[5],
                    'file_size': d[6]
                }
                for d in docs
            ]
        }, f"Found {len(docs)} documents")
        
    except Exception as e:
        return error_response(f"Failed to list documents: {str(e)}", 500)

# ==================== ANALYSIS ENDPOINTS ====================

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze(user_id):
    """Analyze document"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text = data.get('text', '').strip()
        language = data.get('language', 'English')
        document_id = data.get('document_id')
        
        # Validate inputs
        Validator.validate_text(text)
        Validator.validate_language(language)
        
        # Generate analysis
        summary, metrics = analyzer.generate_summary(text, language=language)
        glossary = analyzer.extract_glossary(text, language=language)
        risk_data = analyzer.analyze_risk_and_complexity(text, language=language)
        
        # Save to database if document_id provided
        if document_id:
            Database.save_analysis(document_id, summary, glossary, metrics, language)
        
        return success_response({
            'summary': summary,
            'metrics': metrics,
            'glossary': glossary,
            'risk_data': risk_data
        }, "Analysis completed")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Analysis failed: {str(e)}", 500)

@app.route('/api/question', methods=['POST'])
@login_required
def ask_question(user_id):
    """Ask question about document"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text = data.get('text', '').strip()
        question = data.get('question', '').strip()
        language = data.get('language', 'English')
        document_id = data.get('document_id')
        
        # Validate inputs
        Validator.validate_text(text, min_length=10)
        Validator.validate_text(question, min_length=5)
        Validator.validate_language(language)
        
        # Generate answer
        answer, confidence = analyzer.ask_question(text, question, language=language)
        
        # Save to chat history
        if document_id:
            Database.save_chat(user_id, document_id, question, answer)
        
        return success_response({
            'answer': answer,
            'confidence': confidence
        }, "Question answered")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Question processing failed: {str(e)}", 500)

@app.route('/api/compare', methods=['POST'])
@login_required
def compare_bills(user_id):
    """Compare two documents"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text1 = data.get('text1', '').strip()
        text2 = data.get('text2', '').strip()
        language = data.get('language', 'English')
        
        # Validate inputs
        Validator.validate_text(text1)
        Validator.validate_text(text2)
        Validator.validate_language(language)
        
        # Compare
        comparison = analyzer.compare_bills_analysis(text1, text2, language)
        
        return success_response({
            'comparison': comparison
        }, "Comparison completed")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Comparison failed: {str(e)}", 500)

@app.route('/api/compliance', methods=['POST'])
@login_required
def get_compliance(user_id):
    """Get compliance checklist"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text = data.get('text', '').strip()
        language = data.get('language', 'English')
        
        Validator.validate_text(text)
        Validator.validate_language(language)
        
        checklist = analyzer.generate_compliance_checklist(text, language)
        
        return success_response({
            'checklist': checklist
        }, "Compliance checklist generated")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Compliance check failed: {str(e)}", 500)

@app.route('/api/timeline', methods=['POST'])
@login_required
def get_timeline(user_id):
    """Extract timeline data"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text = data.get('text', '').strip()
        language = data.get('language', 'English')
        
        Validator.validate_text(text)
        Validator.validate_language(language)
        
        timeline = analyzer.extract_timeline_data(text, language)
        
        return success_response({
            'timeline': timeline
        }, "Timeline extracted")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Timeline extraction failed: {str(e)}", 500)

# ==================== EXPORT ENDPOINTS ====================

@app.route('/api/export/pdf', methods=['POST'])
@login_required
def export_pdf(user_id):
    """Export analysis as PDF"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        summary = data.get('text', '').strip()
        language = data.get('language', 'English')
        
        if not summary:
            return error_response("No summary text provided", 400)
        
        Validator.validate_language(language)
        
        pdf_path = reporter.generate_summary_pdf(summary, language)
        abs_tmp = os.path.abspath("tmp")
        filename = os.path.basename(pdf_path)
        download_name = f"Legislative_Summary_{language}.pdf"
        
        return send_from_directory(
            abs_tmp,
            filename,
            as_attachment=True,
            download_name=download_name,
            mimetype="application/pdf"
        )
        
    except Exception as e:
        return error_response(f"PDF export failed: {str(e)}", 500)

@app.route('/api/export/json', methods=['POST'])
@login_required
def export_json(user_id):
    """Export analysis as JSON"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        return success_response(data, "Data exported as JSON")
        
    except Exception as e:
        return error_response(f"JSON export failed: {str(e)}", 500)

@app.route('/api/export/csv', methods=['POST'])
@login_required
def export_csv(user_id):
    """Export data as CSV"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        glossary = data.get('glossary', [])
        
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Term', 'Definition'])
        
        for item in glossary:
            if isinstance(item, dict):
                writer.writerow([item.get('term', ''), item.get('definition', '')])
        
        csv_content = output.getvalue()
        
        return success_response({
            'csv': csv_content
        }, "Data exported as CSV")
        
    except Exception as e:
        return error_response(f"CSV export failed: {str(e)}", 500)

# ==================== TTS ENDPOINT ====================

@app.route('/api/tts', methods=['POST'])
@login_required
def text_to_speech(user_id):
    """Generate text-to-speech"""
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Invalid JSON data", 400)
        
        text = data.get('text', '').strip()
        language = data.get('language', 'English')
        
        Validator.validate_text(text, min_length=5)
        Validator.validate_language(language)
        
        lang_code = analyzer.lang_map.get(language, 'en')
        # Truncate long texts for TTS stability
        tts_text = text[:3000] if len(text) > 3000 else text
        
        tts = gTTS(text=tts_text, lang=lang_code, slow=False)
        tts_path = os.path.join("tmp", f"summary_{user_id}.mp3")
        tts.save(tts_path)
        
        with open(tts_path, "rb") as f:
            audio_content = base64.b64encode(f.read()).decode('utf-8')
        
        return success_response({
            'audio': audio_content,
            'language': language
        }, "Audio generated")
        
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Audio generation failed: {str(e)}", 500)

# ==================== STATIC FILES ====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def server_error(error):
    return error_response("Internal server error", 500)

# ==================== START APP ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
