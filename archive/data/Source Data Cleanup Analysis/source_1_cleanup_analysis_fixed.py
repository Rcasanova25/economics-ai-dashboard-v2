"""
Source 1 Cleanup Analysis - FIXED to keep first instance of duplicates
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
        
        # Track duplicate groups for proper handling
        self.duplicate_groups = {}
        
    def analyze(self):
        """Run complete analysis and categorize all records"""
        print("=" * 80)
        print("SOURCE 1 CLEANUP ANALYSIS - FIXED DUPLICATE HANDLING")
        print(f"File: {self.source_name}")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_1_df)}")
        
        # First, let's understand the data
        self.print_initial_analysis()
        
        # Pre-process to identify duplicate groups
        self.identify_duplicate_groups()
        
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
            
        # Year distribution
        print("\nYear Distribution:")
        year_dist = self.source_1_df['year'].value_counts().sort_index()
        print(f"  Range: {year_dist.index.min()} - {year_dist.index.max()}")
        
        # Value analysis
        print("\nCommon Values (top 10):")
        value_counts = self.source_1_df['value'].value_counts().head(10)
        for value, count in value_counts.items():
            if count > 3:
                print(f"  {value}: appears {count} times")
                
    def identify_duplicate_groups(self):
        """Pre-identify duplicate groups to handle first occurrence properly"""
        self.duplicate_groups = {}
        
        # Group by value/unit/year
        grouped = self.source_1_df.groupby(['value', 'unit', 'year'])
        
        for (value, unit, year), group in grouped:
            if len(group) > 1:
                # Sort by index to ensure we keep the first occurrence
                sorted_group = group.sort_index()
                # Store first occurrence and duplicates separately
                self.duplicate_groups[(value, unit, year)] = {
                    'first': sorted_group.index[0],
                    'duplicates': sorted_group.index[1:].tolist()
                }
                
        print(f"\nIdentified {len(self.duplicate_groups)} duplicate groups")
        
    def categorize_record(self, idx, row):
        """Categorize each record into keep/remove/modify"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        year = row['year']
        
        # Check if this record is part of a duplicate group
        dup_key = (value, unit, year)
        if dup_key in self.duplicate_groups:
            dup_info = self.duplicate_groups[dup_key]
            
            if idx == dup_info['first']:
                # This is the first occurrence - process normally
                pass
            elif idx in dup_info['duplicates']:
                # This is a duplicate - mark for removal
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
                return
        
        # Check for other issues
        
        # 1. Check for energy_unit which is likely a misclassified reference year
        if unit == 'energy_unit':
            # These are often years from academic citations
            if 1950 <= value <= 2030:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'current_metric_type': metric_type,
                    'new_metric_type': 'reference_year',
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': '',
                    'country': '',
                    'company_size': '',
                    'reason': 'Energy unit is a misclassified year/reference',
                    'confidence': 0.95
                })
            else:
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Energy unit is a misclassified reference',
                    'confidence': 0.90
                })
            return
                
        # 2. Check for general_rate classifications
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
            
        # 3. Check for billions_usd parsing issues
        if unit == 'billions_usd' and context:
            # Check if this might be from figure/table labels
            if any(word in context for word in ['figure', 'table', 'exhibit', 'appendix']):
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': year,
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Likely from figure/table numbering',
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
        # Productivity related
        if any(word in context for word in ['productivity', 'efficiency', 'output', 'performance']):
            return 'productivity_metric'
            
        # Employment/labor related
        if any(word in context for word in ['employment', 'labor', 'worker', 'job', 'occupation']):
            return 'employment_metric'
            
        # Growth related
        if any(word in context for word in ['growth', 'increase', 'expansion', 'scaling']):
            return 'growth_metric'
            
        # Technology adoption
        if any(word in context for word in ['adoption', 'implementation', 'deployment', 'usage']):
            return 'adoption_metric'
            
        # AI/technology specific
        if any(word in context for word in ['ai', 'artificial intelligence', 'genai', 'generative']):
            return 'ai_metric'
            
        return 'general_rate'
        
    def generate_csv_reports(self):
        """Generate the three CSV files"""
        # Create output directory
        import os
        output_dir = "Source Data Cleanup Analysis/Source_1"
        os.makedirs(output_dir, exist_ok=True)
        
        # Records to keep
        if self.records_to_keep:
            keep_df = pd.DataFrame(self.records_to_keep)
            keep_df.to_csv(f"{output_dir}/records_to_keep_fixed.csv", index=False)
            print(f"\nRecords to keep: {len(self.records_to_keep)}")
            
        # Records to remove
        if self.records_to_remove:
            remove_df = pd.DataFrame(self.records_to_remove)
            remove_df.to_csv(f"{output_dir}/records_to_remove_fixed.csv", index=False)
            print(f"Records to remove: {len(self.records_to_remove)}")
            
        # Records to modify
        if self.records_to_modify:
            modify_df = pd.DataFrame(self.records_to_modify)
            modify_df.to_csv(f"{output_dir}/records_to_modify_fixed.csv", index=False)
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
        all_records_df.to_csv(f"{output_dir}/initial_analysis_fixed.csv", index=False)
        
    def generate_summary(self):
        """Generate summary text file"""
        output_dir = "Source Data Cleanup Analysis/Source_1"
        
        summary = f"""SOURCE 1 CLEANUP ANALYSIS SUMMARY - FIXED
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE: {self.source_name}
Original Records: {len(self.source_1_df)}

PROPOSED ACTIONS:
- Records to KEEP: {len(self.records_to_keep)}
- Records to REMOVE: {len(self.records_to_remove)}
- Records to MODIFY: {len(self.records_to_modify)}

DUPLICATE HANDLING:
- Duplicate groups identified: {len(self.duplicate_groups)}
- First occurrences kept: {len(self.duplicate_groups)}
- Subsequent duplicates removed: {sum(len(info['duplicates']) for info in self.duplicate_groups.values())}

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

KEY IMPROVEMENT:
- This analysis now properly keeps the first occurrence of each duplicate
- Previous analysis removed ALL occurrences of duplicated records
- This ensures no valuable data points are completely lost

NEXT STEPS:
1. Review the CSV files to validate proposed actions
2. Verify that important metrics are preserved
3. Check metric reclassifications
4. Approve or modify the cleanup plan before execution
"""
        
        with open(f"{output_dir}/cleanup_summary_fixed.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"\nSummary saved to: {output_dir}/cleanup_summary_fixed.txt")
        

if __name__ == "__main__":
    analyzer = Source1CleanupAnalyzer()
    analyzer.analyze()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nFiles created in 'Source Data Cleanup Analysis/Source_1/':")
    print("  - initial_analysis_fixed.csv (all records with proposed actions)")
    print("  - records_to_keep_fixed.csv")
    print("  - records_to_remove_fixed.csv") 
    print("  - records_to_modify_fixed.csv")
    print("  - cleanup_summary_fixed.txt")
    print("\nPlease review these files before proceeding with cleanup.")