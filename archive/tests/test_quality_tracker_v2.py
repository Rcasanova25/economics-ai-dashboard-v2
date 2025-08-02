"""
Comprehensive tests for the enhanced QualityTrackerV2
"""

import pytest
import pandas as pd
import os
import csv
import json
import tempfile
from datetime import datetime

from quality_tracker_v2 import QualityTrackerV2, QualityRecord


class TestQualityRecord:
    """Test the QualityRecord dataclass"""
    
    def test_quality_record_creation(self):
        """Test creating a QualityRecord from analysis results"""
        analysis_results = {
            'total_records': 100,
            'kept_records': 70,
            'removed_records': 20,
            'modified_records': 10,
            'duplicate_groups': 5,
            'duplicates_removed': 15,
            'top_removal_reason': 'Duplicates',
            'top_removal_count': 15,
            'schema_version': '1.1'
        }
        
        record = QualityRecord.from_analysis(1, 'Test Source', analysis_results)
        
        assert record.source_id == 1
        assert record.source_name == 'Test Source'
        assert record.total_records == 100
        assert record.kept_records == 70
        assert record.removed_records == 20
        assert record.modified_records == 10
        assert record.removal_rate == 20.0
        assert record.modification_rate == 10.0
        assert record.quality_score == 75.0  # 100 - 20 - 10/2
        
    def test_quality_score_calculation(self):
        """Test various quality score calculations"""
        # Perfect quality
        results = {
            'total_records': 100,
            'kept_records': 100,
            'removed_records': 0,
            'modified_records': 0
        }
        record = QualityRecord.from_analysis(1, 'Test', results)
        assert record.quality_score == 100.0
        
        # All removed
        results['kept_records'] = 0
        results['removed_records'] = 100
        record = QualityRecord.from_analysis(1, 'Test', results)
        assert record.quality_score == 0.0
        
        # Mixed
        results = {
            'total_records': 100,
            'kept_records': 50,
            'removed_records': 30,
            'modified_records': 20
        }
        record = QualityRecord.from_analysis(1, 'Test', results)
        assert record.quality_score == 60.0  # 100 - 30 - 20/2


