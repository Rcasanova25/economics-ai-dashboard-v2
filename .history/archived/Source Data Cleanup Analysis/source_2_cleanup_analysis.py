"""
Source 2 Cleanup Analysis - Following established template
Creates separate CSVs for review before any data modification
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class Source2CleanupAnalyzer:
    def __init__(self):
        # Load the dataset with Sources 7 and 1 already cleaned
        self.df = pd.read_csv('ai_metrics_cleaned_source1_7.csv')
        self.source_2_df = self.df[self.df['source_id'] == 2].copy()
        
        # Get source name
        sources_df = pd.read_csv('data/exports/data_sources_20250719.csv')
        self.source_name = sources_df[sources_df['id'] == 2]['name'].values[0]
        
        self.records_to_keep = []
        self.records_to_remove = []
        self.records_to_modify = []
        
    def analyze(self):
        """Run complete analysis and categorize all records"""
        print("=" * 80)
        print("SOURCE 2 CLEANUP ANALYSIS")
        print(f"File: {self.source_name}")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_2_df)}")
        
        # First, let's understand the data
        self.print_initial_analysis()
        
        # Analyze each record
        for idx, row in self.source_2_df.iterrows():
            self.categorize_record(idx, row)
            
        # Generate reports
        self.generate_csv_reports()
        self.generate_summary()
        
    def print_initial_analysis(self):
        """Print initial data analysis"""
        print("\nINITIAL DATA ANALYSIS:")
        print("-" * 40)
        
        # Metric type distribution
        print("\nMetric Type Distribution:")
        metric_dist = self.source_2_df['metric_type'].value_counts()
        for metric, count in metric_dist.items():
            print(f"  {metric}: {count} ({count/len(self.source_2_df)*100:.1f}%)")
            
        # Unit distribution
        print("\nUnit Distribution:")
        unit_dist = self.source_2_df['unit'].value_counts()
        for unit, count in unit_dist.head(10).items():
            print(f"  {unit}: {count}")
            
        # Check for problematic units
        problem_units = ['energy_unit', 'unknown', 'multiple', 'co2_emissions']
        found_problems = [u for u in problem_units if u in unit_dist.index]
        if found_problems:
            print(f"\n  WARNING: Problem units found: {found_problems}")
            
        # Year distribution
        print("\nYear Distribution:")
        year_dist = self.source_2_df['year'].value_counts().sort_index()
        print(f"  Range: {year_dist.index.min()} - {year_dist.index.max()}")
        
        # Value analysis for common patterns
        print("\nCommon Values (top 10):")
        value_counts = self.source_2_df['value'].value_counts().head(10)
        for value, count in value_counts.items():
            if count > 5:  # Only show values that appear frequently
                print(f"  {value}: appears {count} times")
        
        # Check for duplicates
        dup_cols = ['value', 'unit', 'year']
        duplicates = self.source_2_df[self.source_2_df.duplicated(subset=dup_cols, keep=False)]
        print(f"\nPotential duplicates (same value/unit/year): {len(duplicates)} records")
        
    def categorize_record(self, idx, row):
        """Categorize each record into keep/remove/modify"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        year = row['year']
        
        # Check for common issues first
        
        # 1. Check for 0.0 percentage that might be artifacts
        if value == 0.0 and unit == 'percentage':
            # Check if it's meaningful (e.g., "0% increase", "no change")
            meaningful_zero_keywords = ['no change', 'zero', 'unchanged', 'baseline', 'none', 'not']
            if not any(keyword in context for keyword in meaningful_zero_keywords):
                # Likely an artifact
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Zero percentage likely extraction artifact',
                    'confidence': 0.75
                })
                return
                
        # 2. Check for vague metric classifications
        if metric_type == 'general_rate':
            new_type = self.classify_general_rate(context, value, unit)
            if new_type != 'general_rate':
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': new_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector(context),
                    'country': '',
                    'company_size': '',
                    'reason': f'Reclassify based on context: {new_type}',
                    'confidence': 0.80
                })
            else:
                self.records_to_keep.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'General rate - needs manual review',
                    'confidence': 0.50
                })
            return
            
        # 3. Check for duplicates
        if self.is_duplicate(row):
            self.records_to_remove.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'reason': 'Duplicate record (same value/unit/year/similar context)',
                'confidence': 0.85
            })
            return
            
        # 4. Validate financial metrics
        if metric_type in ['cost_metric', 'financial_metric'] and unit == 'percentage':
            # Cost metrics with percentage might be cost reduction percentages
            if 'reduction' in context or 'decrease' in context or 'save' in context:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': 'cost_reduction_metric',
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': self.extract_sector(context),
                    'country': '',
                    'company_size': '',
                    'reason': 'Cost metric with percentage likely cost reduction',
                    'confidence': 0.85
                })
                return
                
        # Default - keep the record
        self.records_to_keep.append({
            'original_id': idx,
            'value': value,
            'unit': unit,
            'year': year,
            'metric_type': metric_type,
            'context_preview': context[:100] + '...' if len(context) > 100 else context,
            'reason': 'No issues detected',
            'confidence': 0.80
        })
        
    def classify_general_rate(self, context, value, unit):
        """Classify general_rate based on context"""
        # AI readiness/maturity related
        if any(word in context for word in ['readiness', 'maturity', 'stage', 'level']):
            return 'readiness_metric'
            
        # Strategy related
        if any(word in context for word in ['strategy', 'strategic', 'plan', 'initiative']):
            return 'strategy_metric'
            
        # Cost/ROI related
        if any(word in context for word in ['cost', 'roi', 'return', 'investment', 'spend']):
            return 'cost_metric'
            
        # Adoption related
        if any(word in context for word in ['adopt', 'implement', 'deploy', 'use', 'using']):
            return 'adoption_metric'
            
        # Performance/value related
        if any(word in context for word in ['value', 'benefit', 'improvement', 'performance']):
            return 'performance_metric'
            
        return 'general_rate'
        
    def extract_sector(self, context):
        """Try to extract sector information from context"""
        sectors = {
            'financial services': ['financial', 'banking', 'finance', 'fintech'],
            'healthcare': ['health', 'medical', 'pharma', 'clinical'],
            'retail': ['retail', 'commerce', 'shopping', 'consumer'],
            'manufacturing': ['manufacturing', 'industrial', 'production'],
            'technology': ['technology', 'tech', 'software', 'IT']
        }
        
        for sector, keywords in sectors.items():
            if any(keyword in context for keyword in keywords):
                return sector
                
        return ''
        
    def is_duplicate(self, row):
        """Check if this is a duplicate record"""
        # Get all records with same value/unit/year
        similar = self.source_2_df[
            (self.source_2_df['value'] == row['value']) &
            (self.source_2_df['unit'] == row['unit']) &
            (self.source_2_df['year'] == row['year'])
        ]
        
        # If more than one record with same values
        if len(similar) > 1:
            # Check context similarity
            current_context = str(row['context']).lower()
            for _, other in similar.iterrows():
                if other.name != row.name:  # Don't compare with itself
                    other_context = str(other['context']).lower()
                    # Simple similarity check - could be enhanced
                    if (current_context[:50] == other_context[:50] or 
                        current_context[-50:] == other_context[-50:]):
                        return True
                        
        return False
        
    def generate_csv_reports(self):
        """Generate the three CSV files"""
        # Create output directory
        import os
        output_dir = "Source Data Cleanup Analysis/Source_2"
        os.makedirs(output_dir, exist_ok=True)
        
        # Records to keep
        if self.records_to_keep:
            keep_df = pd.DataFrame(self.records_to_keep)
            keep_df.to_csv(f"{output_dir}/records_to_keep.csv", index=False)
            print(f"\nRecords to keep: {len(self.records_to_keep)}")
            
        # Records to remove
        if self.records_to_remove:
            remove_df = pd.DataFrame(self.records_to_remove)
            remove_df.to_csv(f"{output_dir}/records_to_remove.csv", index=False)
            print(f"Records to remove: {len(self.records_to_remove)}")
            
        # Records to modify
        if self.records_to_modify:
            modify_df = pd.DataFrame(self.records_to_modify)
            modify_df.to_csv(f"{output_dir}/records_to_modify.csv", index=False)
            print(f"Records to modify: {len(self.records_to_modify)}")
            
        # Initial analysis (all records with proposed actions)
        all_records = []
        
        for record in self.records_to_keep:
            record['proposed_action'] = 'KEEP'
            all_records.append(record)
            
        for record in self.records_to_remove:
            record['proposed_action'] = 'REMOVE'
            all_records.append(record)
            
        for record in self.records_to_modify:
            record['proposed_action'] = 'MODIFY'
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
            
        # Sort by original ID
        all_records_df = pd.DataFrame(all_records).sort_values('original_id')
        all_records_df.to_csv(f"{output_dir}/initial_analysis.csv", index=False)
        
    def generate_summary(self):
        """Generate summary text file"""
        output_dir = "Source Data Cleanup Analysis/Source_2"
        
        summary = f"""SOURCE 2 CLEANUP ANALYSIS SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE: {self.source_name}
Original Records: {len(self.source_2_df)}

PROPOSED ACTIONS:
- Records to KEEP: {len(self.records_to_keep)}
- Records to REMOVE: {len(self.records_to_remove)}
- Records to MODIFY: {len(self.records_to_modify)}

REMOVAL REASONS:
"""
        # Count removal reasons
        removal_reasons = {}
        for record in self.records_to_remove:
            reason = record['reason']
            removal_reasons[reason] = removal_reasons.get(reason, 0) + 1
            
        for reason, count in removal_reasons.items():
            summary += f"  - {reason}: {count} records\n"
            
        summary += "\nMODIFICATION SUMMARY:\n"
        
        # Count modification types
        mod_types = {}
        for record in self.records_to_modify:
            if 'current_metric_type' in record and 'new_metric_type' in record:
                change = f"{record['current_metric_type']} -> {record['new_metric_type']}"
                mod_types[change] = mod_types.get(change, 0) + 1
            
        for change, count in mod_types.items():
            summary += f"  - {change}: {count} records\n"
            
        # Count sector enrichments
        sector_count = sum(1 for r in self.records_to_modify if r.get('sector'))
        
        summary += f"""
METADATA ENRICHMENT:
- Records with sector identified: {sector_count}

CONFIDENCE DISTRIBUTION:
- High confidence (>0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] > 0.85)} records
- Medium confidence (0.70-0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if 0.70 <= r['confidence'] <= 0.85)} records  
- Low confidence (<0.70): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] < 0.70)} records

NEXT STEPS:
1. Review the CSV files to validate proposed actions
2. Pay special attention to zero percentage removals
3. Verify metric reclassifications
4. Approve or modify the cleanup plan before execution
"""
        
        with open(f"{output_dir}/cleanup_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"\nSummary saved to: {output_dir}/cleanup_summary.txt")
        

if __name__ == "__main__":
    analyzer = Source2CleanupAnalyzer()
    analyzer.analyze()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nFiles created in 'Source Data Cleanup Analysis/Source_2/':")
    print("  - initial_analysis.csv (all records with proposed actions)")
    print("  - records_to_keep.csv")
    print("  - records_to_remove.csv") 
    print("  - records_to_modify.csv")
    print("  - cleanup_summary.txt")
    print("\nPlease review these files before proceeding with cleanup.")