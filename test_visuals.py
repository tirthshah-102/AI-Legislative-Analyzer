import os
from src.utils.pdf_handler import extract_text_from_pdf
from src.utils.analyzer import LegislativeAnalyzer

def test_visuals():
    analyzer = LegislativeAnalyzer()
    pdf_path = "Green_Energy_Act_Demo.pdf"
    
    print(f"Testing visual extractors for {pdf_path}...\n")
    text = extract_text_from_pdf(pdf_path)
    
    print("--- Risk & Complexity ---")
    risk = analyzer.analyze_risk_and_complexity(text)
    print(risk)
    
    print("\n--- Timeline ---")
    timeline = analyzer.extract_timeline_data(text)
    print(timeline)
    
    print("\n--- Entities ---")
    entities = analyzer.extract_entity_map(text)
    print(entities)

if __name__ == "__main__":
    test_visuals()
