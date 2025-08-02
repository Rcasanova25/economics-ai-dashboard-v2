"""Preview McKinsey candidates to see quality"""

import json
from pathlib import Path

def preview_mckinsey():
    """Show meaningful McKinsey candidates"""
    
    candidates_file = Path("extraction_output/the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf_candidates.json")
    
    with open(candidates_file, 'r', encoding='utf-8') as f:
        candidates = json.load(f)
    
    print(f"Total candidates: {len(candidates)}\n")
    
    # Filter for percentages and financial values
    percentages = [c for c in candidates if c['unit_hint'] in ['percentage', '%']]
    financial = [c for c in candidates if c['unit_hint'] == 'financial']
    text_extracted = [c for c in candidates if c['extraction_method'] == 'text']
    
    print(f"Percentages found: {len(percentages)}")
    print(f"Financial values found: {len(financial)}")
    print(f"Text extraction found: {len(text_extracted)}")
    
    print("\n" + "="*80)
    print("PERCENTAGE METRICS")
    print("="*80)
    
    # Show percentages between 10-100
    meaningful_pct = [c for c in percentages if 10 <= c['numeric_value'] <= 100]
    
    for i, candidate in enumerate(meaningful_pct[:10]):
        print(f"\n{i+1}. {candidate['numeric_value']}%")
        print(f"   Page: {candidate['page_number']} | Category: {candidate['suggested_category']}")
        print(f"   Context: {candidate['surrounding_text'][:200] if candidate['surrounding_text'] else 'No context'}")
    
    print("\n" + "="*80)
    print("TEXT-EXTRACTED METRICS")
    print("="*80)
    
    for i, candidate in enumerate(text_extracted[:10]):
        print(f"\n{i+1}. {candidate['numeric_value']} {candidate['unit_hint']}")
        print(f"   Page: {candidate['page_number']} | Category: {candidate['suggested_category']}")
        print(f"   Context: {candidate['surrounding_text'][:200] if candidate['surrounding_text'] else 'No context'}")
        print(f"   Raw: {candidate['raw_value']}")

if __name__ == "__main__":
    preview_mckinsey()