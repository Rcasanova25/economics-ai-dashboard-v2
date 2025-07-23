"""
Comprehensive tests for the enhanced cleanup modules
"""

import pytest
import pandas as pd
import numpy as np
import os
import json
import tempfile
from datetime import datetime

from metric_validator import MetricValidator
from quality_tracker import QualityTracker
from source_cleanup_enhanced import EnhancedSourceAnalyzer


class TestMetricValidator:
    """Test the MetricValidator module"""
    
    @pytest.fixture
    def validator(self):
        return MetricValidator()
    
    def test_validate_employment_metric_with_financial_unit(self, validator):
        """Test that employment metrics with financial units are flagged"""
        issues = validator.validate_against_schema(
            metric_type='employment_metric',
            value=1000,
            unit='millions_usd',
            context='company has 1000 employees'
        )
        
        assert len(issues) > 0
        assert any('Invalid unit' in issue['reason'] for issue in issues)
        assert issues[0]['confidence'] > 0.9
        
    def test_validate_adoption_rate_over_100_percent(self, validator):
        """Test that adoption rates over 100% are flagged"""
        issues = validator.validate_against_schema(
            metric_type='adoption_metric',
            value=150,
            unit='percentage',
            context='adoption rate increased to 150%'
        )
        
        assert len(issues) > 0
        assert any('outside expected range' in issue['reason'] for issue in issues)
        
    def test_validate_zero_employment_invalid(self, validator):
        """Test that zero employees is flagged as suspicious"""
        issues = validator.validate_against_schema(
            metric_type='employment_metric',
            value=0,
            unit='number',
            context='company employees'
        )
        
        assert len(issues) > 0
        assert any('Zero value suspicious' in issue['reason'] for issue in issues)
        
    def test_detect_citation_year(self, validator):
        """Test citation year detection"""
        # Should detect citation
        assert validator.detect_citation_year(
            value=2024,
            year=2024,
            context='according to Smith (2024), AI adoption is increasing'
        ) == True
        
        # Should not detect citation
        assert validator.detect_citation_year(
            value=85,
            year=2024,
            context='adoption rate reached 85% in 2024'
        ) == False
        
    def test_classify_metric_type(self, validator):
        """Test metric type classification"""
        # Test adoption classification
        result = validator.classify_metric_type(
            context='companies are adopting AI technologies',
            value=75,
            unit='percentage'
        )
        assert result == 'adoption_metric'
        
        # Test investment classification
        result = validator.classify_metric_type(
            context='total investment in AI reached billions',
            value=5.2,
            unit='billions_usd'
        )
        assert result == 'investment_metric'
        
        # Test productivity classification
        result = validator.classify_metric_type(
            context='productivity increased by 25%',
            value=25,
            unit='percentage'
        )
        assert result == 'productivity_metric'
        
    def test_cross_metric_rules(self, validator):
        """Test cross-metric validation rules"""
        # Test employment metric with financial unit
        issues = validator.apply_cross_metric_rules(
            metric_type='employment_metric',
            value=1000,
            unit='millions_usd',
            year=2024,
            context='company workforce'
        )
        
        assert len(issues) > 0
        assert any('Financial units should not appear with employment metrics' 
                  in issue['reason'] for issue in issues)
        
    def test_unit_metric_consistency(self, validator):
        """Test unit-metric consistency validation"""
        # Valid combination
        is_valid, reason = validator.validate_unit_metric_consistency(
            'employment_metric', 'number'
        )
        assert is_valid == True
        
        # Invalid combination
        is_valid, reason = validator.validate_unit_metric_consistency(
            'employment_metric', 'billions_usd'
        )
        assert is_valid == False
        assert 'invalid for employment_metric' in reason


