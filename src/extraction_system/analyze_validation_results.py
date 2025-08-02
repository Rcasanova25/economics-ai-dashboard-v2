"""Analyze validation results from UI testing"""

import json
from pathlib import Path
from collections import Counter

def analyze_results():
    """Analyze the validation decisions"""
    
    validated_file = Path("extraction_output/oecd-artificial-intelligence-review-2025.pdf_validated.json")
    
    with open(validated_file, 'r') as f:
        validated = json.load(f)
    
    print(f"Total validated candidates: {len(validated)}")
    
    # Count decisions
    decisions = Counter(item['decision'] for item in validated)
    
    print("\nValidation decisions:")
    for decision, count in decisions.items():
        print(f"  {decision}: {count}")
    
    # Analyze accepted metrics
    accepted = [item for item in validated if item['decision'] == 'accept']
    
    if accepted:
        print(f"\nAccepted metrics: {len(accepted)}")
        print("-" * 60)
        
        for item in accepted:
            print(f"\nValue: {item['numeric_value']}")
            print(f"Category: {item['category']}")
            print(f"Type: {item['type']}")
            print(f"Unit: {item['unit']}")
            print(f"Context: {item['surrounding_text']}")
            print(f"Page: {item['page_number']}")
    
    # Time analysis
    print("\n" + "="*60)
    print("VALIDATION EFFICIENCY")
    print("="*60)
    
    # Calculate time spent (if we had timestamps)
    total_candidates = 66
    validated_count = len(validated)
    
    print(f"Validated: {validated_count}/{total_candidates} ({validated_count/total_candidates*100:.1f}%)")
    
    # Estimate time
    if validated_count > 0:
        avg_seconds_per_candidate = 5  # Rough estimate
        total_minutes = (validated_count * avg_seconds_per_candidate) / 60
        print(f"Estimated time: {total_minutes:.1f} minutes")
        print(f"Validation rate: ~{60/avg_seconds_per_candidate:.0f} candidates/minute")

if __name__ == "__main__":
    analyze_results()