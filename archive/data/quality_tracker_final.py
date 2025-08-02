"""
Final Quality Tracking Module - Using pandas for consistency
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class QualityTrackerFinal:
    """Quality tracker using pandas for all CSV operations"""
    
    def __init__(self, tracking_file: str = "data_quality_tracking.csv"):
        self.tracking_file = tracking_file
        self.current_run_timestamp = datetime.now().isoformat()
        self.current_run_sources = {}
        
        # Define schema
        self.columns = [
            'timestamp', 'source_id', 'source_name', 'total_records', 
            'kept_records', 'removed_records', 'modified_records',
            'removal_rate', 'modification_rate', 'quality_score',
            'top_removal_reason', 'top_removal_count',
            'duplicate_groups', 'duplicates_removed',
            'schema_version', 'notes'
        ]
        
        # Initialize empty DataFrame if file doesn't exist
        if not os.path.exists(self.tracking_file):
            empty_df = pd.DataFrame(columns=self.columns)
            empty_df.to_csv(self.tracking_file, index=False)
            
    def record_source_analysis(self, source_id: int, source_name: str, 
                             analysis_results: Dict) -> Dict:
        """Record the results of analyzing a single source"""
        # Calculate metrics
        total = analysis_results.get('total_records', 0)
        kept = analysis_results.get('kept_records', 0)
        removed = analysis_results.get('removed_records', 0)
        modified = analysis_results.get('modified_records', 0)
        
        removal_rate = (removed / total * 100) if total > 0 else 0
        modification_rate = (modified / total * 100) if total > 0 else 0
        quality_score = 100 - (removal_rate + modification_rate / 2)
        quality_score = max(0, min(100, quality_score))
        
        # Create record
        record = {
            'timestamp': self.current_run_timestamp,
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
        self.current_run_sources[source_id] = record
        
        # Read existing data
        existing_df = pd.read_csv(self.tracking_file)
        
        # Append new record
        new_df = pd.concat([existing_df, pd.DataFrame([record])], ignore_index=True)
        
        # Write back
        new_df.to_csv(self.tracking_file, index=False)
        
        return record
        
    def get_source_history(self, source_id: int) -> List[Dict]:
        """Get historical quality metrics for a specific source"""
        if not os.path.exists(self.tracking_file):
            return []
            
        df = pd.read_csv(self.tracking_file)
        
        if df.empty:
            return []
            
        # Filter by source_id and sort by timestamp
        source_df = df[df['source_id'] == source_id].sort_values('timestamp')
        return source_df.to_dict('records')
        
    def get_all_records(self) -> pd.DataFrame:
        """Get all tracking records as a DataFrame"""
        if not os.path.exists(self.tracking_file):
            return pd.DataFrame(columns=self.columns)
            
        return pd.read_csv(self.tracking_file)
        
    def get_quality_trends(self) -> Dict:
        """Analyze quality trends across all sources"""
        df = self.get_all_records()
        
        if df.empty:
            return {'error': 'No tracking data available'}
            
        # Convert timestamp to datetime for proper sorting
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get latest record for each source
        latest_per_source = df.sort_values('timestamp').groupby('source_id').last()
        
        if latest_per_source.empty:
            return {'error': 'No tracking data available'}
            
        trends = {
            'total_sources_analyzed': len(latest_per_source),
            'average_quality_score': round(latest_per_source['quality_score'].mean(), 2),
            'average_removal_rate': round(latest_per_source['removal_rate'].mean(), 2),
            'average_modification_rate': round(latest_per_source['modification_rate'].mean(), 2),
            'total_records_processed': int(latest_per_source['total_records'].sum()),
            'total_records_removed': int(latest_per_source['removed_records'].sum()),
            'total_records_modified': int(latest_per_source['modified_records'].sum()),
            'most_problematic_sources': [],
            'most_improved_sources': []
        }
        
        # Find most problematic sources (lowest quality)
        if len(latest_per_source) > 0:
            problematic = latest_per_source.nsmallest(
                min(5, len(latest_per_source)), 'quality_score'
            )
            trends['most_problematic_sources'] = [
                {
                    'source_id': int(idx),
                    'source_name': row['source_name'],
                    'quality_score': row['quality_score']
                }
                for idx, row in problematic.iterrows()
            ]
            
        # Find most improved sources
        improvements = []
        for source_id in df['source_id'].unique():
            source_history = df[df['source_id'] == source_id].sort_values('timestamp')
            if len(source_history) > 1:
                first = source_history.iloc[0]
                last = source_history.iloc[-1]
                improvement = last['quality_score'] - first['quality_score']
                
                if improvement > 0:
                    improvements.append({
                        'source_id': int(source_id),
                        'source_name': last['source_name'],
                        'improvement': round(improvement, 2),
                        'current_score': round(last['quality_score'], 2)
                    })
                    
        improvements.sort(key=lambda x: x['improvement'], reverse=True)
        trends['most_improved_sources'] = improvements[:5]
        
        return trends
        
    def export_run_summary(self, output_format: str = 'both') -> Dict[str, str]:
        """Export current run summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exports = {}
        
        if not self.current_run_sources:
            return {'error': 'No data to export'}
            
        # Calculate summary statistics
        total_records = sum(s['total_records'] for s in self.current_run_sources.values())
        total_kept = sum(s['kept_records'] for s in self.current_run_sources.values())
        total_removed = sum(s['removed_records'] for s in self.current_run_sources.values())
        total_modified = sum(s['modified_records'] for s in self.current_run_sources.values())
        avg_quality = sum(s['quality_score'] for s in self.current_run_sources.values()) / len(self.current_run_sources)
        
        summary = {
            'run_timestamp': self.current_run_timestamp,
            'sources_analyzed': len(self.current_run_sources),
            'total_records': total_records,
            'total_kept': total_kept,
            'total_removed': total_removed,
            'total_modified': total_modified,
            'average_quality_score': round(avg_quality, 2),
            'sources': self.current_run_sources
        }
        
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
            
            md_content = f"""# Data Quality Analysis Run Summary

**Timestamp**: {summary['run_timestamp']}  
**Sources Analyzed**: {summary['sources_analyzed']}

## Overall Statistics

- **Total Records**: {summary['total_records']:,}
- **Records Kept**: {summary['total_kept']:,} ({summary['total_kept']/summary['total_records']*100:.1f}%)
- **Records Removed**: {summary['total_removed']:,} ({summary['total_removed']/summary['total_records']*100:.1f}%)
- **Records Modified**: {summary['total_modified']:,} ({summary['total_modified']/summary['total_records']*100:.1f}%)
- **Average Quality Score**: {summary['average_quality_score']}%

## Source Details

| Source | Total | Kept | Removed | Modified | Quality |
|--------|-------|------|---------|----------|---------|
"""
            
            for source_id, data in summary['sources'].items():
                md_content += f"| {data['source_name']} | {data['total_records']} | "
                md_content += f"{data['kept_records']} | {data['removed_records']} | "
                md_content += f"{data['modified_records']} | {data['quality_score']}% |\n"
                
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            exports['markdown'] = md_path
            
        return exports