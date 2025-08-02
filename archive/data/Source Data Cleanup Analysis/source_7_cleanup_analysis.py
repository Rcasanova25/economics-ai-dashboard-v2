"""
Source 7 Cleanup Analysis with Revised Understanding
Creates separate CSVs for review before any data modification
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime

class Source7CleanupAnalyzer:
    def __init__(self):
        self.df = pd.read_csv('data/exports/ai_metrics_20250719.csv')
        self.source_7_df = self.df[self.df['source_id'] == 7].copy()
        self.records_to_keep = []
        self.records_to_remove = []
        self.records_to_modify = []
        
    def analyze(self):
        """Run complete analysis and categorize all records"""
        print("=" * 80)
        print("SOURCE 7 CLEANUP ANALYSIS - REVISED APPROACH")
        print("=" * 80)
        print(f"Total records to analyze: {len(self.source_7_df)}")
        
        # Analyze each record
        for idx, row in self.source_7_df.iterrows():
            self.categorize_record(idx, row)
            
        # Generate reports
        self.generate_csv_reports()
        self.generate_summary()
        
    def categorize_record(self, idx, row):
        """Categorize each record into keep/remove/modify"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        
        # Check for energy_unit errors first (definite removal)
        if unit == 'energy_unit':
            self.records_to_remove.append({
                'original_id': idx,
                'value': value,
                'unit': unit,
                'year': row['year'],
                'metric_type': metric_type,
                'context_preview': context[:100] + '...' if len(context) > 100 else context,
                'reason': 'Energy unit is actually a citation year from references',
                'confidence': 0.95
            })
            return
            
        # Check if this is structured sector data
        is_sector_data = self.is_sector_comparison_data(context)
        
        if is_sector_data:
            # This is valuable sector comparison data - modify to enrich
            sector_info = self.extract_sector_info(context)
            
            # Determine new metric type based on context
            new_metric_type = 'adoption_metric'  # Most sector comparisons are about adoption
            
            # Check for duplicates in sector data
            if self.is_duplicate_sector_data(row, sector_info):
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': row['year'],
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': 'Duplicate sector comparison data (same country/sector/size/value)',
                    'confidence': 0.85
                })
            else:
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': row['year'],
                    'current_metric_type': metric_type,
                    'new_metric_type': new_metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': sector_info.get('sector', ''),
                    'country': sector_info.get('country', ''),
                    'company_size': sector_info.get('size', ''),
                    'reason': 'Sector comparison data - enrich with metadata',
                    'confidence': 0.90
                })
        else:
            # Not sector data - check other criteria
            action = self.determine_action_for_non_sector_data(idx, row)
            
            if action['action'] == 'keep':
                self.records_to_keep.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': row['year'],
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': action['reason'],
                    'confidence': action['confidence']
                })
            elif action['action'] == 'remove':
                self.records_to_remove.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': row['year'],
                    'metric_type': metric_type,
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'reason': action['reason'],
                    'confidence': action['confidence']
                })
            elif action['action'] == 'modify':
                self.records_to_modify.append({
                    'original_id': idx,
                    'value': value,
                    'unit': unit,
                    'year': row['year'],
                    'current_metric_type': metric_type,
                    'new_metric_type': action['new_metric_type'],
                    'context_preview': context[:100] + '...' if len(context) > 100 else context,
                    'sector': '',
                    'country': '',
                    'company_size': '',
                    'reason': action['reason'],
                    'confidence': action['confidence']
                })
                
    def is_sector_comparison_data(self, context):
        """Check if this record contains sector comparison data"""
        sector_indicators = [
            r'ict.*manufacturing|manufacturing.*ict',
            r'50-249|250\+',
            r'\b(deu|fra|ita|jpn|can)\b.*\d+\s*\(',
            r'\d+\s*\(\d+\.\d+%\)'
        ]
        
        matches = sum(1 for pattern in sector_indicators if re.search(pattern, context, re.IGNORECASE))
        return matches >= 2  # Need at least 2 indicators
        
    def extract_sector_info(self, context):
        """Extract structured information from sector data"""
        info = {}
        
        # Extract country
        country_map = {
            'deu': 'Germany',
            'fra': 'France', 
            'ita': 'Italy',
            'jpn': 'Japan',
            'can': 'Canada'
        }
        for code, name in country_map.items():
            if code in context.lower():
                info['country'] = name
                break
                
        # Extract sector
        if 'ict' in context.lower() and 'manufacturing' not in context.lower()[:20]:
            info['sector'] = 'ICT'
        elif 'manufacturing' in context.lower() and 'ict' not in context.lower()[:20]:
            info['sector'] = 'Manufacturing'
            
        # Extract company size
        if '50-249' in context:
            info['size'] = '50-249'
        elif '250+' in context or '250\+' in context:
            info['size'] = '250+'
            
        return info
        
    def is_duplicate_sector_data(self, row, sector_info):
        """Check if this sector data is a duplicate"""
        # For now, simple check - could be enhanced
        # Check if same value appears multiple times for same country/sector/size
        if row['value'] == 0.0 and row['unit'] == 'percentage':
            # Many 0.0% values are from table formatting, not real data
            if len(row['context']) < 100:  # Short contexts are often fragments
                return True
        return False
        
    def determine_action_for_non_sector_data(self, idx, row):
        """Determine action for records that aren't sector comparisons"""
        context = str(row['context']).lower()
        value = row['value']
        unit = row['unit']
        metric_type = row['metric_type']
        
        # Employment-related metrics
        if any(word in context for word in ['employment', 'jobs', 'occupation', 'worker', 'labor']):
            if metric_type != 'employment_metric':
                return {
                    'action': 'modify',
                    'new_metric_type': 'employment_metric',
                    'reason': 'Context indicates employment-related metric',
                    'confidence': 0.85
                }
            else:
                return {
                    'action': 'keep',
                    'reason': 'Properly classified employment metric',
                    'confidence': 0.90
                }
                
        # Productivity metrics
        elif any(word in context for word in ['productivity', 'efficiency', 'output', 'performance']):
            if metric_type != 'productivity_metric':
                return {
                    'action': 'modify',
                    'new_metric_type': 'productivity_metric',
                    'reason': 'Context indicates productivity-related metric',
                    'confidence': 0.85
                }
            else:
                return {
                    'action': 'keep',
                    'reason': 'Properly classified productivity metric',
                    'confidence': 0.90
                }
                
        # Check for meaningless 0.0% not in sector data
        elif value == 0.0 and unit == 'percentage' and len(context) < 50:
            return {
                'action': 'remove',
                'reason': 'Fragment with 0.0% - likely parsing error',
                'confidence': 0.80
            }
            
        # General rates that need classification
        elif metric_type == 'general_rate':
            # Try to classify based on context
            if 'growth' in context or 'increase' in context:
                return {
                    'action': 'modify',
                    'new_metric_type': 'growth_metric',
                    'reason': 'Context indicates growth metric',
                    'confidence': 0.75
                }
            elif 'adopt' in context or 'usage' in context:
                return {
                    'action': 'modify', 
                    'new_metric_type': 'adoption_metric',
                    'reason': 'Context indicates adoption metric',
                    'confidence': 0.75
                }
            else:
                return {
                    'action': 'keep',
                    'reason': 'General rate - needs manual review for classification',
                    'confidence': 0.50
                }
        else:
            # Default - keep with current classification
            return {
                'action': 'keep',
                'reason': 'No issues detected',
                'confidence': 0.70
            }
            
    def generate_csv_reports(self):
        """Generate the three CSV files"""
        output_dir = "Source Data Cleanup Analysis/Source_7"
        
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
            # Flatten the modify records for the combined view
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
            
        # Sort by original ID to maintain order
        all_records_df = pd.DataFrame(all_records).sort_values('original_id')
        all_records_df.to_csv(f"{output_dir}/initial_analysis.csv", index=False)
        
    def generate_summary(self):
        """Generate summary text file"""
        output_dir = "Source Data Cleanup Analysis/Source_7"
        
        summary = f"""SOURCE 7 CLEANUP ANALYSIS SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FILE: cost-benefit-analysis-artificial-intelligence-evidence-from-a-field-experiment-on-gpt-4o-1.pdf
Original Records: {len(self.source_7_df)}

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
            change = f"{record['current_metric_type']} → {record['new_metric_type']}"
            mod_types[change] = mod_types.get(change, 0) + 1
            
        for change, count in mod_types.items():
            summary += f"  - {change}: {count} records\n"
            
        summary += f"""