class TestQualityTracker:
    """Test the QualityTracker module"""
    
    @pytest.fixture
    def tracker(self):
        # Generate a unique filename without creating the file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f'test_quality_{os.getpid()}_{id(self)}.csv')
        
        # Let QualityTracker create the file with proper initialization
        tracker = QualityTracker(tracking_file=temp_file)
        yield tracker
        
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    def test_initialize_tracking_file(self, tracker):
        """Test that tracking file is initialized correctly"""
        assert os.path.exists(tracker.tracking_file)
        
        # The tracker should have headers defined
        assert hasattr(tracker, 'headers')
        assert len(tracker.headers) > 0
        
        expected_headers = [
            'timestamp', 'source_id', 'source_name', 'total_records',
            'kept_records', 'removed_records', 'modified_records'
        ]
        
        for header in expected_headers:
            assert header in tracker.headers
            
    def test_record_source_analysis(self, tracker):
        """Test recording analysis results"""
        analysis_results = {
            'total_records': 100,
            'kept_records': 70,
            'removed_records': 20,
            'modified_records': 10,
            'duplicate_groups': 5,
            'duplicates_removed': 15,
            'top_removal_reason': 'Duplicate record',
            'top_removal_count': 15,
            'schema_version': '1.1'
        }
        
        record = tracker.record_source_analysis(1, 'Test Source', analysis_results)
        
        assert record['source_id'] == 1
        assert record['total_records'] == 100
        assert record['removal_rate'] == 20.0
        assert record['modification_rate'] == 10.0
        assert record['quality_score'] == 75.0  # 100 - 20 - 10/2
        
    def test_get_source_history(self, tracker):
        """Test retrieving source history"""
        # Record multiple analyses with all required fields
        for i in range(3):
            analysis_results = {
                'total_records': 100,
                'kept_records': 70 + i*5,
                'removed_records': 20 - i*3,
                'modified_records': 10 - i*2,
                'duplicate_groups': 0,
                'duplicates_removed': 0,
                'top_removal_reason': 'Test reason',
                'top_removal_count': 5,
                'schema_version': '1.1',
                'notes': ''
            }
            tracker.record_source_analysis(1, 'Test Source', analysis_results)
            
        history = tracker.get_source_history(1)
        assert len(history) == 3
        
        # Check that quality improves over time
        quality_scores = [h['quality_score'] for h in history]
        assert quality_scores[0] < quality_scores[-1]
        
    def test_export_run_summary(self, tracker):
        """Test exporting run summary"""
        # Add some test data
        tracker.current_run['sources'][1] = {
            'source_name': 'Test Source 1',
            'total_records': 100,
            'kept_records': 80,
            'removed_records': 15,
            'modified_records': 5,
            'quality_score': 82.5
        }
        
        # Export JSON
        exports = tracker.export_run_summary('json')
        assert 'json' in exports
        assert os.path.exists(exports['json'])
        
        # Check JSON content
        with open(exports['json'], 'r') as f:
            data = json.load(f)
        assert data['sources_analyzed'] == 1
        assert data['total_records'] == 100
        
        # Cleanup
        os.remove(exports['json'])
        os.rmdir('quality_reports')


