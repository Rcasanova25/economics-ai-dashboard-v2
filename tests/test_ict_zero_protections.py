"""
Test ICT and Meaningful Zero Protections
Verify that ICT data and meaningful zeros are preserved
"""

import pandas as pd
from metric_validator import MetricValidator
from source_cleanup_enhanced import EnhancedSourceAnalyzer
import os
import sys

def test_ict_preservation():
    """Test that ICT data is preserved"""
    validator = MetricValidator()
    
    # Test various ICT patterns
    test_cases = [
        "investment in ICT infrastructure reached $5 billion",
        "information communication technology adoption at 45%",
        "telecom sector growth of 12%",
        "digital infrastructure spending increased",
        "Information Technology services expanded by 20%",
        "communication technology investments rose"
    ]
    
    print("Testing ICT Detection:")
    for context in test_cases:
        is_ict = validator.is_ict_data(context)
        print(f"  '{context[:50]}...' -> ICT: {is_ict}")
        assert is_ict, f"Failed to detect ICT in: {context}"
    
    print("[PASS] All ICT patterns detected successfully\n")

def test_meaningful_zeros():
    """Test that meaningful zeros are detected"""
    validator = MetricValidator()
    
    # Test meaningful zero contexts
    test_cases = [
        (0.0, "survey found 0% adoption rate among small businesses"),
        (0.0, "study indicates zero growth in Q4"),
        (0.0, "findings show no change in productivity"),
        (0.0, "results observed 0% increase"),
        (0.0, "participants reported no productivity gains"),
        (0.0, "employment remained flat at 0% growth"),
        (1.0, "survey found 1% adoption rate"),  # Not zero
        (0.0, "value is 0")  # Not meaningful
    ]
    
    print("Testing Meaningful Zero Detection:")
    for value, context in test_cases:
        is_meaningful = validator.is_meaningful_zero(value, context)
        expected = value == 0 and any(pattern in context.lower() for pattern in 
                                     ['survey', 'study', 'finding', 'observed', 'reported', 'remained flat'])
        print(f"  Value={value}, '{context[:40]}...' -> Meaningful: {is_meaningful}")
        assert is_meaningful == expected, f"Incorrect detection for: {context}"
    
    print("[PASS] All meaningful zeros detected correctly\n")

def test_full_pipeline():
    """Test the full pipeline with sample data"""
    print("Testing Full Pipeline with Sample Data:")
    
    # Create test data
    test_data = pd.DataFrame([
        # ICT data that should be kept
        {
            'source_id': 99,
            'value': 45.0,
            'unit': 'percentage',
            'year': 2024,
            'metric_type': 'adoption_rate',
            'context': 'ICT adoption in financial services reached 45%'
        },
        # Meaningful zero that should be kept
        {
            'source_id': 99,
            'value': 0.0,
            'unit': 'percentage',
            'year': 2024,
            'metric_type': 'growth_rate',
            'context': 'Survey results show 0% productivity growth in traditional sectors'
        },
        # Regular duplicate that should be removed
        {
            'source_id': 99,
            'value': 10.0,
            'unit': 'percentage',
            'year': 2024,
            'metric_type': 'general_rate',
            'context': 'General increase observed'
        },
        {
            'source_id': 99,
            'value': 10.0,
            'unit': 'percentage',
            'year': 2024,
            'metric_type': 'general_rate',
            'context': 'General increase observed'  # Duplicate
        }
    ])
    
    # Save test data
    test_file = 'test_ict_zero_data.csv'
    test_data.to_csv(test_file, index=False)
    
    try:
        # Run analyzer
        analyzer = EnhancedSourceAnalyzer(99, test_file)
        analyzer.analyze()
        
        # Check results
        print(f"\nResults:")
        print(f"  Records to keep: {len(analyzer.records_to_keep)}")
        print(f"  Records to remove: {len(analyzer.records_to_remove)}")
        
        # Verify ICT data was kept
        ict_kept = any('ICT sector data' in str(r.get('reason', '')) 
                      for r in analyzer.records_to_keep)
        print(f"  ICT data preserved: {ict_kept}")
        assert ict_kept, "ICT data was not preserved!"
        
        # Verify meaningful zero was kept  
        zero_kept = any(r['value'] == 0 and 'survey' in str(r.get('context_preview', '')).lower() 
                       for r in analyzer.records_to_keep)
        print(f"  Meaningful zero preserved: {zero_kept}")
        assert zero_kept, "Meaningful zero was not preserved!"
        
        # Check reasons
        print("\nKept records reasons:")
        for record in analyzer.records_to_keep:
            print(f"  - {record['reason']}")
            
        print("\n[PASS] Full pipeline test passed!")
        
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
        
if __name__ == "__main__":
    print("=" * 60)
    print("ICT and Meaningful Zero Protection Tests")
    print("=" * 60)
    
    test_ict_preservation()
    test_meaningful_zeros()
    test_full_pipeline()
    
    print("\n[SUCCESS] All tests passed! ICT and zero protections are working.")