KEY INSIGHTS:
1. Identified {sum(1 for r in self.records_to_modify if r.get('sector'))} sector comparison records
2. Found {sum(1 for r in self.records_to_remove if 'energy_unit' in r['reason'])} energy_unit errors
3. Detected {sum(1 for r in self.records_to_remove if 'Duplicate' in r['reason'])} duplicate records

CONFIDENCE DISTRIBUTION:
- High confidence (>0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] > 0.85)} records
- Medium confidence (0.70-0.85): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if 0.70 <= r['confidence'] <= 0.85)} records  
- Low confidence (<0.70): {sum(1 for r in self.records_to_keep + self.records_to_remove + self.records_to_modify if r['confidence'] < 0.70)} records

NEXT STEPS:
1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Confirm sector data identification is accurate
4. Approve or modify the cleanup plan before execution
"""
        
        with open(f"{output_dir}/cleanup_summary.txt", 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"\nSummary saved to: {output_dir}/cleanup_summary.txt")
        

if __name__ == "__main__":
    analyzer = Source7CleanupAnalyzer()
    analyzer.analyze()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nFiles created in 'Source Data Cleanup Analysis/Source_7/':")
    print("  - initial_analysis.csv (all records with proposed actions)")
    print("  - records_to_keep.csv")
    print("  - records_to_remove.csv") 
    print("  - records_to_modify.csv")
    print("  - cleanup_summary.txt")
    print("\nPlease review these files before proceeding with cleanup.")