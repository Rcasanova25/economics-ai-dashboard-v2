"""Preview extracted candidates to assess quality"""

import json
from pathlib import Path

def preview_candidates():
    """Show a sample of extracted candidates"""
    
    candidates_file = Path("extraction_output/oecd-artificial-intelligence-review-2025.pdf_candidates.json")
    
    with open(candidates_file, 'r') as f:
        candidates = json.load(f)
    
    print(f"Total candidates: {len(candidates)}\n")
    
    # Filter out obvious non-metrics (single digit values)
    meaningful = [c for c in candidates if c['numeric_value'] > 10 or c['unit_hint']]
    
    print(f"Potentially meaningful candidates: {len(meaningful)}\n")
    
    print("Sample candidates:")
    print("-" * 80)
    
    for i, candidate in enumerate(meaningful[:15]):
        print(f"\n{i+1}. Value: {candidate['numeric_value']} {candidate['unit_hint']}")
        print(f"   Page: {candidate['page_number']} | Method: {candidate['extraction_method']}")
        print(f"   Category: {candidate['suggested_category']}")
        print(f"   Geography: {candidate['suggested_geography']}")
        print(f"   Context: {candidate['surrounding_text'][:100] if candidate['surrounding_text'] else 'No context'}")
        print(f"   Raw: {candidate['raw_value'][:100]}")

if __name__ == "__main__":
    preview_candidates()