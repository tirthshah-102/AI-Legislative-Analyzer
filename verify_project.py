import os
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.compressor import ScaleDownClient
from dotenv import load_dotenv

load_dotenv()

def verify():
    print("--- ⚖️ Verifying AI Legislative Analyzer ---")
    
    # 1. Verify PDF Extraction
    pdf_path = "AI Legislative Analyzer_ Token Compression.pdf"
    print(f"Testing PDF extraction for: {pdf_path}")
    if os.path.exists(pdf_path):
        text = extract_text_from_pdf(pdf_path)
        if text:
            print(f"✅ Success: Extracted {len(text)} characters.")
            # print(text[:200] + "...")
        else:
            print("❌ Failure: PDF extraction returned no text.")
    else:
        print(f"❌ Failure: PDF file not found at {pdf_path}")

    # 2. Verify API Key / Connection
    print("\nTesting ScaleDown API Connection...")
    client = ScaleDownClient()
    if client.api_key:
        print(f"API Key found: {client.api_key[:5]}...{client.api_key[-5:]}")
        # Small test compression
        result, error = client.compress_context("This is a test context about legislation.", "Summarize this.")
        if error:
            print(f"❌ API Error: {error}")
        else:
            print("✅ API Success: Compression result received.")
            # print(result)
    else:
        print("❌ Failure: API Key not found in .env")

if __name__ == "__main__":
    verify()
