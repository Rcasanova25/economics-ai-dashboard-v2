"""
Analyze data quality issues by source ID
This script examines each source's data to understand patterns before cleaning
"""

import pandas as pd
import numpy as np
from collections import Counter

class SourceAnalyzer:
    def __init__(self, csv_path, sources_csv_path):
        self.df = pd.read_csv(csv_path)
        self.sources = pd.read_csv(sources_csv_path)
        self.source_map = dict(zip(self.sources['id'], self.sources['name']))
        
    def analyze_source(self, source_id):
        """Analyze a specific source's data"""
        source_name = self.source_map.get(source_id, f"Unknown Source {source_id}")
        source_df = self.df[self.df['source_id'] == source_id]
        
        if len(source_df) == 0:
            print(f"\nNo data found for source {source_id}")
            return
            
        print(f"\n{'='*80}")
        print(f"SOURCE {source_id}: {source_name}")
        print(f"{'='*80}")
        
        print(f"\n1. BASIC STATISTICS:")
        print(f"   Total records: {len(source_df)}")
        print(f"   Unique metric types: {source_df['metric_type'].nunique()}")
        print(f"   Year range: {source_df['year'].min()} - {source_df['year'].max()}")
        
        print(f"\n2. METRIC TYPE DISTRIBUTION:")
        metric_counts = source_df['metric_type'].value_counts()
        for metric, count in metric_counts.head(10).items():
            print(f"   - {metric}: {count} ({count/len(source_df)*100:.1f}%)")
            
        print(f"\n3. UNIT DISTRIBUTION:")
        unit_counts = source_df['unit'].value_counts()
        for unit, count in unit_counts.head(10).items():
            print(f"   - {unit}: {count}")
            
        # Check for problematic units
        problem_units = ['energy_unit', 'unknown', 'multiple']
        found_problems = [u for u in problem_units if u in unit_counts.index]
        if found_problems:
            print(f"\n   WARNING: Problem units found: {found_problems}")
            
        print(f"\n4. DUPLICATE ANALYSIS:")
        # Check for exact duplicates
        dup_cols = ['value', 'unit', 'year', 'context']
        duplicates = source_df[source_df.duplicated(subset=dup_cols, keep=False)]
        print(f"   Records with duplicates: {len(duplicates)}")
        
        if len(duplicates) > 0:
            # Show top duplicate groups
            dup_groups = duplicates.groupby(dup_cols[:-1]).size().reset_index(name='count')
            dup_groups = dup_groups.sort_values('count', ascending=False).head(5)
            print(f"\n   Top duplicate groups:")
            for _, group in dup_groups.iterrows():
                print(f"   - Value: {group['value']}, Unit: {group['unit']}, Year: {group['year']} → {group['count']} times")
                
        print(f"\n5. VALUE RANGE ANALYSIS:")
        # Analyze by metric type and unit
        for metric_type in source_df['metric_type'].value_counts().head(3).index:
            metric_df = source_df[source_df['metric_type'] == metric_type]
            print(f"\n   {metric_type}:")
            for unit in metric_df['unit'].value_counts().head(3).index:
                unit_df = metric_df[metric_df['unit'] == unit]
                values = unit_df['value'].dropna()
                if len(values) > 0:
                    print(f"     {unit}: min={values.min():.2f}, max={values.max():.2f}, mean={values.mean():.2f}")
                    
        print(f"\n6. SAMPLE RECORDS (First 5):")
        sample_cols = ['metric_type', 'value', 'unit', 'year', 'context']
        for idx, row in source_df[sample_cols].head(5).iterrows():
            context_preview = str(row['context'])[:80] + '...' if len(str(row['context'])) > 80 else str(row['context'])
            print(f"\n   Record {idx}:")
            print(f"   - Type: {row['metric_type']}")
            print(f"   - Value: {row['value']} {row['unit']} ({row['year']})")
            print(f"   - Context: {context_preview}")
            
        print(f"\n7. DATA QUALITY ISSUES SUMMARY:")
        issues = []
        
        # Check vague metric types
        vague_types = ['general_rate', 'unknown_metric', 'percentages']
        vague_count = source_df[source_df['metric_type'].isin(vague_types)].shape[0]
        if vague_count > 0:
            issues.append(f"- {vague_count} records with vague metric types")
            
        # Check missing data
        for col in ['sector', 'region', 'technology']:
            missing = source_df[col].isna().sum()
            if missing > 0:
                issues.append(f"- {missing} records missing {col}")
                
        # Check outliers (simple check for extreme values)
        if 'percentage' in source_df['unit'].values:
            pct_df = source_df[source_df['unit'] == 'percentage']
            extreme_pct = pct_df[(pct_df['value'] > 200) | (pct_df['value'] < -50)]
            if len(extreme_pct) > 0:
                issues.append(f"- {len(extreme_pct)} percentage values outside normal range")
                
        if issues:
            for issue in issues:
                print(f"   {issue}")
        else:
            print("   No major issues found")
            
    def analyze_all_sources(self):
        """Analyze all sources in order"""
        source_ids = sorted(self.df['source_id'].unique())
        
        print(f"ANALYZING {len(source_ids)} SOURCES")
        print(f"Total records across all sources: {len(self.df)}")
        
        for source_id in source_ids:
            self.analyze_source(source_id)
            
        # Overall summary
        self.print_overall_summary()
        
    def print_overall_summary(self):
        """Print summary across all sources"""
        print(f"\n{'='*80}")
        print("OVERALL SUMMARY ACROSS ALL SOURCES")
        print(f"{'='*80}")
        
        # Sources with most records
        print("\nSOURCES BY RECORD COUNT:")
        source_counts = self.df['source_id'].value_counts().head(10)
        for source_id, count in source_counts.items():
            name = self.source_map.get(source_id, f"Unknown {source_id}")
            print(f"   {source_id}. {name}: {count} records")
            
        # Most common metric types overall
        print("\nMOST COMMON METRIC TYPES OVERALL:")
        overall_metrics = self.df['metric_type'].value_counts().head(10)
        for metric, count in overall_metrics.items():
            print(f"   - {metric}: {count} ({count/len(self.df)*100:.1f}%)")
            
        # Problem units summary
        print("\nPROBLEM UNITS ACROSS ALL SOURCES:")
        problem_units = ['energy_unit', 'unknown', 'multiple']
        for unit in problem_units:
            count = (self.df['unit'] == unit).sum()
            if count > 0:
                sources_with_unit = self.df[self.df['unit'] == unit]['source_id'].unique()
                print(f"   - {unit}: {count} records in sources {list(sources_with_unit)}")


if __name__ == "__main__":
    import sys
    import io
    
    # Set up proper encoding for output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    analyzer = SourceAnalyzer(
        'data/exports/ai_metrics_20250719.csv',
        'data/exports/data_sources_20250719.csv'
    )
    
    # Also save output to file
    import contextlib
    
    with open('source_analysis_report.txt', 'w', encoding='utf-8') as f:
        with contextlib.redirect_stdout(f):
            analyzer.analyze_all_sources()
    
    # Also print to console
    analyzer.analyze_all_sources()