class TestQualityTrackerV2:
    """Test the enhanced QualityTrackerV2"""
    
    @pytest.fixture
    def tracker(self):
        """Create a tracker with temporary file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_file = f.name
        tracker = QualityTrackerV2(tracking_file=temp_file)
        yield tracker
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    def test_file_initialization(self, tracker):
        """Test that tracking file is created with headers"""
        assert os.path.exists(tracker.tracking_file)
        
        # Read and verify headers
        with open(tracker.tracking_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
        expected_headers = [
            'timestamp', 'source_id', 'source_name', 'total_records',
            'kept_records', 'removed_records', 'modified_records',
            'removal_rate', 'modification_rate', 'quality_score'
        ]
        
        for header in expected_headers:
            assert header in headers
            
    def test_record_source_analysis(self, tracker):
        """Test recording a source analysis"""
        analysis_results = {
            'total_records': 100,
            'kept_records': 70,
            'removed_records': 20,
            'modified_records': 10,
            'duplicate_groups': 5,
            'duplicates_removed': 15,
            'top_removal_reason': 'Duplicates',
            'top_removal_count': 15,
            'schema_version': '1.1'
        }
        
        record = tracker.record_source_analysis(1, 'Test Source', analysis_results)
        
        # Verify record structure
        assert record['source_id'] == 1
        assert record['source_name'] == 'Test Source'
        assert record['quality_score'] == 75.0
        
        # Verify it was written to file
        df = pd.read_csv(tracker.tracking_file)
        assert len(df) == 1
        assert df.iloc[0]['source_id'] == 1
        
    def test_get_source_history_empty(self, tracker):
        """Test getting history for source with no data"""
        history = tracker.get_source_history(1)
        assert history == []
        
    def test_get_source_history_with_data(self, tracker):
        """Test getting history for source with multiple records"""
        # Add multiple records
        for i in range(3):
            analysis_results = {
                'total_records': 100,
                'kept_records': 70 + i*5,  # Improving over time
                'removed_records': 20 - i*3,
                'modified_records': 10 - i*2,
                'duplicate_groups': 5,
                'duplicates_removed': 15 - i*5,
                'top_removal_reason': 'Duplicates',
                'top_removal_count': 15 - i*5,
                'schema_version': '1.1'
            }
            tracker.record_source_analysis(1, 'Test Source', analysis_results)
            
        history = tracker.get_source_history(1)
        
        assert len(history) == 3
        # Verify records are sorted by timestamp
        timestamps = [h['timestamp'] for h in history]
        assert timestamps == sorted(timestamps)
        
        # Verify quality improves over time
        quality_scores = [h['quality_score'] for h in history]
        assert quality_scores[0] < quality_scores[-1]
        
    def test_get_all_records(self, tracker):
        """Test getting all records as DataFrame"""
        # Empty case
        df = tracker.get_all_records()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert 'source_id' in df.columns
        
        # With data
        tracker.record_source_analysis(1, 'Source 1', {
            'total_records': 100, 'kept_records': 80,
            'removed_records': 15, 'modified_records': 5
        })
        tracker.record_source_analysis(2, 'Source 2', {
            'total_records': 200, 'kept_records': 150,
            'removed_records': 30, 'modified_records': 20
        })
        
        df = tracker.get_all_records()
        assert len(df) == 2
        assert set(df['source_id'].values) == {1, 2}
        
    def test_get_quality_trends(self, tracker):
        """Test quality trend analysis"""
        # Add data for multiple sources
        sources_data = [
            (1, 'Source 1', {'total_records': 100, 'kept_records': 80, 
                           'removed_records': 15, 'modified_records': 5}),
            (2, 'Source 2', {'total_records': 200, 'kept_records': 100,
                           'removed_records': 80, 'modified_records': 20}),
            (3, 'Source 3', {'total_records': 150, 'kept_records': 140,
                           'removed_records': 5, 'modified_records': 5})
        ]
        
        for source_id, name, data in sources_data:
            tracker.record_source_analysis(source_id, name, data)
            
        trends = tracker.get_quality_trends()
        
        assert 'error' not in trends
        assert trends['total_sources_analyzed'] == 3
        assert trends['total_records_processed'] == 450
        assert len(trends['most_problematic_sources']) > 0
        
        # Source 2 should be most problematic (lowest quality)
        most_problematic = trends['most_problematic_sources'][0]
        assert most_problematic['source_id'] == 2
        
    def test_export_run_summary(self, tracker):
        """Test exporting run summary"""
        # Add test data
        tracker.record_source_analysis(1, 'Test Source', {
            'total_records': 100, 'kept_records': 80,
            'removed_records': 15, 'modified_records': 5
        })
        
        # Export JSON
        exports = tracker.export_run_summary('json')
        assert 'json' in exports
        assert os.path.exists(exports['json'])
        
        # Verify JSON content
        with open(exports['json'], 'r') as f:
            summary = json.load(f)
            
        assert summary['sources_analyzed'] == 1
        assert summary['total_records'] == 100
        assert summary['average_quality_score'] == 82.5
        
        # Cleanup
        os.remove(exports['json'])
        os.rmdir('quality_reports')
        
    def test_edge_cases(self, tracker):
        """Test edge cases and error handling"""
        # Zero total records
        record = tracker.record_source_analysis(1, 'Empty', {
            'total_records': 0, 'kept_records': 0,
            'removed_records': 0, 'modified_records': 0
        })
        assert record['removal_rate'] == 0
        assert record['quality_score'] == 100  # No issues = perfect quality
        
        # Missing optional fields
        record = tracker.record_source_analysis(2, 'Minimal', {
            'total_records': 10, 'kept_records': 10,
            'removed_records': 0, 'modified_records': 0
        })
        assert record['top_removal_reason'] == ''
        assert record['duplicate_groups'] == 0
        
    def test_concurrent_operations(self, tracker):
        """Test that multiple sources can be tracked in same run"""
        # Record multiple sources
        for i in range(5):
            tracker.record_source_analysis(i, f'Source {i}', {
                'total_records': 100, 'kept_records': 90 - i*10,
                'removed_records': 5 + i*5, 'modified_records': 5 + i*5
            })
            
        # All should be in current run
        assert len(tracker.current_run['sources']) == 5
        
        # All should be in file
        df = tracker.get_all_records()
        assert len(df) == 5
        
        # All should have same timestamp
        assert len(df['timestamp'].unique()) == 1


class TestIntegrationWithEnhancedAnalyzer:
    """Test integration with the main analyzer"""
    
    def test_analyzer_tracker_integration(self):
        """Test that analyzer properly uses the tracker"""
        # This would test the actual integration
        # For now, we'll test the interface compatibility
        
        tracker = QualityTrackerV2("test_integration.csv")
        
        # Simulate what the analyzer would do
        analysis_results = {
            'total_records': 1000,
            'kept_records': 800,
            'removed_records': 150,
            'modified_records': 50,
            'duplicate_groups': 25,
            'duplicates_removed': 100,
            'top_removal_reason': 'Citation years',
            'top_removal_count': 75,
            'schema_version': '1.1'
        }
        
        record = tracker.record_source_analysis(
            10, 'Integration Test Source', analysis_results
        )
        
        # Verify the record is properly structured
        assert all(key in record for key in [
            'timestamp', 'source_id', 'source_name', 'quality_score'
        ])
        
        # Cleanup
        os.remove("test_integration.csv")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])