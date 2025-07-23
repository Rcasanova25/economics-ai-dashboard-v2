"""
Enhanced Source Cleanup Analysis with Modular Architecture
Clean, maintainable, and reusable across projects
"""

import pandas as pd
import numpy as np
import re
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

from metric_validator import MetricValidator
from quality_tracker import QualityTracker


class EnhancedSourceAnalyzer:
    def __init__(self, source_id: int, previous_cleaned_file: str = 'ai_metrics.csv',
                 data_sources_file: str = 'data/exports/data_sources_20250719.csv'):
        """
        Initialize analyzer with modular components
        
        Args:
            source_id: The ID of the source to analyze
            previous_cleaned_file: The CSV file with previously cleaned data
            data_sources_file: Path to the data sources metadata file
        """
        # Initialize components
        self.validator = MetricValidator()
        self.quality_tracker = QualityTracker()
        
        # Load data
        self.source_id = source_id
        self.df = pd.read_csv(previous_cleaned_file)
        self.source_df = self.df[self.df['source_id'] == source_id].copy()
        
        # Get source metadata
        try:
            sources_df = pd.read_csv(data_sources_file)
            self.source_name = sources_df[sources_df['id'] == source_id]['name'].values[0]
        except:
            self.source_name = f"Source_{source_id}"
            
        # Initialize tracking
        self.records_to_keep = []
        self.records_to_remove = []
        self.records_to_modify = []
        self.duplicate_groups = {}
        
        # Statistics for quality tracking
        self.removal_reasons = {}
        self.modification_types = {}
        
    def analyze(self):
        """Run complete analysis with quality tracking"""
        print("=" * 80)
        print(f"SOURCE {self.source_id} ENHANCED CLEANUP ANALYSIS")
        print(f"File: {self.source_name}")
        print(f"Schema Version: 1.1")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_df)}")
        
        if len(self.source_df) == 0:
            print("No records found for this source.")
            return
            
        # Analysis phases
        self.print_initial_analysis()
        self.identify_duplicate_groups()
        
        # Process records
        for idx, row in self.source_df.iterrows():
            self.categorize_record(idx, row)
            
        # Generate outputs
        self.generate_csv_reports()
        summary_data = self.generate_enhanced_summary()
        
        # Track quality metrics
        self._track_quality_metrics()
        
        # Export summary in multiple formats
        self.export_summary(summary_data)
        
    def print_initial_analysis(self):
        """Print initial data analysis with insights"""
        print("\nINITIAL DATA ANALYSIS:")
        print("-" * 40)
        
        # Metric type distribution
        print("\nMetric Type Distribution:")
        metric_dist = self.source_df['metric_type'].value_counts()
        for metric, count in metric_dist.head(10).items():
            pct = count/len(self.source_df)*100
            print(f"  {metric}: {count} ({pct:.1f}%)")
            
        # Unit distribution with warnings
        print("\nUnit Distribution:")
        unit_dist = self.source_df['unit'].value_counts()
        problem_units = ['energy_unit', 'unknown', 'multiple', 'co2_emissions']
        
        for unit, count in unit_dist.head(10).items():
            warning = " ⚠️ PROBLEMATIC" if unit in problem_units else ""
            print(f"  {unit}: {count}{warning}")
            
        # Year distribution
        print("\nYear Distribution:")
        year_dist = self.source_df['year'].value_counts().sort_index()
        if len(year_dist) > 0:
            print(f"  Range: {year_dist.index.min()} - {year_dist.index.max()}")
            
        # Value patterns
        print("\nValue Analysis:")
        zero_count = (self.source_df['value'] == 0).sum()
        print(f"  Zero values: {zero_count} ({zero_count/len(self.source_df)*100:.1f}%)")
        
        # Potential citation years
        potential_citations = self.source_df[
            (self.source_df['value'] >= 1900) & 
            (self.source_df['value'] <= 2030) &
            (self.source_df['value'] == self.source_df['year'])
        ]
        if len(potential_citations) > 0:
            print(f"  ⚠️  Potential citation years: {len(potential_citations)} records")
            
    def identify_duplicate_groups(self):
        """Identify duplicate groups with enhanced reporting"""
        self.duplicate_groups = {}
        
        # Group by value/unit/year
        grouped = self.source_df.groupby(['value', 'unit', 'year'])
        
        for (value, unit, year), group in grouped:
            if len(group) > 1:
                sorted_group = group.sort_index()
                self.duplicate_groups[(value, unit, year)] = {
                    'first': sorted_group.index[0],
                    'duplicates': sorted_group.index[1:].tolist(),
                    'count': len(group)
                }
                
        print(f"\nDuplicate Analysis:")
        print(f"  Duplicate groups found: {len(self.duplicate_groups)}")
        print(f"  Total duplicate records: {sum(d['count']-1 for d in self.duplicate_groups.values())}")
        
        if self.duplicate_groups and len(self.duplicate_groups) <= 5:
            print("  Examples:")
            for key, info in list(self.duplicate_groups.items())[:3]:
                print(f"    {key}: {info['count']} occurrences")
                
    def categorize_record(self, idx: int, row: pd.Series):
        """Categorize record with defensive checks and validation"""
        # Defensive checks
        if pd.isna(row['value']) or pd.isna(row['unit']) or pd.isna(row['year']):
            self.records_to_remove.append({
                'original_id': idx,
                'value': row.get('value', np.nan),
                'unit': row.get('unit', ''),
                'year': row.get('year', np.nan),
                'metric_type': row.get('metric_type', ''),
                'context_preview': 'Missing required fields',
                'reason': 'Incomplete record - missing value, unit, or year',
                'confidence': 1.0
            })
            self._track_removal_reason('Incomplete record')
            return
            
        # Extract and clean values
        context = str(row.get('context', '')).lower()
        value = float(row['value'])
        unit = str(row['unit'])
        metric_type = str(row['metric_type'])
        year = int(row['year'])
        
        # Check for citation years first
        if self.validator.detect_citation_year(value, year, context):
            self.records_to_remove.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'reason': 'Citation year extracted as metric value',
                'confidence': 0.95
            })
            self._track_removal_reason('Citation year extracted as metric value')
            return
            
        # Check for duplicates
        dup_key = (value, unit, year)
        if dup_key in self.duplicate_groups:
            dup_info = self.duplicate_groups[dup_key]
            if idx in dup_info['duplicates']:
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Duplicate record (keeping first occurrence)',
                    'confidence': 0.90
                })
                self._track_removal_reason('Duplicate record')
                return
                
        # Apply cross-metric validation rules
        cross_issues = self.validator.apply_cross_metric_rules(metric_type, value, unit, year, context)
        if cross_issues:
            highest_issue = max(cross_issues, key=lambda x: x['confidence'])
            if highest_issue.get('action') == 'remove':
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': highest_issue['reason'],
                    'confidence': highest_issue['confidence']
                })
                self._track_removal_reason(highest_issue['reason'])
                return
                
        # Schema validation
        schema_issues = self.validator.validate_against_schema(metric_type, value, unit, context)
        if schema_issues:
            highest_issue = max(schema_issues, key=lambda x: x['confidence'])
            if highest_issue['confidence'] >= 0.85:  # High confidence issues
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': highest_issue['reason'],
                    'confidence': highest_issue['confidence']
                })
                self._track_removal_reason(highest_issue['reason'])
                return
                
        # Check for vague classifications
        if metric_type in ['general_rate', 'general_metric', 'unknown_metric']:
            new_type = self.validator.classify_metric_type(context, value, unit, metric_type)
            if new_type != metric_type:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': new_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector_enhanced(context),
                    'country': '',
                    'company_size': '',
                    'reason': f'Reclassify: {metric_type} → {new_type}',
                    'confidence': 0.80
                })
                self._track_modification_type(f'{metric_type} → {new_type}')
                return
                
        # Record passes all checks
        self.records_to_keep.append({
            'original_id': idx,
            'value': value,
            'unit': unit,
            'year': year,
            'metric_type': metric_type,
            'context_preview': context[:100] + '...' if len(context) > 100 else context,
            'reason': 'Passed all validation checks',
            'confidence': 0.85
        })
        
    def extract_sector_enhanced(self, context: str) -> str:
        """Enhanced sector extraction with regex patterns"""
        # Define sector patterns with regex for better matching
        sector_patterns = {
            'financial services': r'\b(?:financ|bank|insurance|fintech|investment|asset\s+manag)',
            'healthcare': r'\b(?:health|medic|pharma|clinical|hospital|patient|therap)',
            'retail': r'\b(?:retail|e-commerce|shopping|consumer\s+goods|store|merchandise)',
            'manufacturing': r'\b(?:manufactur|industrial|production|factory|assembly)',
            'technology': r'\b(?:tech|software|IT|digital|cyber|cloud|data\s+center)',
            'education': r'\b(?:educat|academic|university|school|learn|train|student)',
            'government': r'\b(?:government|public\s+sector|federal|municipal|state\s+agency)',
            'energy': r'\b(?:energy|utility|power|renewable|oil|gas|electric)',
            'transportation': r'\b(?:transport|logistics|shipping|delivery|airline|automotive)'
        }
        
        context_lower = context.lower()
        
        for sector, pattern in sector_patterns.items():
            if re.search(pattern, context_lower):
                return sector
                
        return ''
        
    def _track_removal_reason(self, reason: str):
        """Track removal reasons for reporting"""
        self.removal_reasons[reason] = self.removal_reasons.get(reason, 0) + 1
        
    def _track_modification_type(self, mod_type: str):
        """Track modification types for reporting"""
        self.modification_types[mod_type] = self.modification_types.get(mod_type, 0) + 1
        
    def generate_csv_reports(self):
        """Generate CSV output files"""
        output_dir = f"Source Data Cleanup Analysis/Source_{self.source_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each category
        if self.records_to_keep:
            pd.DataFrame(self.records_to_keep).to_csv(
                f"{output_dir}/records_to_keep.csv", index=False
            )
            
        if self.records_to_remove:
            pd.DataFrame(self.records_to_remove).to_csv(
                f"{output_dir}/records_to_remove.csv", index=False
            )
            
        if self.records_to_modify:
            pd.DataFrame(self.records_to_modify).to_csv(
                f"{output_dir}/records_to_modify.csv", index=False
            )
            
        # Combined analysis file
        all_records = []
        for record in self.records_to_keep:
            record['proposed_action'] = 'KEEP'
            all_records.append(record)
            
        for record in self.records_to_remove:
            record['proposed_action'] = 'REMOVE'
            all_records.append(record)
            
        for record in self.records_to_modify:
            flat_record = {
                'original_id': record['original_id'],
                'value': record['value'],
                'unit': record['unit'],
                'year': record['year'],
                'metric_type': record['current_metric_type'],
                'context_preview': record['context_preview'],
                'reason': record['reason'],
                'confidence': record['confidence'],
                'proposed_action': 'MODIFY'
            }
            all_records.append(flat_record)
            
        if all_records:
            pd.DataFrame(all_records).sort_values('original_id').to_csv(
                f"{output_dir}/initial_analysis.csv", index=False
            )
            
        print(f"\nOutput Summary:")
        print(f"  Records to keep: {len(self.records_to_keep)}")
        print(f"  Records to remove: {len(self.records_to_remove)}")
        print(f"  Records to modify: {len(self.records_to_modify)}")
        
    def generate_enhanced_summary(self) -> Dict:
        """Generate comprehensive summary data"""
        summary = {
            'source_id': self.source_id,
            'source_name': self.source_name,
            'timestamp': datetime.now().isoformat(),
            'schema_version': '1.1',
            'total_records': len(self.source_df),
            'kept_records': len(self.records_to_keep),
            'removed_records': len(self.records_to_remove),
            'modified_records': len(self.records_to_modify),
            'duplicate_groups': len(self.duplicate_groups),
            'duplicates_removed': sum(len(d['duplicates']) for d in self.duplicate_groups.values()),
            'removal_reasons': dict(sorted(self.removal_reasons.items(), 
                                         key=lambda x: x[1], reverse=True)),
            'modification_types': dict(sorted(self.modification_types.items(), 
                                            key=lambda x: x[1], reverse=True)),
            'confidence_distribution': self._get_confidence_distribution(),
            'quality_metrics': self._calculate_quality_metrics()
        }
        
        # Find top removal reason
        if self.removal_reasons:
            top_reason = max(self.removal_reasons.items(), key=lambda x: x[1])
            summary['top_removal_reason'] = top_reason[0]
            summary['top_removal_count'] = top_reason[1]
        else:
            summary['top_removal_reason'] = ''
            summary['top_removal_count'] = 0
            
        return summary
        
    def _get_confidence_distribution(self) -> Dict:
        """Calculate confidence score distribution"""
        all_records = self.records_to_keep + self.records_to_remove + self.records_to_modify
        
        if not all_records:
            return {'high': 0, 'medium': 0, 'low': 0}
            
        high = sum(1 for r in all_records if r['confidence'] > 0.85)
        medium = sum(1 for r in all_records if 0.70 <= r['confidence'] <= 0.85)
        low = sum(1 for r in all_records if r['confidence'] < 0.70)
        
        return {
            'high': high,
            'medium': medium,
            'low': low,
            'high_pct': round(high / len(all_records) * 100, 1),
            'medium_pct': round(medium / len(all_records) * 100, 1),
            'low_pct': round(low / len(all_records) * 100, 1)
        }
        
    def _calculate_quality_metrics(self) -> Dict:
        """Calculate quality metrics for the source"""
        total = len(self.source_df)
        if total == 0:
            return {'quality_score': 0, 'issues_found': 0}
            
        issues = len(self.records_to_remove) + len(self.records_to_modify)
        quality_score = max(0, 100 - (issues / total * 100))
        
        return {
            'quality_score': round(quality_score, 2),
            'issues_found': issues,
            'removal_rate': round(len(self.records_to_remove) / total * 100, 2),
            'modification_rate': round(len(self.records_to_modify) / total * 100, 2)
        }
        
    def _track_quality_metrics(self):
        """Record quality metrics for trend tracking"""
        summary = self.generate_enhanced_summary()
        
        # Prepare data for quality tracker
        analysis_results = {
            'total_records': summary['total_records'],
            'kept_records': summary['kept_records'],
            'removed_records': summary['removed_records'],
            'modified_records': summary['modified_records'],
            'duplicate_groups': summary['duplicate_groups'],
            'duplicates_removed': summary['duplicates_removed'],
            'top_removal_reason': summary['top_removal_reason'],
            'top_removal_count': summary['top_removal_count'],
            'schema_version': summary['schema_version']
        }
        
        self.quality_tracker.record_source_analysis(
            self.source_id, self.source_name, analysis_results
        )
        
    def export_summary(self, summary_data: Dict):
        """Export summary in multiple formats"""
        output_dir = f"Source Data Cleanup Analysis/Source_{self.source_id}"
        
        # JSON export
        json_path = f"{output_dir}/summary.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2)
            
        # Markdown export
        md_path = f"{output_dir}/summary.md"
        md_content = self._generate_markdown_report(summary_data)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        # Traditional text summary (for backward compatibility)
        txt_path = f"{output_dir}/cleanup_summary.txt"
        txt_content = self._generate_text_summary(summary_data)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
            
        print(f"\nExported summaries:")
        print(f"  JSON: {json_path}")
        print(f"  Markdown: {md_path}")
        print(f"  Text: {txt_path}")
        
    def _generate_markdown_report(self, summary: Dict) -> str:
        """Generate markdown report"""
        md = f"""# Source {self.source_id} Cleanup Analysis Report

**File**: {summary['source_name']}  
**Analyzed**: {summary['timestamp']}  
**Schema Version**: {summary['schema_version']}

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | {summary['total_records']} | 100% |
| Records Kept | {summary['kept_records']} | {summary['kept_records']/summary['total_records']*100:.1f}% |
| Records Removed | {summary['removed_records']} | {summary['removed_records']/summary['total_records']*100:.1f}% |
| Records Modified | {summary['modified_records']} | {summary['modified_records']/summary['total_records']*100:.1f}% |

## Quality Metrics

- **Quality Score**: {summary['quality_metrics']['quality_score']}%
- **Issues Found**: {summary['quality_metrics']['issues_found']}
- **Removal Rate**: {summary['quality_metrics']['removal_rate']}%
- **Modification Rate**: {summary['quality_metrics']['modification_rate']}%

## Duplicate Handling

- **Duplicate Groups**: {summary['duplicate_groups']}
- **Duplicates Removed**: {summary['duplicates_removed']}

## Top Removal Reasons

| Reason | Count |
|--------|-------|
"""
        
        for reason, count in list(summary['removal_reasons'].items())[:10]:
            md += f"| {reason} | {count} |\n"
            
        if summary['modification_types']:
            md += "\n## Modification Types\n\n| Type | Count |\n|------|-------|\n"
            for mod_type, count in summary['modification_types'].items():
                md += f"| {mod_type} | {count} |\n"
                
        md += f"""
## Confidence Distribution

- **High (>85%)**: {summary['confidence_distribution']['high']} ({summary['confidence_distribution']['high_pct']}%)
- **Medium (70-85%)**: {summary['confidence_distribution']['medium']} ({summary['confidence_distribution']['medium_pct']}%)
- **Low (<70%)**: {summary['confidence_distribution']['low']} ({summary['confidence_distribution']['low_pct']}%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
"""
        
        return md
        
    def _generate_text_summary(self, summary: Dict) -> str:
        """Generate traditional text summary for compatibility"""
        return f"""SOURCE {summary['source_id']} CLEANUP ANALYSIS SUMMARY
Generated: {summary['timestamp']}

FILE: {summary['source_name']}
Original Records: {summary['total_records']}

PROPOSED ACTIONS:
- Records to KEEP: {summary['kept_records']}
- Records to REMOVE: {summary['removed_records']}
- Records to MODIFY: {summary['modified_records']}

Quality Score: {summary['quality_metrics']['quality_score']}%

Top removal reason: {summary['top_removal_reason']} ({summary['top_removal_count']} records)

Please review the detailed reports before proceeding with cleanup.
"""


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        source_id = int(sys.argv[1])
        previous_file = sys.argv[2] if len(sys.argv) > 2 else 'ai_metrics.csv'
        
        analyzer = EnhancedSourceAnalyzer(source_id, previous_file)
        analyzer.analyze()
        
        # Show quality trends
        trends = analyzer.quality_tracker.get_quality_trends()
        if 'error' not in trends:
            print("\n" + "=" * 80)
            print("OVERALL QUALITY TRENDS")
            print("=" * 80)
            print(f"Average Quality Score: {trends['average_quality_score']}%")
            print(f"Total Sources Analyzed: {trends['total_sources_analyzed']}")
    else:
        print("Usage: python source_cleanup_enhanced.py <source_id> [previous_cleaned_file]")
        print("Example: python source_cleanup_enhanced.py 8 ai_metrics_cleaned_source1_7.csv")