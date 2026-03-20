import difflib
from src.utils.analyzer import LegislativeAnalyzer

def test_compare():
    text1 = "The Green Energy Act 2026 mandates a 30% solar rebate for all citizens applying before Dec 1. It also introduces a 5% tax on carbon emissions."
    text2 = "The Green Energy Act 2026 mandates a 40% solar rebate for all citizens applying before Dec 1. It also introduces a 10% tax on carbon emissions. And a new EV subsidy."
    
    # We can split text into sentences for comparison
    import re
    sentences1 = [s.strip() for s in re.split(r'(?<=[.!?]) +', text1) if s.strip()]
    sentences2 = [s.strip() for s in re.split(r'(?<=[.!?]) +', text2) if s.strip()]
    
    differ = difflib.Differ()
    diff = list(differ.compare(sentences1, sentences2))
    
    added = []
    removed = []
    unchanged = []
    
    for line in diff:
        if line.startswith('+ '):
            added.append(line[2:])
        elif line.startswith('- '):
            removed.append(line[2:])
        elif line.startswith('  '):
            unchanged.append(line[2:])
            
    print("--- ADDED ---")
    for a in added: print(f"- {a}")
    print("\n--- REMOVED ---")
    for r in removed: print(f"- {r}")

if __name__ == "__main__":
    test_compare()
