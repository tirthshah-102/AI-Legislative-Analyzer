# 🚀 AI Legislative Analyzer - UPGRADED VERSION

This is the **enhanced, production-ready** version of the AI Legislative Analyzer with authentication, caching, validation, and modern UI.

## ✨ New Features Added

### ✅ Authentication System
- User registration & login with JWT tokens
- Secure password hashing (PBKDF2)
- Token-based API authentication

### ✅ Database Integration
- SQLite database for user management
- Document storage & history
- Chat history tracking
- File caching system

### ✅ Validation & Error Handling
- Input validation on all endpoints
- Comprehensive error responses
- File size & type validation
- Password strength requirements

### ✅ File Caching
- Automatic PDF extraction caching
- File hash-based cache lookup
- Reduces redundant processing

### ✅ Modern Frontend
- Glass-morphism UI design
- Authentication screens
- Progress tracking for uploads
- Tab-based interface
- Real-time notifications

### ✅ Export Features
- PDF export
- JSON export
- CSV export (for glossaries)

### ✅ Docker Support
- Containerized deployment
- Docker Compose configuration
- Production-ready setup

---

## 🛠️ Setup Instructions

### Option 1: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Flask backend
python main_new.py

# 3. Open browser
# http://localhost:5000
```

### Option 2: Docker

```bash
# Build and run
docker-compose up --build

# Backend: http://localhost:5000
# Frontend: http://localhost:80 (via Nginx)
```

---

## 📁 Project Structure

```
├── main_new.py              # Updated Flask app with auth & validation
├── src/
│   └── utils/
│       ├── database.py      # SQLite database operations
│       ├── auth.py          # JWT authentication & password hashing
│       ├── validation.py    # Input validation utilities
│       ├── cache.py         # File caching system
│       ├── analyzer.py      # AI analysis engine
│       ├── pdf_handler.py   # PDF extraction
│       └── report_gen.py    # PDF report generation
├── static/
│   ├── index_new.html       # Modern frontend UI
│   └── new-script.js        # Frontend JavaScript
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── data/                    # SQLite database location
└── tmp/                     # Temporary files & cache
```

---

## 🔐 API Endpoints

### Authentication
```
POST   /api/auth/register          # Register new user
POST   /api/auth/login             # Login user
```

### Documents
```
POST   /api/documents/upload       # Upload PDF (requires auth)
GET    /api/documents              # List user documents
GET    /api/documents/<id>         # Get document details
```

### Analysis
```
POST   /api/analyze                # Analyze document
POST   /api/question               # Ask question about document
POST   /api/compare                # Compare two documents
POST   /api/compliance             # Get compliance checklist
POST   /api/timeline               # Extract timeline data
```

### Export
```
POST   /api/export/pdf             # Export as PDF
POST   /api/export/json            # Export as JSON
POST   /api/export/csv             # Export as CSV
POST   /api/tts                    # Generate audio
```

---

## 🔑 Authentication

All API endpoints (except `/api/auth/*`) require a Bearer token in the Authorization header:

```javascript
fetch('/api/analyze', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ text, language })
})
```

---

## 📦 Frontend Usage

### 1. Register Account
```html
POST /api/auth/register
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
}
```

### 2. Upload PDF
```javascript
const formData = new FormData();
formData.append('file', pdfFile);

fetch('/api/documents/upload', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
})
```

### 3. Analyze Document
```javascript
fetch('/api/analyze', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        text: extractedText,
        language: 'English'
    })
})
```

---

## 🎯 Usage Steps

1. **Register**: Create a new account
2. **Login**: Sign in with credentials
3. **Upload**: Select a PDF from your device
4. **Track**: Watch upload progress in real-time
5. **Analyze**: Choose language and analyze
6. **Export**: Download results as PDF/CSV
7. **Manage**: View all documents in "My Documents"

---

## 🔒 Security Features

- ✅ Password hashing with PBKDF2
- ✅ JWT token-based authentication
- ✅ Input validation on all endpoints
- ✅ File type & size validation
- ✅ SQL injection protection (prepared statements)
- ✅ CORS enabled for cross-origin requests
- ✅ Error messages don't leak sensitive info

---

## 📊 Database Schema

### users
```sql
id (PK), username, email, password_hash, created_at, updated_at
```

### documents
```sql
id (PK), user_id (FK), filename, original_text, file_path, upload_date, file_size
```

### analyses
```sql
id (PK), document_id (FK), summary, glossary, metrics, language, created_at
```

### chat_history
```sql
id (PK), user_id (FK), document_id (FK), question, answer, created_at
```

### cache
```sql
id (PK), file_hash (UNIQUE), extracted_text, created_at, expires_at
```

---

## ⚙️ Configuration

Edit environment variables in `.env`:

```env
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
DATABASE_PATH=data/app.db
```

---

## 🚨 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Port 5000 already in use
```bash
python main_new.py --port 8000
```

### Database locked
```bash
rm data/app.db
# This will recreate the database
```

### PDF extraction fails
```bash
# Install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 📈 Performance Tips

1. **Enable Caching**: PDF extraction results are cached automatically
2. **Use Shorter Texts**: Large documents (>100k chars) may take longer
3. **Batch Operations**: Process multiple files sequentially to avoid timeouts
4. **Docker**: Use Docker for better resource management in production

---

## 🎨 Frontend Updates

The new frontend (`index_new.html` + `new-script.js`) includes:

- 🎨 Modern glassmorphism design
- 📱 Responsive layout (mobile-friendly)
- ⚡ Real-time progress tracking
- 🔔 Toast notifications
- 🔐 Login/Register screens
- 📊 Analytics dashboard
- 📥 Easy export options
- 💾 Document management

---

## 🔄 How to Switch to New Version

```bash
# Backup old files
cp main.py main_backup.py
cp static/index.html static/index_backup.html

# Use new versions
cp main_new.py main.py
cp static/index_new.html static/index.html
cp static/new-script.js static/script.js

# Install new dependencies
pip install -r requirements.txt

# Run
python main.py
```

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs in console
3. Check browser console (F12) for client-side errors
4. Review server logs for API errors

---

## 📝 License

Same as original project

---

**Last Updated**: May 2026
**Version**: 2.0 (Enhanced Production Ready)
