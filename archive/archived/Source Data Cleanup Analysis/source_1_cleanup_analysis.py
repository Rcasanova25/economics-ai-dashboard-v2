"""
Source 1 Cleanup Analysis - Following Source 7 Template
Creates separate CSVs for review before any data modification
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class Source1CleanupAnalyzer:
    def __init__(self):
        # Load the dataset with Source 7 already cleaned
        self.df = pd.read_csv('ai_metrics_cleaned_source7.csv')
        self.source_1_df = self.df[self.df['source_id'] == 1].copy()
        
        # Get source name
        sources_df = pd.read_csv('data/exports/data_sources_20250719.csv')
        self.source_name = sources_df[sources_df['id'] == 1]['name'].values[0]
        
        self.records_to_keep = []
        self.records_to_remove = []
        self.records_to_modify = []
        
    def analyze(self):
        """Run complete analysis and categorize all records"""
        print("=" * 80)
        print("SOURCE 1 CLEANUP ANALYSIS")
        print(f"File: {self.source_name}")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_1_df)}")
        
        # First, let's understand the data
        self.print_initial_analysis()
        
        # Analyze each record
        for idx, row in self.source_1_df.iterrows():
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
        metric_dist = self.source_1_df['metric_type'].value_counts()
        for metric, count in metric_dist.items():
            print(f"  {metric}: {count} ({count/len(self.source_1_df)*100:.1f}%)")
            
        # Unit distribution
        print("\nUnit Distribution:")
        unit_dist = self.source_1_df['unit'].value_counts()
        for unit, count in unit_dist.head(10).items():
            print(f"  {unit}: {count}")
            
        # Check for problematic units
        problem_units = ['energy_unit', 'unknown', 'multiple', 'co2_emissions']
        found_problems = [u for u in problem_units if u in unit_dist.index]
        if found_problems:
            print(f"\n  WARNING: Problem units found: {found_problems}")
            
        # Year distribution
        print("\nYear Distribution:")
        year_dist = self.source_1_df['year'].value_counts().sort_index()
        print(f"  Range: {year_dist.index.min()} - {year_dist.index.max()}")
        
        # Check for duplicates
        dup_cols = ['value', 'unit', 'year']
        duplicates = self.source_1_df[self.source_1_df.duplicated(subset=dup_cols, keep=False)]
        print(f"\nPotential duplicates (same value/unit/year): {len(duplicates)} records")
        
    def categorize_record(self, idx, row):
        """Categorize each record into keep/remove/modify"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        year = row['year']
        
        # Check for energy_unit errors first
        if unit == 'energy_unit':
            self.records_to_remove.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'reason': 'Energy unit is a misclassified year/reference',
                'confidence': 0.95
            })
            return
            
        # Check for future years that don't make sense
        if year > 2025 and 'forecast' not in context and 'project' not in context:
            self.records_to_modify.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'current_metric_type': metric_type,
                'new_metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'sector': '',
                'country': '',
                'company_size': '',
                'reason': f'Year {year} seems incorrect - needs verification',
                'confidence': 0.60
            })
            return
            
        # Check for vague metric classifications
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
                    'sector': '',
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
            
        # Check for unknown_metric
        if metric_type == 'unknown_metric':
            new_type = self.classify_unknown_metric(context, value, unit)
            self.records_to_modify.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'current_metric_type': metric_type,
                'new_metric_type': new_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'sector': '',
                'country': '',
                'company_size': '',
                'reason': f'Classify unknown metric as: {new_type}',
                'confidence': 0.75
            })
            return
            
        # Check for duplicates
        if self.is_duplicate(row):
            self.records_to_remove.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': year,
                'metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'reason': 'Duplicate record (same value/unit/year/context)',
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
        # Developer/coding related
        if any(word in context for word in ['developer', 'code', 'commit', 'pull request', 'github', 'copilot']):
            return 'productivity_metric'
            
        # Employment related
        if any(word in context for word in ['job', 'employment', 'worker', 'occupation']):
            return 'employment_metric'
            
        # Adoption related
        if any(word in context for word in ['adopt', 'usage', 'user', 'using', 'access']):
            return 'adoption_metric'
            
        # Growth related
        if any(word in context for word in ['growth', 'increase', 'rise', 'gain']):
            return 'growth_metric'
            
        # Performance related
        if any(word in context for word in ['performance', 'productivity', 'efficiency', 'output']):
            return 'productivity_metric'
            
        return 'general_rate'
        
    def classify_unknown_metric(self, context, value, unit):
        """Classify unknown_metric based on context and unit"""
        # Check unit first
        if unit in ['billions_usd', 'millions_usd', 'usd']:
            if 'invest' in context:
                return 'investment_metric'
            elif 'cost' in context:
                return 'cost_metric'
            elif 'revenue' in context:
                return 'revenue_metric'
            else:
                return 'financial_metric'
                
        # If it's a year value
        if value > 2000 and value < 2030 and unit == 'number':
            return 'reference_year'  # Should be removed
            
        # Default
        return 'general_metric'
        
    def is_duplicate(self, row):
        """Check if this is a duplicate record"""
        # Get all records with same value/unit/year
        similar = self.source_1_df[
            (self.source_1_df['value'] == row['value']) &
            (self.source_1_df['unit'] == row['unit']) &
            (self.source_1_df['year'] == row['year'])
        ]
        
        # If more than one record with same values
        if len(similar) > 1:
            # Check if contexts are very similar
            contexts = similar['context'].tolist()
            # Simple check - if contexts are identical or very short fragments
            if len(set(contexts)) < len(contexts):
                return True
                
        return False
        
    def generate_csv_reports(self):
        """Generate the three CSV files"""
        # Create output directory
        import os
        output_dir = "Source Data Cleanup Analysis/Source_1"
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
        output_dir = "Source Data Cleanup Analysis/Source_1"
        
        summary = f"""SOURCE 1 CLEANUP ANALYSIS SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE: {self.source_name}
Original Records: {len(self.source_1_df)}

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
            
        summary += f"""
CONFIDENCE DISTRIBUTION:
- High confidence (>0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] > 0.85)} records
- Medium confidence (0.70-0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if 0.70 <= r['confidence'] <= 0.85)} records  
- Low confidence (<0.70): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] < 0.70)} records

NEXT STEPS:
1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify year corrections and metric reclassifications
4. Approve or modify the cleanup plan before execution
"""
        
        with open(f"{output_dir}/cleanup_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"\nSummary saved to: {output_dir}/cleanup_summary.txt")
        

if __name__ == "__main__":
    analyzer = Source1CleanupAnalyzer()
    analyzer.analyze()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nFiles created in 'Source Data Cleanup Analysis/Source_1/':")
    print("  - initial_analysis.csv (all records with proposed actions)")
    print("  - records_to_keep.csv")
    print("  - records_to_remove.csv") 
    print("  - records_to_modify.csv")
    print("  - cleanup_summary.txt")
    print("\nPlease review these files before proceeding with cleanup.")