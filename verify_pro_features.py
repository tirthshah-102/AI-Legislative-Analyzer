import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from src.utils.analyzer import LegislativeAnalyzer

def test_analyzer_pro_methods():
    analyzer = LegislativeAnalyzer()
    dummy_text = "The Green Energy Act 2024 requires all companies to reduce carbon emissions by 20% by December 2025. Failure to comply results in a fine of $10,000. The Ministry of Environment will oversee this."
    dummy_text_v2 = "The Green Energy Act 2025 requires all companies to reduce carbon emissions by 30% by January 2026. Failure to comply results in a fine of $15,000. Small businesses are exempt."

    print("--- Testing Pro Features Logic ---")

    # 1. Compliance
    print("\n[1] Testing Compliance Checklist...")
    compliance = analyzer.generate_compliance_checklist(dummy_text)
    print("Result:", compliance[:100], "...")

    # 2. Risk/Risk
    print("\n[2] Testing Risk Analysis...")
    risk = analyzer.analyze_risk_and_complexity(dummy_text)
    print("Result:", risk)

    # 3. Timeline
    print("\n[3] Testing Timeline Extraction...")
    timeline = analyzer.extract_timeline_data(dummy_text)
    print("Result:", timeline)

    # 4. Entities/Citations
    print("\n[4] Testing Citations & Entities...")
    citations = analyzer.extract_citations_and_entities(dummy_text)
    print("Result:", citations[:100], "...")

    # 5. Entity Map
    print("\n[5] Testing Entity Map...")
    entities = analyzer.extract_entity_map(dummy_text)
    print("Result:", entities)

    # 6. Comparison
    print("\n[6] Testing Bill Comparison...")
    comparison = analyzer.compare_bills_analysis(dummy_text, dummy_text_v2)
    print("Result:", comparison[:100], "...")

    print("\n--- Logic Verification Complete ---")

if __name__ == "__main__":
    try:
        test_analyzer_pro_methods()
    except Exception as e:
        print(f"Error during verification: {e}")
