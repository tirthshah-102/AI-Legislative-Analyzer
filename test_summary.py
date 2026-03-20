import os
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.analyzer import LegislativeAnalyzer

def test_summary():
    analyzer = LegislativeAnalyzer()
    
    # We will use the existing demo pdf
    pdf_path = "Green_Energy_Act_Demo.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find {pdf_path}")
        return
        
    print(f"Testing summary generation for {pdf_path}...\n")
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        print("Error extracting text.")
        return
        
    print("--- Test 1: English Summary ---")
    summary_en, _ = analyzer.generate_summary(text, language="English")
    with open("summary_en.md", "w", encoding="utf-8") as f:
        f.write(summary_en)
    print("Saved to summary_en.md")
    
    print("--- Test 2: Hindi Summary ---")
    summary_hi, _ = analyzer.generate_summary(text, language="Hindi")
    with open("summary_hi.md", "w", encoding="utf-8") as f:
        f.write(summary_hi)
    print("Saved to summary_hi.md")
    
if __name__ == "__main__":
    test_summary()