class TestEnhancedSourceAnalyzer:
    """Test the main EnhancedSourceAnalyzer"""
    
    @pytest.fixture
    def test_data(self):
        """Create test dataset"""
        data = {
            'source_id': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'value': [0.0, 0.0, 2024.0, 100.0, 50.0, 75.0, 1000.0, 25.0, 30.0, 2023.0],
            'unit': ['millions_usd', 'millions_usd', 'number', 'percentage', 
                     'percentage', 'percentage', 'number', 'percentage', 'billions_usd', 'number'],
            'year': [2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2023],
            'metric_type': ['employment_metric', 'employment_metric', 'unknown_metric',
                           'adoption_metric', 'general_rate', 'productivity_metric',
                           'employment_metric', 'cost_metric', 'investment_metric', 'unknown_metric'],
            'context': [
                'company has over 1000 employees',
                'company has over 1000 employees',  # Duplicate
                'article by Smith (2024) on AI adoption',  # Citation
                'AI adoption rate reached 100%',
                'companies using AI for innovation',  # Should be adoption
                'productivity increased by 75%',
                'employed 1000 workers',
                'cost savings of 25%',
                'investment of $30 billion',
                'research by Jones et al. (2023)'  # Citation
            ]
        }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            data_file = f.name
        pd.DataFrame(data).to_csv(data_file, index=False)
        
        # Create sources file
        sources_data = {
            'id': [1],
            'name': ['Test Source PDF']
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            sources_file = f.name
        pd.DataFrame(sources_data).to_csv(sources_file, index=False)
        
        yield data_file, sources_file
        
        # Cleanup
        os.remove(data_file)
        os.remove(sources_file)
        
    def test_initialization(self, test_data):
        """Test analyzer initialization"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        assert analyzer.source_id == 1
        assert analyzer.source_name == 'Test Source PDF'
        assert len(analyzer.source_df) == 10
        
    def test_identify_duplicates(self, test_data):
        """Test duplicate identification"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        analyzer.identify_duplicate_groups()
        
        # Should find the duplicate employment records
        assert len(analyzer.duplicate_groups) > 0
        assert (0.0, 'millions_usd', 2024) in analyzer.duplicate_groups
        
    def test_categorize_record_citation_year(self, test_data):
        """Test that citation years are detected"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        # Process the records
        analyzer.identify_duplicate_groups()
        for idx, row in analyzer.source_df.iterrows():
            analyzer.categorize_record(idx, row)
            
        # Check that citations were removed
        citation_removals = [r for r in analyzer.records_to_remove 
                           if 'Citation year' in r['reason']]
        assert len(citation_removals) >= 2  # Both 2024 and 2023 citations
        
    def test_categorize_record_unit_mismatch(self, test_data):
        """Test that unit mismatches are detected"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        # Process the records
        analyzer.identify_duplicate_groups()
        for idx, row in analyzer.source_df.iterrows():
            analyzer.categorize_record(idx, row)
            
        # Check that employment metric with financial unit was flagged
        unit_issues = [r for r in analyzer.records_to_remove 
                      if 'Financial units should not appear' in r.get('reason', '')]
        assert len(unit_issues) > 0
        
    def test_categorize_record_reclassification(self, test_data):
        """Test metric reclassification"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        # Process the records
        analyzer.identify_duplicate_groups()
        for idx, row in analyzer.source_df.iterrows():
            analyzer.categorize_record(idx, row)
            
        # Check that general_rate was reclassified
        reclassifications = [r for r in analyzer.records_to_modify 
                           if r['current_metric_type'] == 'general_rate']
        assert len(reclassifications) > 0
        assert reclassifications[0]['new_metric_type'] == 'adoption_metric'
        
    def test_sector_extraction(self, test_data):
        """Test enhanced sector extraction"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        # Test various contexts
        assert analyzer.extract_sector_enhanced('working in financial services') == 'financial services'
        assert analyzer.extract_sector_enhanced('healthcare industry report') == 'healthcare'
        assert analyzer.extract_sector_enhanced('manufacturing output increased') == 'manufacturing'
        assert analyzer.extract_sector_enhanced('no sector mentioned') == ''
        
    def test_summary_generation(self, test_data):
        """Test summary generation"""
        data_file, sources_file = test_data
        analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
        
        # Run minimal analysis
        analyzer.identify_duplicate_groups()
        for idx, row in analyzer.source_df.iterrows():
            analyzer.categorize_record(idx, row)
            
        summary = analyzer.generate_enhanced_summary()
        
        assert summary['source_id'] == 1
        assert summary['total_records'] == 10
        assert summary['duplicate_groups'] > 0
        assert 'quality_metrics' in summary
        assert 'confidence_distribution' in summary
        
    def test_defensive_checks(self, test_data):
        """Test defensive programming checks"""
        data_file, sources_file = test_data
        
        # Add a record with missing values
        df = pd.read_csv(data_file)
        df = pd.concat([df, pd.DataFrame({
            'source_id': [1],
            'value': [np.nan],
            'unit': ['percentage'],
            'year': [2024],
            'metric_type': ['unknown'],
            'context': ['missing value']
        })], ignore_index=True)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        df.to_csv(temp_file, index=False)
        
        analyzer = EnhancedSourceAnalyzer(1, temp_file, sources_file)
        
        # Process records
        for idx, row in analyzer.source_df.iterrows():
            analyzer.categorize_record(idx, row)
            
        # Check that incomplete record was removed
        incomplete_removals = [r for r in analyzer.records_to_remove 
                             if 'Incomplete record' in r['reason']]
        assert len(incomplete_removals) > 0
        
        # Cleanup
        os.remove(temp_file)


# Integration test
class TestIntegration:
    """Test the modules working together"""
    
    @pytest.fixture
    def test_data(self):
        """Create test dataset for integration test"""
        data = {
            'source_id': [1, 1, 1, 1, 1],
            'value': [100.0, 50.0, 75.0, 1000.0, 25.0],
            'unit': ['percentage', 'percentage', 'percentage', 'number', 'percentage'],
            'year': [2024, 2024, 2024, 2024, 2024],
            'metric_type': ['adoption_metric', 'general_rate', 'productivity_metric',
                           'employment_metric', 'cost_metric'],
            'context': [
                'AI adoption rate reached 100%',
                'companies using AI for innovation',
                'productivity increased by 75%',
                'employed 1000 workers',
                'cost savings of 25%'
            ]
        }
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            data_file = f.name
        pd.DataFrame(data).to_csv(data_file, index=False)
        
        # Create sources file
        sources_data = {
            'id': [1],
            'name': ['Test Source PDF']
        }
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            sources_file = f.name
        pd.DataFrame(sources_data).to_csv(sources_file, index=False)
        
        yield data_file, sources_file
        
        # Cleanup
        os.remove(data_file)
        os.remove(sources_file)
    
    def test_full_pipeline(self, test_data):
        """Test the complete analysis pipeline"""
        data_file, sources_file = test_data
        
        # Create temporary output directory
        output_dir = "Source Data Cleanup Analysis/Source_1"
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Run full analysis
            analyzer = EnhancedSourceAnalyzer(1, data_file, sources_file)
            analyzer.analyze()
            
            # Check outputs exist
            # Note: CSV files are only created if there are records in that category
            assert os.path.exists(f"{output_dir}/initial_analysis.csv")
            assert os.path.exists(f"{output_dir}/summary.json")
            assert os.path.exists(f"{output_dir}/summary.md")
            assert os.path.exists(f"{output_dir}/cleanup_summary.txt")
            
            # Check quality tracking
            assert os.path.exists("data_quality_tracking.csv")
            
            # Verify JSON summary
            with open(f"{output_dir}/summary.json", 'r') as f:
                summary = json.load(f)
            assert summary['source_id'] == 1
            assert 'quality_metrics' in summary
            
        finally:
            # Cleanup with retry for Windows file locks
            import shutil
            import time
            
            def remove_with_retry(path, is_dir=True):
                for i in range(3):
                    try:
                        if is_dir and os.path.exists(path):
                            shutil.rmtree(path)
                        elif not is_dir and os.path.exists(path):
                            os.remove(path)
                        break
                    except PermissionError:
                        if i < 2:
                            time.sleep(0.5)  # Wait before retry
                        else:
                            pass  # Ignore on final attempt
                            
            remove_with_retry("Source Data Cleanup Analysis", is_dir=True)
            remove_with_retry("data_quality_tracking.csv", is_dir=False)
            remove_with_retry("quality_reports", is_dir=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])