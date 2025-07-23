"""
Enhanced Data Quality Tracking Module
Properly handles CSV operations with consistent schema
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from dataclasses import dataclass, asdict


@dataclass
class QualityRecord:
    """Data class to ensure consistent structure for quality records"""
    timestamp: str
    source_id: int
    source_name: str
    total_records: int
    kept_records: int
    removed_records: int
    modified_records: int
    removal_rate: float
    modification_rate: float
    quality_score: float
    top_removal_reason: str
    top_removal_count: int
    duplicate_groups: int
    duplicates_removed: int
    schema_version: str
    notes: str = ""
    
    @classmethod
    def from_analysis(cls, source_id: int, source_name: str, 
                     analysis_results: Dict, timestamp: str = None):
        """Create a QualityRecord from analysis results"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        total = analysis_results['total_records']
        kept = analysis_results['kept_records']
        removed = analysis_results['removed_records']
        modified = analysis_results['modified_records']
        
        # Calculate rates
        removal_rate = (removed / total * 100) if total > 0 else 0
        modification_rate = (modified / total * 100) if total > 0 else 0
        
        # Calculate quality score
        quality_score = 100 - (removal_rate + modification_rate / 2)
        quality_score = max(0, min(100, quality_score))
        
        return cls(
            timestamp=timestamp,
            source_id=source_id,
            source_name=source_name,
            total_records=total,
            kept_records=kept,
            removed_records=removed,
            modified_records=modified,
            removal_rate=round(removal_rate, 2),
            modification_rate=round(modification_rate, 2),
            quality_score=round(quality_score, 2),
            top_removal_reason=analysis_results.get('top_removal_reason', ''),
            top_removal_count=analysis_results.get('top_removal_count', 0),
            duplicate_groups=analysis_results.get('duplicate_groups', 0),
            duplicates_removed=analysis_results.get('duplicates_removed', 0),
            schema_version=analysis_results.get('schema_version', '1.0'),
            notes=analysis_results.get('notes', '')
        )


