"""
Test Suite for Data Cleanup Operations
Ensures data integrity is maintained during cleanup
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import tempfile
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from source_cleanup_template import SourceCleanupAnalyzer


class TestDuplicateHandling:
    """Test that duplicate handling preserves first occurrences"""
    
    def test_duplicate_groups_identification(self):
        """Test that duplicate groups are correctly identified"""
        # Create test data with known duplicates
        test_data = pd.DataFrame({
            'source_id': [1, 1, 1, 1, 1],
            'value': [10.0, 10.0, 20.0, 20.0, 30.0],
            'unit': ['percentage', 'percentage', 'percentage', 'percentage', 'percentage'],
            'year': [2024, 2024, 2024, 2024, 2024],
            'metric_type': ['general_rate'] * 5,
            'context': ['context1', 'context2', 'context3', 'context4', 'context5']
        })
        
        # Save to temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            # Create analyzer instance
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.identify_duplicate_groups()
            
            # Verify duplicate groups
            assert len(analyzer.duplicate_groups) == 2  # Two groups with duplicates
            
            # Check first group (value=10.0)
            group1 = analyzer.duplicate_groups[(10.0, 'percentage', 2024)]
            assert group1['first'] == 0  # First occurrence at index 0
            assert group1['duplicates'] == [1]  # Second occurrence at index 1
            
            # Check second group (value=20.0)
            group2 = analyzer.duplicate_groups[(20.0, 'percentage', 2024)]
            assert group2['first'] == 2  # First occurrence at index 2
            assert group2['duplicates'] == [3]  # Second occurrence at index 3
            
        finally:
            Path(temp_file).unlink()
    
    def test_first_occurrence_preserved(self):
        """Test that first occurrence is kept when removing duplicates"""
        # Create test data
        test_data = pd.DataFrame({
            'source_id': [1, 1, 1],
            'value': [50.0, 50.0, 50.0],
            'unit': ['percentage', 'percentage', 'percentage'],
            'year': [2024, 2024, 2024],
            'metric_type': ['adoption_metric'] * 3,
            'context': ['First mention of 50%', 'Second mention', 'Third mention']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.analyze()
            
            # Check that first occurrence is kept
            assert len(analyzer.records_to_keep) >= 1
            kept_record = next((r for r in analyzer.records_to_keep if r['original_id'] == 0), None)
            assert kept_record is not None
            
            # Check that duplicates are marked for removal
            assert len(analyzer.records_to_remove) == 2
            removed_ids = [r['original_id'] for r in analyzer.records_to_remove]
            assert 1 in removed_ids
            assert 2 in removed_ids
            
        finally:
            Path(temp_file).unlink()
    
    def test_no_complete_data_loss(self):
        """Ensure at least one instance of each unique value combination is preserved"""
        # Create test data with multiple unique values
        test_data = pd.DataFrame({
            'source_id': [1] * 10,
            'value': [10.0, 10.0, 20.0, 20.0, 30.0, 40.0, 40.0, 40.0, 50.0, 60.0],
            'unit': ['percentage'] * 10,
            'year': [2024] * 10,
            'metric_type': ['general_rate'] * 10,
            'context': [f'Context {i}' for i in range(10)]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.analyze()
            
            # Get all unique values from original data
            unique_values = test_data['value'].unique()
            
            # Collect all values that will be kept
            kept_values = set()
            for record in analyzer.records_to_keep:
                kept_values.add(record['value'])
            for record in analyzer.records_to_modify:
                kept_values.add(record['value'])
            
            # Verify each unique value has at least one preserved instance
            for value in unique_values:
                assert value in kept_values, f"Value {value} would be completely lost"
                
        finally:
            Path(temp_file).unlink()


class TestMetricReclassification:
    """Test metric type reclassification logic"""
    
    def test_readiness_metric_classification(self):
        """Test that readiness-related metrics are correctly classified"""
        test_contexts = [
            "AI readiness score for organizations",
            "maturity level assessment",
            "preparedness stage analysis",
            "technology readiness level"
        ]
        
        # Create a minimal test CSV file
        test_data = pd.DataFrame({
            'source_id': [1],
            'value': [50.0],
            'unit': ['percentage'],
            'year': [2024],
            'metric_type': ['general_rate'],
            'context': ['test']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            
            for context in test_contexts:
                new_type = analyzer.classify_metric_type(context, 50.0, 'percentage', 'general_rate')
                assert new_type == 'readiness_metric', f"Failed to classify: {context}"
        finally:
            Path(temp_file).unlink()
    
    def test_cost_metric_classification(self):
        """Test that cost-related metrics are correctly classified"""
        test_contexts = [
            "ROI from AI implementation",
            "cost reduction achieved",
            "investment in AI technology",
            "budget allocation for AI",
            "expense analysis"
        ]
        
        # Create a minimal test CSV file
        test_data = pd.DataFrame({
            'source_id': [1],
            'value': [1000000],
            'unit': ['usd'],
            'year': [2024],
            'metric_type': ['general_rate'],
            'context': ['test']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            
            for context in test_contexts:
                new_type = analyzer.classify_metric_type(context, 1000000, 'usd', 'general_rate')
                assert new_type == 'cost_metric', f"Failed to classify: {context}"
        finally:
            Path(temp_file).unlink()
    
    def test_adoption_metric_classification(self):
        """Test that adoption-related metrics are correctly classified"""
        test_contexts = [
            "companies adopting AI",
            "AI implementation rate",
            "deployment of machine learning",
            "organizations using generative AI",
            "AI utilization percentage"
        ]
        
        # Create a minimal test CSV file
        test_data = pd.DataFrame({
            'source_id': [1],
            'value': [75.0],
            'unit': ['percentage'],
            'year': [2024],
            'metric_type': ['general_rate'],
            'context': ['test']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            
            for context in test_contexts:
                new_type = analyzer.classify_metric_type(context, 75.0, 'percentage', 'general_rate')
                assert new_type == 'adoption_metric', f"Failed to classify: {context}"
        finally:
            Path(temp_file).unlink()


class TestDataIntegrity:
    """Test overall data integrity preservation"""
    
    def test_zero_percentage_handling(self):
        """Test that meaningful zero percentages are preserved"""
        test_data = pd.DataFrame({
            'source_id': [1, 1, 1, 1],
            'value': [0.0, 0.0, 0.0, 0.0],
            'unit': ['percentage'] * 4,
            'year': [2024] * 4,
            'metric_type': ['general_rate'] * 4,
            'context': [
                'No change in productivity',  # Should be kept
                'Zero growth observed',        # Should be kept
                '0',                          # Should be removed (artifact)
                'Table 1. 0'                  # Should be removed (artifact)
            ]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.analyze()
            
            # Check that meaningful zeros are preserved (either kept or modified)
            kept_contexts = [r['context_preview'] for r in analyzer.records_to_keep]
            modified_contexts = [r['context_preview'] for r in analyzer.records_to_modify]
            all_preserved_contexts = kept_contexts + modified_contexts
            
            assert any('no change' in ctx.lower() for ctx in all_preserved_contexts), \
                f"'No change' context not preserved. Kept: {kept_contexts}, Modified: {modified_contexts}"
            assert any('zero growth' in ctx.lower() for ctx in all_preserved_contexts), \
                f"'Zero growth' context not preserved. Kept: {kept_contexts}, Modified: {modified_contexts}"
            
            # Check that artifacts are removed
            removed_contexts = [r['context_preview'] for r in analyzer.records_to_remove]
            assert any(ctx.strip() == '0' for ctx in removed_contexts), \
                f"Short artifact '0' not removed. Removed contexts: {removed_contexts}"
            
        finally:
            Path(temp_file).unlink()
    
    def test_unit_correction(self):
        """Test that incorrect units are identified for correction"""
        test_data = pd.DataFrame({
            'source_id': [1, 1],
            'value': [100.0, 500.0],
            'unit': ['billions_usd', 'billions_usd'],
            'year': [2024, 2024],
            'metric_type': ['financial_metric'] * 2,
            'context': [
                'investment of 100k USD',  # Should be corrected to thousands
                'revenue of 500 billion'   # Should remain billions
            ]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.analyze()
            
            # Check that unit correction is identified
            assert len(analyzer.records_to_modify) >= 1
            
            # Find the record that should be corrected
            corrected = next((r for r in analyzer.records_to_modify 
                            if '100k' in r['context_preview']), None)
            assert corrected is not None
            assert 'billions_usd should be thousands' in corrected['reason']
            
        finally:
            Path(temp_file).unlink()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_source_handling(self):
        """Test handling of source with no records"""
        test_data = pd.DataFrame({
            'source_id': [2, 2],  # Different source
            'value': [10.0, 20.0],
            'unit': ['percentage'] * 2,
            'year': [2024] * 2,
            'metric_type': ['general_rate'] * 2,
            'context': ['ctx1', 'ctx2']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            # Try to analyze source 1 (which has no records)
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            analyzer.analyze()
            
            # Should handle gracefully
            assert len(analyzer.records_to_keep) == 0
            assert len(analyzer.records_to_remove) == 0
            assert len(analyzer.records_to_modify) == 0
            
        finally:
            Path(temp_file).unlink()
    
    def test_malformed_data_handling(self):
        """Test handling of malformed data"""
        test_data = pd.DataFrame({
            'source_id': [1, 1, 1],
            'value': [np.nan, 'invalid', 50.0],  # Mixed types and NaN
            'unit': ['percentage', None, 'percentage'],
            'year': [2024, 2024, 2024],
            'metric_type': ['general_rate'] * 3,
            'context': [None, '', 'Valid context']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            analyzer = SourceCleanupAnalyzer(1, temp_file)
            # Should not raise an exception
            analyzer.analyze()
            
            # At least the valid record should be processed
            total_processed = (len(analyzer.records_to_keep) + 
                             len(analyzer.records_to_remove) + 
                             len(analyzer.records_to_modify))
            assert total_processed >= 1
            
        finally:
            Path(temp_file).unlink()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])