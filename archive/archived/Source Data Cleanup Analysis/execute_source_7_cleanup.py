"""
Execute Source 7 Cleanup Based on Approved Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class Source7CleanupExecutor:
    def __init__(self):
        # Load original data
        self.full_df = pd.read_csv('data/exports/ai_metrics_20250719.csv')
        self.source_7_df = self.full_df[self.full_df['source_id'] == 7].copy()
        
        # Load cleanup instructions
        self.to_keep = pd.read_csv('Source Data Cleanup Analysis/Source_7/records_to_keep.csv')
        self.to_remove = pd.read_csv('Source Data Cleanup Analysis/Source_7/records_to_remove.csv')
        self.to_modify = pd.read_csv('Source Data Cleanup Analysis/Source_7/records_to_modify.csv')
        
        self.execution_log = []
        
    def execute_cleanup(self):
        """Execute the approved cleanup plan"""
        print("=" * 80)
        print("EXECUTING SOURCE 7 CLEANUP")
        print("=" * 80)
        print(f"Starting with {len(self.source_7_df)} records")
        
        # Step 1: Remove records marked for removal
        removed_ids = set(self.to_remove['original_id'].values)
        self.log_action(f"Removing {len(removed_ids)} records")
        
        # Step 2: Modify records marked for modification
        modified_count = self.apply_modifications()
        
        # Step 3: Create cleaned Source 7 dataframe
        # Start with all Source 7 records
        cleaned_source_7 = self.source_7_df.copy()
        
        # Remove the records marked for removal
        cleaned_source_7 = cleaned_source_7[~cleaned_source_7.index.isin(removed_ids)]
        
        # Apply modifications
        for _, mod in self.to_modify.iterrows():
            idx = mod['original_id']
            if idx in cleaned_source_7.index:
                # Update metric type
                cleaned_source_7.at[idx, 'metric_type'] = mod['new_metric_type']
                
                # Add sector metadata if available
                if pd.notna(mod.get('sector')) and mod['sector']:
                    cleaned_source_7.at[idx, 'sector'] = mod['sector']
                if pd.notna(mod.get('country')) and mod['country']:
                    cleaned_source_7.at[idx, 'region'] = mod['country']
                if pd.notna(mod.get('company_size')) and mod['company_size']:
                    # Add to context or new field
                    cleaned_source_7.at[idx, 'technology'] = f"Company Size: {mod['company_size']}"
        
        # Step 4: Update the main dataset
        # Remove all old Source 7 records
        cleaned_full_df = self.full_df[self.full_df['source_id'] != 7].copy()
        
        # Add cleaned Source 7 records
        cleaned_full_df = pd.concat([cleaned_full_df, cleaned_source_7], ignore_index=True)
        
        # Step 5: Save outputs
        self.save_outputs(cleaned_source_7, cleaned_full_df)
        
        # Step 6: Generate execution report
        self.generate_execution_report(len(self.source_7_df), len(cleaned_source_7))
        
        return cleaned_full_df
        
    def apply_modifications(self):
        """Apply modifications to records"""
        print(f"\nApplying modifications to {len(self.to_modify)} records...")
        
        modifications_by_type = {}
        for _, mod in self.to_modify.iterrows():
            change = f"{mod['current_metric_type']} -> {mod['new_metric_type']}"
            modifications_by_type[change] = modifications_by_type.get(change, 0) + 1
            
        for change, count in modifications_by_type.items():
            print(f"  {change}: {count} records")
            self.log_action(f"Modified {count} records: {change}")
            
        return len(self.to_modify)
        
    def save_outputs(self, cleaned_source_7, cleaned_full_df):
        """Save all output files"""
        output_dir = "Source Data Cleanup Analysis/Source_7"
        
        # Save cleaned Source 7 data
        cleaned_source_7.to_csv(f"{output_dir}/cleaned_data.csv", index=False)
        print(f"\nSaved cleaned Source 7 data to: {output_dir}/cleaned_data.csv")
        
        # Save updated full dataset
        cleaned_full_df.to_csv("ai_metrics_cleaned_source7.csv", index=False)
        print(f"Saved updated full dataset to: ai_metrics_cleaned_source7.csv")
        
        # Save execution log
        log_df = pd.DataFrame(self.execution_log)
        log_df.to_csv(f"{output_dir}/execution_log.csv", index=False)
        
    def log_action(self, action):
        """Log cleanup actions"""
        self.execution_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': action
        })
        
    def generate_execution_report(self, original_count, final_count):
        """Generate execution report"""
        output_dir = "Source Data Cleanup Analysis/Source_7"
        
        report = f"""SOURCE 7 CLEANUP EXECUTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTION SUMMARY:
- Original Source 7 records: {original_count}
- Records removed: {len(self.to_remove)}
- Records modified: {len(self.to_modify)}
- Records kept as-is: {len(self.to_keep)}
- Final Source 7 records: {final_count}
- Reduction: {(1 - final_count/original_count)*100:.1f}%

MODIFICATIONS APPLIED:
"""
        # Add modification summary
        mod_summary = self.to_modify.groupby(['current_metric_type', 'new_metric_type']).size()
        for (current, new), count in mod_summary.items():
            report += f"  - {current} -> {new}: {count} records\n"
            
        report += f"""
METADATA ENRICHMENT:
- Records with sector added: {len(self.to_modify[self.to_modify['sector'].notna() & (self.to_modify['sector'] != '')])}
- Records with country added: {len(self.to_modify[self.to_modify['country'].notna() & (self.to_modify['country'] != '')])}
- Records with company size added: {len(self.to_modify[self.to_modify['company_size'].notna() & (self.to_modify['company_size'] != '')])}

VERIFICATION:
- All records accounted for: {'YES' if original_count == len(self.to_keep) + len(self.to_remove) + len(self.to_modify) else 'NO'}
- Execution completed successfully: YES

FILES CREATED:
1. {output_dir}/cleaned_data.csv - Cleaned Source 7 data only
2. ai_metrics_cleaned_source7.csv - Full dataset with Source 7 cleaned
3. {output_dir}/execution_log.csv - Detailed execution log
4. {output_dir}/execution_report.txt - This report

NEXT STEPS:
1. Verify the cleaned data meets expectations
2. Proceed with Source 1 cleanup using this same process
3. Continue through all sources in numerical order
"""
        
        with open(f"{output_dir}/execution_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
            
        print("\n" + "=" * 80)
        print("CLEANUP EXECUTION COMPLETE")
        print("=" * 80)
        print(report)
        

if __name__ == "__main__":
    executor = Source7CleanupExecutor()
    cleaned_df = executor.execute_cleanup()
    
    # Quick verification
    print("\nVERIFICATION:")
    print(f"Original total records: {len(pd.read_csv('data/exports/ai_metrics_20250719.csv'))}")
    print(f"Cleaned total records: {len(cleaned_df)}")
    print(f"Source 7 records before: 2472")
    print(f"Source 7 records after: {len(cleaned_df[cleaned_df['source_id'] == 7])}")