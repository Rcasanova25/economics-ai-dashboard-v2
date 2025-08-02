"""
Analyze Context Windows Around Extracted Values
Version: 1.0
Date: January 24, 2025

This script examines the 5 words before and after each extracted value
to better understand if the extraction makes sense.
"""

import pandas as pd
import re
from pathlib import Path
import json


def extract_context_window(full_context, value, window=5):
    """Extract N words before and after the value in context"""
    
    # Convert to string and handle NaN
    context = str(full_context)
    value_str = str(int(value)) if value == int(value) else str(value)
    
    # Find all occurrences of the value
    pattern = r'\b' + re.escape(value_str) + r'\b'
    matches = list(re.finditer(pattern, context))
    
    if not matches:
        # Try to find the value with variations (e.g., 19.0 as "19")
        if '.' in value_str:
            value_str = str(int(float(value_str)))
            pattern = r'\b' + re.escape(value_str) + r'\b'
            matches = list(re.finditer(pattern, context))
    
    if not matches:
        return None, None
    
    # Use the first match
    match = matches[0]
    start, end = match.span()
    
    # Extract words before
    before_text = context[:start].strip()
    before_words = before_text.split()[-window:] if before_text else []
    
    # Extract words after  
    after_text = context[end:].strip()
    after_words = after_text.split()[:window] if after_text else []
    
    return ' '.join(before_words), ' '.join(after_words)


def analyze_suspicious_metrics(csv_path: str):
    """Analyze metrics with detailed context windows"""
    
    print("Loading metrics...")
    df = pd.read_csv(csv_path)
    
    # Categories of analysis
    analyses = {
        "COVID-19 Patterns": [],
        "SME Size (500 employees)": [],
        "Citation Years": [],
        "Round Numbers (100)": [],
        "Small Numbers (<20)": [],
        "Fortune/S&P 500": []
    }
    
    print("\nAnalyzing context windows...")
    
    for idx, row in df.iterrows():
        value = row['value']
        context = str(row['context'])
        metric_type = row['metric_type']
        
        before, after = extract_context_window(context, value)
        
        if before is None:
            continue
            
        # Full context phrase
        context_phrase = f"{before} [{value}] {after}"
        
        # 1. COVID-19 pattern
        if value == 19 and any(term in context.lower() for term in ['covid', 'pandemic', 'coronavirus']):
            analyses["COVID-19 Patterns"].append({
                'id': row['metric_id'],
                'value': value,
                'metric_type': metric_type,
                'before': before,
                'after': after,
                'full_phrase': context_phrase
            })
        
        # 2. SME Size (500 employees)
        elif value == 500 and any(term in context_phrase.lower() for term in ['fewer than', 'less than', 'under', 'small', 'sme']):
            analyses["SME Size (500 employees)"].append({
                'id': row['metric_id'],
                'value': value,
                'metric_type': metric_type,
                'before': before,
                'after': after,
                'full_phrase': context_phrase,
                'is_valid': True  # This is actually valid data!
            })
        
        # 3. Fortune/S&P 500
        elif value == 500 and any(term in context_phrase.lower() for term in ['fortune', 's&p', 'index']):
            analyses["Fortune/S&P 500"].append({
                'id': row['metric_id'],
                'value': value,
                'metric_type': metric_type,
                'before': before,
                'after': after,
                'full_phrase': context_phrase,
                'is_valid': False
            })
        
        # 4. Citation years
        elif 2000 <= value <= 2030 and value == int(value):
            # Check for citation patterns in immediate context
            citation_patterns = ['study', 'paper', 'published', 'article', 'research', 
                               'author', 'et al', 'journal', 'conference', '(', ')']
            if any(pat in context_phrase.lower() for pat in citation_patterns):
                analyses["Citation Years"].append({
                    'id': row['metric_id'],
                    'value': value,
                    'metric_type': metric_type,
                    'before': before,
                    'after': after,
                    'full_phrase': context_phrase
                })
        
        # 5. Round number 100
        elif value == 100:
            analyses["Round Numbers (100)"].append({
                'id': row['metric_id'],
                'value': value,
                'metric_type': metric_type,
                'unit': row['unit'],
                'before': before,
                'after': after,
                'full_phrase': context_phrase
            })
        
        # 6. Small suspicious numbers
        elif value < 20 and row['unit'] in ['number', 'count']:
            # Check if it seems legitimate
            legit_patterns = ['pilot', 'trial', 'initial', 'few', 'several', 'small', 'handful']
            seems_legit = any(pat in context_phrase.lower() for pat in legit_patterns)
            
            if not seems_legit:
                analyses["Small Numbers (<20)"].append({
                    'id': row['metric_id'],
                    'value': value,
                    'metric_type': metric_type,
                    'before': before,
                    'after': after,
                    'full_phrase': context_phrase
                })
    
    return analyses


def print_analysis_results(analyses: dict):
    """Print analysis results in a readable format"""
    
    print("\n" + "="*80)
    print("CONTEXT WINDOW ANALYSIS RESULTS")
    print("="*80)
    
    for category, items in analyses.items():
        if not items:
            continue
            
        print(f"\n{category} ({len(items)} found):")
        print("-" * 60)
        
        # Show first 5 examples
        for item in items[:5]:
            print(f"\nID {item['id']}: {item['value']}")
            print(f"Type: {item['metric_type']}")
            print(f"Context: {item['full_phrase']}")
            
            if 'is_valid' in item:
                validity = "VALID" if item['is_valid'] else "INVALID"
                print(f"Assessment: {validity}")
    
    # Summary of valid vs invalid
    print("\n" + "="*80)
    print("VALIDITY ASSESSMENT")
    print("="*80)
    
    total_analyzed = sum(len(items) for items in analyses.values())
    
    # Count valid SME data
    valid_sme = len(analyses.get("SME Size (500 employees)", []))
    invalid_fortune = len(analyses.get("Fortune/S&P 500", []))
    
    print(f"\nTotal suspicious metrics analyzed: {total_analyzed}")
    print(f"Valid SME size references (500): {valid_sme}")
    print(f"Invalid Fortune 500 references: {invalid_fortune}")
    print(f"COVID-19 extractions: {len(analyses.get('COVID-19 Patterns', []))}")
    print(f"Citation years: {len(analyses.get('Citation Years', []))}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("1. PRESERVE: SME definitions with '500 employees' or 'fewer than 500'")
    print("2. REMOVE: COVID-19 where 19 is extracted")
    print("3. REMOVE: Citation years in academic references")
    print("4. REVIEW: Round numbers (100) - could be valid percentages or counts")
    print("5. CONTEXT-SPECIFIC: Small numbers need individual review")


def main():
    """Main analysis function"""
    # Find latest extraction
    extraction_dirs = list(Path('.').glob('extraction_output_*'))
    if not extraction_dirs:
        print("No extraction output found!")
        return
    
    latest_dir = sorted(extraction_dirs)[-1]
    csv_path = latest_dir / 'all_metrics_extracted.csv'
    
    print(f"Analyzing: {csv_path}")
    
    # Run analysis
    analyses = analyze_suspicious_metrics(str(csv_path))
    
    # Print results
    print_analysis_results(analyses)
    
    # Save detailed results
    output_path = latest_dir / 'context_window_analysis.json'
    
    # Convert to serializable format
    serializable = {}
    for key, items in analyses.items():
        serializable[key] = items
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(serializable, f, indent=2)
    
    print(f"\nDetailed analysis saved to: {output_path}")


if __name__ == "__main__":
    main()