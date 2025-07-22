"""
Integrated Source Cleanup Workflow
Combines backup, logging, and cleanup operations into a single automated workflow

This script ensures:
1. Automated backup before each cleanup
2. Comprehensive logging of all operations
3. Safety checks and confirmation prompts
4. Progress tracking across multiple sources
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import logging
import json
import pandas as pd
from typing import Optional, List, Dict

# Add parent directories to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import from absolute paths
from src.utils.backup_manager import BackupManager
from src.utils.logging_config import CleanupLogger

# Import the template from project root
sys.path.insert(0, str(project_root))
from source_cleanup_template import SourceCleanupAnalyzer

class CleanupWorkflow:
    """Orchestrates the complete cleanup workflow with safety and logging"""
    
    def __init__(self, log_dir: str = "logs/cleanup"):
        """
        Initialize the cleanup workflow
        
        Args:
            log_dir: Directory for cleanup logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.backup_manager = BackupManager()
        
        # Set up logging
        from src.utils.logging_config import setup_logging
        setup_logging(
            log_dir=str(self.log_dir),
            enable_structured=True
        )
        
        # Create standard logger for general messages
        self.logger = logging.getLogger("cleanup_workflow")
        
        # Create specialized cleanup logger for structured cleanup logging
        self.cleanup_logger = CleanupLogger(name="cleanup_operations")
        
        # Track progress
        self.sources_cleaned = []
        self.cleanup_stats = {}
        
    
    def analyze_source(self, source_id: int, previous_cleaned_file: str = "ai_metrics.csv") -> Dict:
        """
        Run analysis for a specific source
        
        Returns:
            Dictionary with analysis results
        """
        self.logger.info(f"Starting analysis for Source {source_id}")
        
        try:
            # Run analyzer
            analyzer = SourceCleanupAnalyzer(source_id, previous_cleaned_file)
            analyzer.analyze()
            
            # Collect statistics
            stats = {
                'source_id': source_id,
                'source_name': analyzer.source_name,  # The analyzer already gets this from CSV
                'total_records': len(analyzer.source_df),
                'records_to_keep': len(analyzer.records_to_keep),
                'records_to_remove': len(analyzer.records_to_remove),
                'records_to_modify': len(analyzer.records_to_modify),
                'duplicate_groups': len(analyzer.duplicate_groups),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Analysis complete for Source {source_id}: "
                           f"{stats['records_to_keep']} keep, "
                           f"{stats['records_to_remove']} remove, "
                           f"{stats['records_to_modify']} modify")
            
            # Also log structured data
            self.cleanup_logger.log_cleanup_action(
                source_id, 
                "analysis_complete", 
                stats['total_records'],
                f"Keep: {stats['records_to_keep']}, Remove: {stats['records_to_remove']}, Modify: {stats['records_to_modify']}"
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error analyzing source {source_id}: {str(e)}")
            self.cleanup_logger.log_error(source_id, e, "analysis phase")
            raise
    
    def execute_cleanup(self, source_id: int, previous_cleaned_file: str = "ai_metrics.csv",
                       auto_confirm: bool = False) -> str:
        """
        Execute cleanup for a source with backup and confirmation
        
        Args:
            source_id: Source ID to clean
            previous_cleaned_file: Input CSV file
            auto_confirm: Skip confirmation prompt
            
        Returns:
            Path to the new cleaned file
        """
        self.logger.info(f"Starting cleanup execution for Source {source_id}")
        
        # Step 1: Create backup
        backup_path = self.backup_manager.create_backup(
            tag="_cleanup",
            source_id=source_id
        )
        self.logger.info(f"Created backup: {backup_path}")
        
        # Step 2: Run analysis if not already done
        analysis_dir = Path(f"Source Data Cleanup Analysis/Source_{source_id}")
        if not (analysis_dir / "initial_analysis.csv").exists():
            self.logger.info("Running analysis first...")
            self.analyze_source(source_id, previous_cleaned_file)
        
        # Step 3: Load analysis results
        records_to_keep = pd.read_csv(analysis_dir / "records_to_keep.csv") if (analysis_dir / "records_to_keep.csv").exists() else pd.DataFrame()
        records_to_remove = pd.read_csv(analysis_dir / "records_to_remove.csv") if (analysis_dir / "records_to_remove.csv").exists() else pd.DataFrame()
        records_to_modify = pd.read_csv(analysis_dir / "records_to_modify.csv") if (analysis_dir / "records_to_modify.csv").exists() else pd.DataFrame()
        
        # Step 4: Show summary and get confirmation
        print("\n" + "="*60)
        print(f"CLEANUP SUMMARY FOR SOURCE {source_id}")
        print("="*60)
        print(f"Records to keep: {len(records_to_keep)}")
        print(f"Records to remove: {len(records_to_remove)}")
        print(f"Records to modify: {len(records_to_modify)}")
        print(f"\nBackup created at: {backup_path}")
        
        if not auto_confirm:
            response = input("\nProceed with cleanup? (yes/no): ").lower().strip()
            if response != 'yes':
                self.logger.info("Cleanup cancelled by user")
                print("Cleanup cancelled.")
                return previous_cleaned_file
        
        # Step 5: Execute cleanup
        self.logger.info("Executing cleanup operations...")
        
        # Load original data
        df = pd.read_csv(previous_cleaned_file)
        original_count = len(df)
        
        # Log cleanup start with structured data
        self.cleanup_logger.log_cleanup_start(source_id, original_count)
        
        # Remove records marked for removal
        if not records_to_remove.empty:
            remove_ids = records_to_remove['original_id'].tolist()
            df = df[~df.index.isin(remove_ids)]
            self.logger.info(f"Removed {len(remove_ids)} records")
        
        # Apply modifications
        if not records_to_modify.empty:
            for _, mod in records_to_modify.iterrows():
                idx = mod['original_id']
                if idx in df.index:
                    # Update metric type if specified
                    if 'new_metric_type' in mod and pd.notna(mod['new_metric_type']):
                        df.loc[idx, 'metric_type'] = mod['new_metric_type']
                    
                    # Add metadata if available
                    if 'sector' in mod and pd.notna(mod['sector']) and mod['sector']:
                        df.loc[idx, 'sector'] = mod['sector']
                        
            self.logger.info(f"Modified {len(records_to_modify)} records")
        
        # Step 6: Save cleaned data
        output_file = f"ai_metrics_cleaned_source{source_id}.csv"
        df.to_csv(output_file, index=False)
        
        # Log results
        final_count = len(df)
        self.logger.info(f"Cleanup complete: {original_count} -> {final_count} records")
        self.logger.info(f"Saved cleaned data to: {output_file}")
        
        # Log structured cleanup completion
        self.cleanup_logger.log_cleanup_complete(source_id, {
            'original_count': original_count,
            'final_count': final_count,
            'removed': len(records_to_remove),
            'modified': len(records_to_modify),
            'output_file': output_file
        })
        
        # Update tracking
        self.sources_cleaned.append(source_id)
        self.cleanup_stats[source_id] = {
            'original_count': original_count,
            'final_count': final_count,
            'removed': len(records_to_remove),
            'modified': len(records_to_modify),
            'output_file': output_file
        }
        
        print(f"\nCleanup complete!")
        print(f"Original records: {original_count}")
        print(f"Final records: {final_count}")
        print(f"Output saved to: {output_file}")
        
        return output_file
    
    def cleanup_multiple_sources(self, source_ids: List[int], 
                               start_file: str = "ai_metrics.csv",
                               auto_confirm: bool = False):
        """
        Clean multiple sources in sequence
        
        Args:
            source_ids: List of source IDs to clean
            start_file: Initial CSV file
            auto_confirm: Skip confirmation prompts
        """
        current_file = start_file
        
        print(f"\nPlanning to clean {len(source_ids)} sources: {source_ids}")
        
        for source_id in source_ids:
            try:
                print(f"\n{'='*60}")
                print(f"Processing Source {source_id} ({source_ids.index(source_id)+1}/{len(source_ids)})")
                print(f"{'='*60}")
                
                # First analyze
                self.analyze_source(source_id, current_file)
                
                # Then execute if confirmed
                new_file = self.execute_cleanup(source_id, current_file, auto_confirm)
                
                # Update current file for next iteration
                if new_file != current_file:
                    current_file = new_file
                    
            except Exception as e:
                self.logger.error(f"Failed to process source {source_id}: {str(e)}")
                self.cleanup_logger.log_error(source_id, e, "cleanup workflow")
                print(f"\nError processing source {source_id}: {str(e)}")
                
                if not auto_confirm:
                    response = input("Continue with next source? (yes/no): ").lower().strip()
                    if response != 'yes':
                        break
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print summary of all cleanup operations"""
        print("\n" + "="*60)
        print("CLEANUP WORKFLOW SUMMARY")
        print("="*60)
        
        if not self.sources_cleaned:
            print("No sources were cleaned.")
            return
        
        print(f"Sources cleaned: {len(self.sources_cleaned)}")
        
        total_removed = sum(stats['removed'] for stats in self.cleanup_stats.values())
        total_modified = sum(stats['modified'] for stats in self.cleanup_stats.values())
        
        print(f"Total records removed: {total_removed}")
        print(f"Total records modified: {total_modified}")
        
        print("\nDetailed results:")
        for source_id, stats in self.cleanup_stats.items():
            print(f"\n  Source {source_id}:")
            print(f"    Original: {stats['original_count']} records")
            print(f"    Final: {stats['final_count']} records")
            print(f"    Removed: {stats['removed']}")
            print(f"    Modified: {stats['modified']}")
            print(f"    Output: {stats['output_file']}")
        
        # Save summary to file
        summary_file = self.log_dir / f"cleanup_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump({
                'sources_cleaned': self.sources_cleaned,
                'stats': self.cleanup_stats,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\nSummary saved to: {summary_file}")


def main():
    """Main entry point for the cleanup workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run source cleanup workflow")
    parser.add_argument('source_ids', type=int, nargs='+', 
                       help='Source IDs to clean (space-separated)')
    parser.add_argument('--start-file', default='ai_metrics.csv',
                       help='Starting CSV file (default: ai_metrics.csv)')
    parser.add_argument('--auto-confirm', action='store_true',
                       help='Skip confirmation prompts')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only run analysis, don\'t execute cleanup')
    
    args = parser.parse_args()
    
    # Create workflow
    workflow = CleanupWorkflow()
    
    if args.analyze_only:
        # Just analyze
        for source_id in args.source_ids:
            print(f"\nAnalyzing Source {source_id}...")
            stats = workflow.analyze_source(source_id, args.start_file)
            print(f"Analysis complete: {stats['records_to_keep']} keep, "
                  f"{stats['records_to_remove']} remove, "
                  f"{stats['records_to_modify']} modify")
    else:
        # Full cleanup
        workflow.cleanup_multiple_sources(
            args.source_ids,
            args.start_file,
            args.auto_confirm
        )


if __name__ == "__main__":
    # If no arguments provided, show usage
    if len(sys.argv) == 1:
        print("Integrated Source Cleanup Workflow")
        print("\nUsage examples:")
        print("  # Analyze only (no cleanup)")
        print("  python run_source_cleanup.py 3 4 5 --analyze-only")
        print("\n  # Clean single source")
        print("  python run_source_cleanup.py 3")
        print("\n  # Clean multiple sources")
        print("  python run_source_cleanup.py 3 4 5 6")
        print("\n  # Clean with custom start file")
        print("  python run_source_cleanup.py 3 --start-file ai_metrics_cleaned_source1_2_7.csv")
        print("\n  # Auto-confirm all prompts")
        print("  python run_source_cleanup.py 3 4 5 --auto-confirm")
    else:
        main()