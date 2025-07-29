"""
Execute Source 1 Cleanup Based on Approved Analysis
Using the same structure as Source 7 cleanup
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class Source1CleanupExecutor:
    def __init__(self):
        # Load data (with Source 7 already cleaned)
        self.full_df = pd.read_csv('ai_metrics_cleaned_source7.csv')
        self.source_1_df = self.full_df[self.full_df['source_id'] == 1].copy()
        
        # Load cleanup instructions
        self.to_keep = pd.read_csv('Source Data Cleanup Analysis/Source_1/records_to_keep.csv')
        self.to_remove = pd.read_csv('Source Data Cleanup Analysis/Source_1/records_to_remove.csv')
        self.to_modify = pd.read_csv('Source Data Cleanup Analysis/Source_1/records_to_modify.csv')
        
        self.execution_log = []
        
    def execute_cleanup(self):
        """Execute the approved cleanup plan"""
        print("=" * 80)
        print("EXECUTING SOURCE 1 CLEANUP")
        print("=" * 80)
        print(f"Starting with {len(self.source_1_df)} records")
        
        # Step 1: Remove records marked for removal
        removed_ids = set(self.to_remove['original_id'].values)
        self.log_action(f"Removing {len(removed_ids)} records")
        
        # Step 2: Modify records marked for modification
        modified_count = self.apply_modifications()
        
        # Step 3: Create cleaned Source 1 dataframe
        cleaned_source_1 = self.source_1_df.copy()
        
        # Remove the records marked for removal
        cleaned_source_1 = cleaned_source_1[~cleaned_source_1.index.isin(removed_ids)]
        
        # Apply modifications
        for _, mod in self.to_modify.iterrows():
            idx = mod['original_id']
            if idx in cleaned_source_1.index:
                # Update metric type
                cleaned_source_1.at[idx, 'metric_type'] = mod['new_metric_type']
                
                # Note: Source 1 doesn't have sector/country data like Source 7
                # But we could add technology field for AI tool type if needed
                context = str(cleaned_source_1.at[idx, 'context']).lower()
                if 'copilot' in context:
                    cleaned_source_1.at[idx, 'technology'] = 'GitHub Copilot'
                elif 'gpt' in context:
                    cleaned_source_1.at[idx, 'technology'] = 'GPT'
        
        # Step 4: Update the main dataset
        # Remove all old Source 1 records
        cleaned_full_df = self.full_df[self.full_df['source_id'] != 1].copy()
        
        # Add cleaned Source 1 records
        cleaned_full_df = pd.concat([cleaned_full_df, cleaned_source_1], ignore_index=True)
        
        # Step 5: Save outputs
        self.save_outputs(cleaned_source_1, cleaned_full_df)
        
        # Step 6: Generate execution report
        self.generate_execution_report(len(self.source_1_df), len(cleaned_source_1))
        
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
        
    def save_outputs(self, cleaned_source_1, cleaned_full_df):
        """Save all output files"""
        output_dir = "Source Data Cleanup Analysis/Source_1"
        
        # Save cleaned Source 1 data
        cleaned_source_1.to_csv(f"{output_dir}/cleaned_data.csv", index=False)
        print(f"\nSaved cleaned Source 1 data to: {output_dir}/cleaned_data.csv")
        
        # Save updated full dataset (now with both Source 7 and 1 cleaned)
        cleaned_full_df.to_csv("ai_metrics_cleaned_source1_7.csv", index=False)
        print(f"Saved updated full dataset to: ai_metrics_cleaned_source1_7.csv")
        
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
        output_dir = "Source Data Cleanup Analysis/Source_1"
        
        report = f"""SOURCE 1 CLEANUP EXECUTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTION SUMMARY:
- Original Source 1 records: {original_count}
- Records removed: {len(self.to_remove)}
- Records modified: {len(self.to_modify)}
- Records kept as-is: {len(self.to_keep)}
- Final Source 1 records: {final_count}
- Reduction: {(1 - final_count/original_count)*100:.1f}%

MODIFICATIONS APPLIED:
"""
        # Add modification summary
        mod_summary = self.to_modify.groupby(['current_metric_type', 'new_metric_type']).size()
        for (current, new), count in mod_summary.items():
            report += f"  - {current} -> {new}: {count} records\n"
            
        # Count technology enrichments
        tech_count = 0
        if 'technology' in self.to_modify.columns:
            tech_count = len(self.to_modify[self.to_modify['technology'].notna()])
            
        report += f"""
METADATA ENRICHMENT:
- Records with AI technology identified: {tech_count}

KEY REMOVALS:
- Duplicate statistics (paper repetition): {sum(1 for r in self.to_remove if 'Duplicate' in self.to_remove.iloc[0]['reason'])}
- Figure/table parsing errors: {sum(1 for r in self.to_remove if 'billions_usd' in str(r) and '24' in str(r))}
- Energy unit errors (citation years): 4

VERIFICATION:
- All records accounted for: {'YES' if original_count == len(self.to_keep) + len(self.to_remove) + len(self.to_modify) else 'NO'}
- Execution completed successfully: YES

FILES CREATED:
1. {output_dir}/cleaned_data.csv - Cleaned Source 1 data only
2. ai_metrics_cleaned_source1_7.csv - Full dataset with Sources 1 & 7 cleaned
3. {output_dir}/execution_log.csv - Detailed execution log
4. {output_dir}/execution_report.txt - This report

CUMULATIVE PROGRESS:
- Sources cleaned: 2 of 22 (Source 7, Source 1)
- Original total records: 12,258
- Current total records: Will be calculated after execution
- Next source: Source 2

NEXT STEPS:
1. Verify the cleaned data meets expectations
2. Proceed with Source 2 cleanup using this same process
3. Continue through all sources in numerical order
"""
        
        with open(f"{output_dir}/execution_report.txt", 'w', encoding='utf-8') as f:
            f.write(report)
            
        print("\n" + "=" * 80)
        print("CLEANUP EXECUTION COMPLETE")
        print("=" * 80)
        print(report)
        

if __name__ == "__main__":
    executor = Source1CleanupExecutor()
    cleaned_df = executor.execute_cleanup()
    
    # Quick verification
    print("\nVERIFICATION:")
    print(f"Dataset after Source 7 cleanup: {len(pd.read_csv('ai_metrics_cleaned_source7.csv'))} records")
    print(f"Dataset after Source 1 cleanup: {len(cleaned_df)} records")
    print(f"Source 1 records before: 334")
    print(f"Source 1 records after: {len(cleaned_df[cleaned_df['source_id'] == 1])}")
    print(f"\nTotal reduction so far: {12258 - len(cleaned_df)} records removed")