class QualityTrackerV2:
    """Enhanced quality tracker with proper data handling"""
    
    def __init__(self, tracking_file: str = "data_quality_tracking.csv"):
        self.tracking_file = tracking_file
        self.current_run = {
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # Use dataclass fields to ensure consistency
        self.fieldnames = list(QualityRecord.__dataclass_fields__.keys())
        
        # Initialize file if needed
        self._ensure_file_exists()
        
    def _ensure_file_exists(self):
        """Ensure tracking file exists with proper headers"""
        if not os.path.exists(self.tracking_file):
            # Create with headers
            with open(self.tracking_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                
    def record_source_analysis(self, source_id: int, source_name: str, 
                             analysis_results: Dict) -> Dict:
        """Record analysis results using structured data"""
        # Create structured record
        record = QualityRecord.from_analysis(
            source_id, source_name, analysis_results, 
            self.current_run['timestamp']
        )
        
        # Convert to dict for storage and CSV
        record_dict = asdict(record)
        
        # Store in current run
        self.current_run['sources'][source_id] = record_dict
        
        # Append to CSV
        with open(self.tracking_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(record_dict)
            
        return record_dict
        
    def get_source_history(self, source_id: int) -> List[Dict]:
        """Get historical quality metrics for a specific source"""
        if not os.path.exists(self.tracking_file):
            return []
            
        try:
            # Read CSV with proper handling
            df = pd.read_csv(self.tracking_file)
            
            # Handle empty dataframe
            if df.empty:
                return []
                
            # Filter by source_id
            source_df = df[df['source_id'] == source_id].sort_values('timestamp')
            return source_df.to_dict('records')
            
        except pd.errors.EmptyDataError:
            # File has only headers, no data
            return []
        except Exception as e:
            print(f"Error reading tracking file: {e}")
            return []
            
    def get_all_records(self) -> pd.DataFrame:
        """Get all tracking records as a DataFrame"""
        if not os.path.exists(self.tracking_file):
            return pd.DataFrame(columns=self.fieldnames)
            
        try:
            df = pd.read_csv(self.tracking_file)
            return df
        except pd.errors.EmptyDataError:
            # Return empty dataframe with proper columns
            return pd.DataFrame(columns=self.fieldnames)
            
    def get_quality_trends(self) -> Dict:
        """Analyze quality trends across all sources"""
        df = self.get_all_records()
        
        if df.empty:
            return {'error': 'No tracking data available'}
            
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Overall trends
        latest_run = df.groupby('source_id').last()
        
        if latest_run.empty:
            return {'error': 'No tracking data available'}
            
        trends = {
            'total_sources_analyzed': len(latest_run),
            'average_quality_score': round(latest_run['quality_score'].mean(), 2),
            'average_removal_rate': round(latest_run['removal_rate'].mean(), 2),
            'average_modification_rate': round(latest_run['modification_rate'].mean(), 2),
            'total_records_processed': int(latest_run['total_records'].sum()),
            'total_records_removed': int(latest_run['removed_records'].sum()),
            'total_records_modified': int(latest_run['modified_records'].sum()),
            'most_problematic_sources': [],
            'most_improved_sources': []
        }
        
        # Find most problematic sources
        if len(latest_run) > 0:
            problematic = latest_run.nsmallest(min(5, len(latest_run)), 'quality_score')
            trends['most_problematic_sources'] = [
                {
                    'source_id': int(idx),
                    'source': row['source_name'], 
                    'quality_score': row['quality_score']
                }
                for idx, row in problematic.iterrows()
            ]
        
        # Find most improved sources
        improvements = []
        for source_id in df['source_id'].unique():
            source_history = df[df['source_id'] == source_id].sort_values('timestamp')
            if len(source_history) > 1:
                first_score = source_history.iloc[0]['quality_score']
                last_score = source_history.iloc[-1]['quality_score']
                improvement = last_score - first_score
                
                if improvement > 0:
                    improvements.append({
                        'source_id': int(source_id),
                        'source': source_history.iloc[-1]['source_name'],
                        'improvement': round(improvement, 2),
                        'current_score': round(last_score, 2)
                    })
        
        # Sort and take top 5
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        trends['most_improved_sources'] = improvements[:5]
        
        return trends
        
    def export_run_summary(self, output_format: str = 'both') -> Dict[str, str]:
        """Export current run summary in JSON and/or Markdown format"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exports = {}
        
        # Prepare summary data
        summary = {
            'run_timestamp': self.current_run['timestamp'],
            'sources_analyzed': len(self.current_run['sources']),
            'total_records': sum(s['total_records'] for s in self.current_run['sources'].values()),
            'total_kept': sum(s['kept_records'] for s in self.current_run['sources'].values()),
            'total_removed': sum(s['removed_records'] for s in self.current_run['sources'].values()),
            'total_modified': sum(s['modified_records'] for s in self.current_run['sources'].values()),
            'average_quality_score': round(
                sum(s['quality_score'] for s in self.current_run['sources'].values()) / 
                len(self.current_run['sources']) if self.current_run['sources'] else 0, 2
            ),
            'sources': self.current_run['sources']
        }
        
        # Create output directory
        os.makedirs('quality_reports', exist_ok=True)
        
        # Export JSON
        if output_format in ['json', 'both']:
            json_path = f'quality_reports/run_summary_{timestamp}.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            exports['json'] = json_path
        
        # Export Markdown
        if output_format in ['markdown', 'both']:
            md_path = f'quality_reports/run_summary_{timestamp}.md'
            md_content = self._generate_markdown_summary(summary)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            exports['markdown'] = md_path
            
        return exports
        
    def _generate_markdown_summary(self, summary: Dict) -> str:
        """Generate a markdown summary report"""
        md = f"""# Data Quality Analysis Run Summary

**Timestamp**: {summary['run_timestamp']}  
**Sources Analyzed**: {summary['sources_analyzed']}

## Overall Statistics

| Metric | Value |
|--------|-------|
| Total Records | {summary['total_records']:,} |
| Records Kept | {summary['total_kept']:,} ({(summary['total_kept']/summary['total_records']*100 if summary['total_records'] > 0 else 0):.1f}%) |
| Records Removed | {summary['total_removed']:,} ({(summary['total_removed']/summary['total_records']*100 if summary['total_records'] > 0 else 0):.1f}%) |
| Records Modified | {summary['total_modified']:,} ({(summary['total_modified']/summary['total_records']*100 if summary['total_records'] > 0 else 0):.1f}%) |
| Average Quality Score | {summary['average_quality_score']}% |

## Source-by-Source Results

| Source | Total | Kept | Removed | Modified | Quality Score |
|--------|-------|------|---------|----------|---------------|
"""
        
        for source_id, data in summary['sources'].items():
            name = data['source_name'][:40] + '...' if len(data['source_name']) > 40 else data['source_name']
            md += f"| {name} | {data['total_records']} | {data['kept_records']} | "
            md += f"{data['removed_records']} | {data['modified_records']} | {data['quality_score']}% |\n"
            
        # Add trends if available
        trends = self.get_quality_trends()
        if 'error' not in trends:
            md += f"""
## Historical Trends

### Overall Metrics
- **Total Sources Analyzed**: {trends['total_sources_analyzed']}
- **Average Quality Score**: {trends['average_quality_score']}%
- **Average Removal Rate**: {trends['average_removal_rate']}%
- **Average Modification Rate**: {trends['average_modification_rate']}%
"""
            
            if trends['most_problematic_sources']:
                md += "\n### Most Problematic Sources\n"
                for source in trends['most_problematic_sources'][:5]:
                    md += f"- {source['source']} (ID: {source['source_id']}): {source['quality_score']}% quality\n"
                    
            if trends['most_improved_sources']:
                md += "\n### Most Improved Sources\n"
                for source in trends['most_improved_sources'][:5]:
                    md += f"- {source['source']} (ID: {source['source_id']}): "
                    md += f"+{source['improvement']}% improvement (now {source['current_score']}%)\n"
                    
        return md