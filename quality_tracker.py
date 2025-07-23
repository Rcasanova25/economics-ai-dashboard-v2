"""
Data Quality Tracking Module
Tracks cleanup metrics over time to monitor data quality improvements
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class QualityTracker:
    """Track data quality metrics across cleanup runs"""
    
    def __init__(self, tracking_file: str = "data_quality_tracking.csv"):
        self.tracking_file = tracking_file
        self.current_run = {
            'timestamp': datetime.now().isoformat(),
            'sources': {}
        }
        
        # Define headers as class attribute for consistency
        self.headers = [
            'timestamp', 'source_id', 'source_name', 'total_records', 
            'kept_records', 'removed_records', 'modified_records',
            'removal_rate', 'modification_rate', 'quality_score',
            'top_removal_reason', 'top_removal_count',
            'duplicate_groups', 'duplicates_removed',
            'schema_version', 'notes'
        ]
        
        # Initialize tracking file if it doesn't exist
        if not os.path.exists(self.tracking_file):
            self._initialize_tracking_file()
    
    def _initialize_tracking_file(self):
        """Create the tracking CSV with headers"""
        with open(self.tracking_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
    
    def record_source_analysis(self, source_id: int, source_name: str, 
                             analysis_results: Dict):
        """Record the results of analyzing a single source"""
        total = analysis_results['total_records']
        kept = analysis_results['kept_records']
        removed = analysis_results['removed_records']
        modified = analysis_results['modified_records']
        
        # Calculate rates
        removal_rate = (removed / total * 100) if total > 0 else 0
        modification_rate = (modified / total * 100) if total > 0 else 0
        
        # Calculate quality score (higher is better)
        # Quality improves as we need fewer removals/modifications
        quality_score = 100 - (removal_rate + modification_rate / 2)
        quality_score = max(0, min(100, quality_score))  # Clamp to 0-100
        
        record = {
            'timestamp': self.current_run['timestamp'],
            'source_id': source_id,
            'source_name': source_name,
            'total_records': total,
            'kept_records': kept,
            'removed_records': removed,
            'modified_records': modified,
            'removal_rate': round(removal_rate, 2),
            'modification_rate': round(modification_rate, 2),
            'quality_score': round(quality_score, 2),
            'top_removal_reason': analysis_results.get('top_removal_reason', ''),
            'top_removal_count': analysis_results.get('top_removal_count', 0),
            'duplicate_groups': analysis_results.get('duplicate_groups', 0),
            'duplicates_removed': analysis_results.get('duplicates_removed', 0),
            'schema_version': analysis_results.get('schema_version', '1.0'),
            'notes': analysis_results.get('notes', '')
        }
        
        # Store in current run
        self.current_run['sources'][source_id] = record
        
        # Append to CSV
        with open(self.tracking_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow(record)
            
        return record
    
    def get_source_history(self, source_id: int) -> List[Dict]:
        """Get historical quality metrics for a specific source"""
        history = []
        
        if os.path.exists(self.tracking_file):
            df = pd.read_csv(self.tracking_file)
            source_df = df[df['source_id'] == source_id].sort_values('timestamp')
            history = source_df.to_dict('records')
            
        return history
    
    def get_quality_trends(self) -> Dict:
        """Analyze quality trends across all sources"""
        if not os.path.exists(self.tracking_file):
            return {'error': 'No tracking data available'}
            
        df = pd.read_csv(self.tracking_file)
        
        if df.empty:
            return {'error': 'No tracking data available'}
            
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Overall trends
        latest_run = df.groupby('source_id').last()
        
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
        
        # Find most problematic sources (lowest quality scores)
        problematic = latest_run.nsmallest(5, 'quality_score')[['source_name', 'quality_score']]
        trends['most_problematic_sources'] = [
            {'source': row['source_name'], 'quality_score': row['quality_score']}
            for _, row in problematic.iterrows()
        ]
        
        # Find most improved sources (compare first and last run)
        for source_id in df['source_id'].unique():
            source_history = df[df['source_id'] == source_id].sort_values('timestamp')
            if len(source_history) > 1:
                first_score = source_history.iloc[0]['quality_score']
                last_score = source_history.iloc[-1]['quality_score']
                improvement = last_score - first_score
                
                if improvement > 0:
                    trends['most_improved_sources'].append({
                        'source': source_history.iloc[-1]['source_name'],
                        'improvement': round(improvement, 2),
                        'current_score': round(last_score, 2)
                    })
        
        # Sort by improvement
        trends['most_improved_sources'].sort(key=lambda x: x['improvement'], reverse=True)
        trends['most_improved_sources'] = trends['most_improved_sources'][:5]
        
        return trends
    
    def export_run_summary(self, output_format: str = 'both') -> Dict[str, str]:
        """
        Export current run summary in JSON and/or Markdown format
        
        Args:
            output_format: 'json', 'markdown', or 'both'
            
        Returns:
            Dictionary with paths to exported files
        """
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
            'sources': self.current_run['sources']
        }
        
        # Export JSON
        if output_format in ['json', 'both']:
            json_path = f'quality_reports/run_summary_{timestamp}.json'
            os.makedirs('quality_reports', exist_ok=True)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2)
            exports['json'] = json_path
        
        # Export Markdown
        if output_format in ['markdown', 'both']:
            md_path = f'quality_reports/run_summary_{timestamp}.md'
            os.makedirs('quality_reports', exist_ok=True)
            
            md_content = self._generate_markdown_summary(summary)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            exports['markdown'] = md_path
            
        return exports
    
    def _generate_markdown_summary(self, summary: Dict) -> str:
        """Generate a markdown summary report"""
        md = f"""# Data Quality Analysis Run Summary

**Timestamp**: {summary['run_timestamp']}

## Overall Statistics

- **Sources Analyzed**: {summary['sources_analyzed']}
- **Total Records**: {summary['total_records']:,}
- **Records Kept**: {summary['total_kept']:,} ({summary['total_kept']/summary['total_records']*100:.1f}%)
- **Records Removed**: {summary['total_removed']:,} ({summary['total_removed']/summary['total_records']*100:.1f}%)
- **Records Modified**: {summary['total_modified']:,} ({summary['total_modified']/summary['total_records']*100:.1f}%)

## Source-by-Source Results

| Source | Total | Kept | Removed | Modified | Quality Score |
|--------|-------|------|---------|----------|---------------|
"""
        
        for source_id, data in summary['sources'].items():
            md += f"| {data['source_name'][:40]}... | {data['total_records']} | {data['kept_records']} | {data['removed_records']} | {data['modified_records']} | {data['quality_score']}% |\n"
            
        # Add trends if available
        trends = self.get_quality_trends()
        if 'error' not in trends:
            md += f"""
## Quality Trends

### Overall Metrics
- **Average Quality Score**: {trends['average_quality_score']}%
- **Average Removal Rate**: {trends['average_removal_rate']}%
- **Average Modification Rate**: {trends['average_modification_rate']}%

### Most Problematic Sources
"""
            for source in trends['most_problematic_sources']:
                md += f"- {source['source']}: {source['quality_score']}% quality\n"
                
            if trends['most_improved_sources']:
                md += "\n### Most Improved Sources\n"
                for source in trends['most_improved_sources']:
                    md += f"- {source['source']}: +{source['improvement']}% improvement (now {source['current_score']}%)\n"
                    
        return md
    
    def generate_quality_dashboard(self) -> str:
        """Generate an HTML dashboard for quality metrics"""
        # This could be expanded to create interactive charts
        # For now, we'll create a simple HTML summary
        pass  # Implementation left for future enhancement