"""
Analyze Extraction Quality
Version: 1.0
Date: January 24, 2025

This script analyzes the extracted data to identify:
1. Compound term numbers (COVID-19, Fortune 500, etc.)
2. Other nonsensical patterns
3. Overall data quality metrics
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import json
from collections import Counter


def analyze_extraction_quality(csv_path: str):
    """Analyze extracted metrics for quality issues"""
    
    print("Loading extracted metrics...")
    df = pd.read_csv(csv_path)
    print(f"Total metrics: {len(df)}")
    
    # Initialize findings
    findings = {
        "total_metrics": len(df),
        "issues": {
            "compound_terms": [],
            "suspicious_values": [],
            "context_mismatches": [],
            "extreme_outliers": []
        },
        "patterns": {}
    }
    
    # 1. Check for compound term patterns
    print("\n1. Checking for compound term extractions...")
    compound_patterns = [
        (r'COVID[\-\s]?19', 19),
        (r'Fortune\s+500', 500),
        (r'S&P\s+500', 500),
        (r'24/7', [24, 7]),
        (r'9[\-\s]?to[\-\s]?5', [9, 5]),
        (r'401\s*\(?\s*k\s*\)?', 401),
        (r'360[\-\s]?degree', 360),
        (r'365[\-\s]?day', 365),
        (r'52[\-\s]?week', 52),
        (r'100[\-\s]?year', 100)
    ]
    
    compound_issues = []
    for idx, row in df.iterrows():
        context = str(row['context']).lower()
        value = row['value']
        
        for pattern, expected_val in compound_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                if isinstance(expected_val, list):
                    if value in expected_val:
                        compound_issues.append({
                            'metric_id': row['metric_id'],
                            'value': value,
                            'pattern': pattern,
                            'context': str(row['context'])[:100],
                            'metric_type': row['metric_type']
                        })
                else:
                    if abs(value - expected_val) < 1:
                        compound_issues.append({
                            'metric_id': row['metric_id'],
                            'value': value,
                            'pattern': pattern,
                            'context': str(row['context'])[:100],
                            'metric_type': row['metric_type']
                        })
    
    findings['issues']['compound_terms'] = compound_issues
    print(f"Found {len(compound_issues)} potential compound term issues")
    
    # 2. Check for suspicious small values
    print("\n2. Checking for suspicious small values...")
    small_values = df[(df['value'] < 100) & (df['unit'].isin(['number', 'count']))]
    
    suspicious_small = []
    for idx, row in small_values.iterrows():
        context_lower = str(row['context']).lower()
        value = row['value']
        
        # Check if it's likely a real small number
        legitimate_patterns = [
            'pilot', 'trial', 'test', 'initial', 'startup', 'small',
            'few', 'handful', 'several', 'limited', 'select'
        ]
        
        if not any(pattern in context_lower for pattern in legitimate_patterns):
            # Check for number extraction from text
            if value < 50:  # Focus on very small numbers
                suspicious_small.append({
                    'metric_id': row['metric_id'],
                    'value': value,
                    'unit': row['unit'],
                    'metric_type': row['metric_type'],
                    'context': str(row['context'])[:100],
                    'sector': row['sector']
                })
    
    findings['issues']['suspicious_values'] = suspicious_small[:20]  # Top 20
    print(f"Found {len(suspicious_small)} suspicious small values")
    
    # 3. Check context-metric mismatches
    print("\n3. Checking for context-metric mismatches...")
    mismatches = []
    
    employment_metrics = df[df['metric_type'].str.contains('employment|job', case=False)]
    for idx, row in employment_metrics.iterrows():
        context_lower = str(row['context']).lower()
        
        # Check if context is about something else
        non_employment_patterns = [
            'year', 'percent', 'dollar', 'revenue', 'cost', 'price',
            'temperature', 'degree', 'chapter', 'section', 'page',
            'version', 'release', 'model'
        ]
        
        if any(pattern in context_lower for pattern in non_employment_patterns):
            if not any(emp_word in context_lower for emp_word in ['employee', 'job', 'worker', 'staff']):
                mismatches.append({
                    'metric_id': row['metric_id'],
                    'value': row['value'],
                    'metric_type': row['metric_type'],
                    'context': row['context'][:100]
                })
    
    findings['issues']['context_mismatches'] = mismatches[:20]  # Top 20
    print(f"Found {len(mismatches)} context-metric mismatches")
    
    # 4. Statistical outliers by metric type
    print("\n4. Checking for statistical outliers...")
    outliers = []
    
    for metric_type in df['metric_type'].unique():
        subset = df[df['metric_type'] == metric_type]
        if len(subset) > 10:  # Need enough data
            values = subset['value'].values
            Q1 = np.percentile(values, 25)
            Q3 = np.percentile(values, 75)
            IQR = Q3 - Q1
            
            # Extreme outliers
            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR
            
            extreme_subset = subset[(subset['value'] < lower_bound) | (subset['value'] > upper_bound)]
            
            for idx, row in extreme_subset.iterrows():
                outliers.append({
                    'metric_id': row['metric_id'],
                    'value': row['value'],
                    'metric_type': metric_type,
                    'context': str(row['context'])[:100],
                    'bounds': f"[{lower_bound:.1f}, {upper_bound:.1f}]"
                })
    
    findings['issues']['extreme_outliers'] = outliers[:20]  # Top 20
    print(f"Found {len(outliers)} extreme outliers")
    
    # 5. Summary statistics
    print("\n5. Overall quality metrics...")
    findings['summary'] = {
        'confidence_distribution': {
            'high': len(df[df['confidence'] >= 0.7]),
            'medium': len(df[(df['confidence'] >= 0.5) & (df['confidence'] < 0.7)]),
            'low': len(df[df['confidence'] < 0.5])
        },
        'sectors': df['sector'].value_counts().to_dict(),
        'metric_types': df['metric_type'].value_counts().head(10).to_dict(),
        'units': df['unit'].value_counts().to_dict()
    }
    
    # 6. Estimate removal rate
    total_issues = (len(compound_issues) + 
                   len(suspicious_small) + 
                   len(mismatches) + 
                   len(outliers))
    
    # Avoid double counting
    unique_problematic_ids = set()
    for issue_list in [compound_issues, suspicious_small, mismatches, outliers]:
        for issue in issue_list:
            unique_problematic_ids.add(issue['metric_id'])
    
    estimated_removal = len(unique_problematic_ids)
    findings['estimated_removal_rate'] = (estimated_removal / len(df)) * 100
    
    return findings


def create_cleaning_recommendations(findings: dict):
    """Create specific cleaning recommendations"""
    
    print("\n" + "="*60)
    print("CLEANING RECOMMENDATIONS")
    print("="*60)
    
    recommendations = []
    
    # 1. Compound terms
    if findings['issues']['compound_terms']:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Compound Term Numbers',
            'count': len(findings['issues']['compound_terms']),
            'action': 'Filter metrics where value matches compound term patterns',
            'examples': findings['issues']['compound_terms'][:3]
        })
    
    # 2. Suspicious small values
    if findings['issues']['suspicious_values']:
        recommendations.append({
            'priority': 'MEDIUM',
            'issue': 'Suspicious Small Values',
            'count': len(findings['issues']['suspicious_values']),
            'action': 'Review small numbers without legitimate context',
            'examples': findings['issues']['suspicious_values'][:3]
        })
    
    # 3. Context mismatches
    if findings['issues']['context_mismatches']:
        recommendations.append({
            'priority': 'HIGH',
            'issue': 'Context-Metric Mismatches',
            'count': len(findings['issues']['context_mismatches']),
            'action': 'Validate metric type matches context content',
            'examples': findings['issues']['context_mismatches'][:3]
        })
    
    print(f"\nEstimated removal rate: {findings['estimated_removal_rate']:.1f}%")
    
    if findings['estimated_removal_rate'] > 20:
        print("[WARNING] High removal rate expected. Review cleaning rules carefully.")
    
    return recommendations


def main():
    """Main analysis function"""
    # Find the latest extraction output
    extraction_dirs = list(Path('.').glob('extraction_output_*'))
    if not extraction_dirs:
        print("No extraction output found!")
        return
    
    latest_dir = sorted(extraction_dirs)[-1]
    csv_path = latest_dir / 'all_metrics_extracted.csv'
    
    print(f"Analyzing: {csv_path}")
    
    # Run analysis
    findings = analyze_extraction_quality(str(csv_path))
    
    # Save findings
    output_path = latest_dir / 'quality_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(findings, f, indent=2, default=str)
    
    print(f"\nAnalysis saved to: {output_path}")
    
    # Create recommendations
    recommendations = create_cleaning_recommendations(findings)
    
    # Show sample issues
    print("\nSAMPLE ISSUES FOUND:")
    print("-" * 60)
    
    if findings['issues']['compound_terms']:
        print("\nCompound Term Examples:")
        for issue in findings['issues']['compound_terms'][:5]:
            print(f"  ID {issue['metric_id']}: {issue['value']} from '{issue['context'][:50]}...'")
    
    if findings['issues']['suspicious_values']:
        print("\nSuspicious Value Examples:")
        for issue in findings['issues']['suspicious_values'][:5]:
            print(f"  ID {issue['metric_id']}: {issue['value']} {issue['unit']} in {issue['sector']}")
    
    print("\nNext step: Create cleaning script based on these findings")


if __name__ == "__main__":
    main()