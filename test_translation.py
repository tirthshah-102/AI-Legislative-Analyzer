from src.utils.analyzer import LegislativeAnalyzer

def test_translation():
    print("--- 🌐 Testing Multilingual Translation ---")
    analyzer = LegislativeAnalyzer()
    
    test_text = "The Green Energy Transition Act aims to reduce carbon emissions by 50% by the year 2030."
    
    print(f"Original: {test_text}")
    
    print("\nTranslating to Hindi...")
    hindi_text = analyzer._translate_if_needed(test_text, "Hindi")
    print(f"Hindi: {hindi_text}")
    
    print("\nTranslating to Gujarati...")
    gujarati_text = analyzer._translate_if_needed(test_text, "Gujarati")
    print(f"Gujarati: {gujarati_text}")

if __name__ == "__main__":
    test_translation()
