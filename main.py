from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import base64
from gtts import gTTS
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.analyzer import LegislativeAnalyzer
from src.utils.report_gen import ReportGenerator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

analyzer = LegislativeAnalyzer()
reporter = ReportGenerator()

# Ensure tmp directory exists
os.makedirs("tmp", exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload request received")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        temp_path = os.path.join("tmp", file.filename)
        file.save(temp_path)
        
        print(f"File saved to {temp_path}, extracting text...")
        text = extract_text_from_pdf(temp_path)
        if text:
            print(f"Extraction successful: {len(text)} characters")
            return jsonify({"status": "success", "text": text})
        else:
            print("Extraction failed")
            return jsonify({"error": "Text extraction failed"}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    print("Analyze request received")
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        summary, metrics = analyzer.generate_summary(text, language=language)
        glossary = analyzer.extract_glossary(text, language=language)
        risk_data = analyzer.analyze_risk_and_complexity(text, language=language)
        return jsonify({
            "summary": summary,
            "metrics": metrics,
            "glossary": glossary,
            "risk_data": risk_data
        })
    except Exception as e:
        print(f"Analysis error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/compliance', methods=['POST'])
def get_compliance():
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    try:
        checklist = analyzer.generate_compliance_checklist(text, language)
        return jsonify({"checklist": checklist})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/citations', methods=['POST'])
def get_citations():
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    try:
        citations = analyzer.extract_citations_and_entities(text, language)
        return jsonify({"citations": citations})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/timeline', methods=['POST'])
def get_timeline():
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    try:
        timeline = analyzer.extract_timeline_data(text, language)
        return jsonify({"timeline": timeline})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entities', methods=['POST'])
def get_entities():
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    try:
        entities = analyzer.extract_entity_map(text, language)
        return jsonify({"entities": entities})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compare', methods=['POST'])
def compare_bills():
    data = request.json
    text1 = data.get('text1')
    text2 = data.get('text2')
    language = data.get('language', 'English')
    if not text1 or not text2:
        return jsonify({"error": "Two documents required for comparison"}), 400
    try:
        comparison = analyzer.compare_bills_analysis(text1, text2, language)
        return jsonify({"comparison": comparison})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    print("Ask request received")
    data = request.json
    text = data.get('text')
    question = data.get('question')
    language = data.get('language', 'English')
    
    if not text or not question:
        return jsonify({"error": "Missing parameters"}), 400
    
    try:
        answer, _ = analyzer.ask_question(text, question, language=language)
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"Ask error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download_summary():
    print("Download request received")
    data = request.json
    summary = data.get('text')
    language = data.get('language', 'English')
    
    if not summary:
        return jsonify({"error": "No summary text provided"}), 400
    
    try:
        pdf_path = reporter.generate_summary_pdf(summary, language)
        abs_tmp = os.path.abspath("tmp")
        filename = os.path.basename(pdf_path)
        download_name = f"Legislative_Summary_{language}.pdf"
        return send_from_directory(abs_tmp, filename, as_attachment=True, download_name=download_name, mimetype="application/pdf")
    except Exception as e:
        print(f"Download error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500

@app.route('/tts', methods=['POST'])
def text_to_speech():
    print("TTS request received")
    data = request.json
    text = data.get('text')
    language = data.get('language', 'English')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        lang_code = analyzer.lang_map.get(language, 'en')
        # gTTS can fail on very long texts - truncate to ~3000 chars for stability
        tts_text = text[:3000] if len(text) > 3000 else text
        tts = gTTS(text=tts_text, lang=lang_code, slow=False)
        tts_path = os.path.join("tmp", "summary.mp3")
        tts.save(tts_path)
        
        with open(tts_path, "rb") as f:
            audio_content = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({"audio": audio_content, "status": "ok"})
    except Exception as e:
        print(f"TTS error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"error": f"Audio generation failed: {str(e)}"}), 500

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
