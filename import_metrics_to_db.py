"""
Import Extracted Metrics to Database

This script imports all extracted metrics from JSON files into the SQLite database.
It handles deduplication, validation, and provides a comprehensive import report.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.operations import MetricsDatabase, DatabaseError
from src.database.models import create_tables, get_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MetricsImporter:
    """Handle importing metrics from JSON to database."""
    
    def __init__(self, db_path: str = "data/processed/economics_ai.db"):
        """Initialize importer with database connection."""
        self.db = MetricsDatabase(db_path)
        self.import_stats = {
            'total_files': 0,
            'total_metrics': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0,
            'sources': set()
        }
    
    def validate_metric(self, metric: Dict) -> Tuple[bool, str]:
        """
        Validate a metric before import.
        
        Returns:
            (is_valid, error_message)
        """
        required_fields = ['metric_type', 'value', 'unit']
        
        # Check required fields
        for field in required_fields:
            if field not in metric:
                return False, f"Missing required field: {field}"
        
        # Validate value is numeric
        try:
            float(metric['value'])
        except (ValueError, TypeError):
            return False, f"Invalid value: {metric['value']}"
        
        # Validate year if present
        if 'year' in metric:
            try:
                year = int(metric['year'])
                if year < 2000 or year > 2030:
                    return False, f"Invalid year: {year}"
            except (ValueError, TypeError):
                return False, f"Invalid year format: {metric['year']}"
        
        return True, ""
    
    def import_json_file(self, json_path: Path) -> Dict:
        """Import metrics from a single JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Determine source name
            if 'pdf_name' in data:
                source_name = data['pdf_name']
            elif 'pdf_source' in data.get('metrics', [{}])[0]:
                source_name = data['metrics'][0]['pdf_source']
            else:
                source_name = json_path.stem
            
            # Get metrics from file
            if 'metrics' in data:
                metrics = data['metrics']
            elif isinstance(data, list):
                metrics = data
            else:
                logger.warning(f"No metrics found in {json_path}")
                return {'imported': 0, 'duplicates': 0, 'errors': 0}
            
            # Validate and prepare metrics
            valid_metrics = []
            for metric in metrics:
                is_valid, error = self.validate_metric(metric)
                if is_valid:
                    # Add source information
                    metric['pdf_source'] = source_name
                    valid_metrics.append(metric)
                else:
                    logger.debug(f"Invalid metric in {json_path}: {error}")
                    self.import_stats['errors'] += 1
            
            # Import to database
            if valid_metrics:
                imported, duplicates = self.db.add_metrics_batch(
                    valid_metrics, source_name
                )
                
                # Update source information if available
                if 'organization' in data or 'url' in data:
                    self.db.add_source(
                        name=source_name,
                        organization=data.get('organization'),
                        url=data.get('url'),
                        publication_date=data.get('publication_date')
                    )
                
                self.import_stats['sources'].add(source_name)
                
                return {
                    'imported': imported,
                    'duplicates': duplicates,
                    'errors': len(metrics) - len(valid_metrics)
                }
            
            return {'imported': 0, 'duplicates': 0, 'errors': len(metrics)}
            
        except Exception as e:
            logger.error(f"Error importing {json_path}: {e}")
            return {'imported': 0, 'duplicates': 0, 'errors': 1}
    
    def import_all_metrics(self, directories: List[Path]) -> Dict:
        """Import metrics from all JSON files in specified directories."""
        logger.info("Starting metrics import to database...")
        
        # Find all JSON files
        json_files = []
        for directory in directories:
            if directory.exists():
                json_files.extend(directory.glob("*.json"))
        
        self.import_stats['total_files'] = len(json_files)
        logger.info(f"Found {len(json_files)} JSON files to import")
        
        # Import each file
        for json_file in json_files:
            logger.info(f"Importing: {json_file.name}")
            
            result = self.import_json_file(json_file)
            
            self.import_stats['imported'] += result['imported']
            self.import_stats['duplicates'] += result['duplicates']
            self.import_stats['errors'] += result.get('errors', 0)
            
            # Log progress
            if result['imported'] > 0:
                logger.info(f"  [OK] Imported {result['imported']} metrics")
            if result['duplicates'] > 0:
                logger.info(f"  [SKIP] Skipped {result['duplicates']} duplicates")
        
        self.import_stats['total_metrics'] = (
            self.import_stats['imported'] + 
            self.import_stats['duplicates'] + 
            self.import_stats['errors']
        )
        
        return self.import_stats
    
    def generate_import_report(self) -> str:
        """Generate a detailed import report."""
        # Get database statistics
        db_stats = self.db.get_summary_stats()
        
        report = f"""
=== METRICS IMPORT REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMPORT SUMMARY:
- Files processed: {self.import_stats['total_files']}
- Total metrics found: {self.import_stats['total_metrics']:,}
- Successfully imported: {self.import_stats['imported']:,}
- Duplicates skipped: {self.import_stats['duplicates']:,}
- Errors encountered: {self.import_stats['errors']:,}
- Unique sources: {len(self.import_stats['sources'])}

DATABASE STATISTICS:
- Total sources: {db_stats['total_sources']}
- Total metrics: {db_stats['total_metrics']:,}
- Metric types: {db_stats['metric_types']}
- Year range: {db_stats['year_range'][0]} - {db_stats['year_range'][1]}
- Sectors covered: {db_stats['sectors']}
- Average confidence: {db_stats['avg_confidence']:.2f}

METRICS BY TYPE:
"""
        # Add metrics by type
        for metric_type, count in sorted(db_stats['metrics_by_type'].items()):
            report += f"- {metric_type}: {count:,}\n"
        
        # Add conflict detection summary
        report += "\nCONFLICT DETECTION:\n"
        
        # Check for conflicts in major metrics
        major_types = ['adoption_rate', 'investment', 'productivity']
        for metric_type in major_types:
            for year in range(2023, 2026):
                conflicts = self.db.find_conflicts(metric_type, year)
                if conflicts:
                    report += f"- {metric_type} ({year}): {len(conflicts)} conflicts found\n"
                    for conflict in conflicts[:2]:  # Show first 2
                        report += f"  - {conflict['source1']}: {conflict['value1']} vs "
                        report += f"{conflict['source2']}: {conflict['value2']} "
                        report += f"({conflict['difference_pct']}% difference)\n"
        
        report += "\n" + "="*30 + "\n"
        
        return report


def main():
    """Main import process."""
    # Initialize importer
    importer = MetricsImporter()
    
    # Define directories to import from
    import_dirs = [
        Path("data/processed/extractions"),
        Path("data/processed/converted_metrics")
    ]
    
    # Create database backup
    db_path = Path("data/processed/economics_ai.db")
    if db_path.exists():
        backup_path = db_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        import shutil
        shutil.copy(db_path, backup_path)
        logger.info(f"Created database backup: {backup_path}")
    
    # Run import
    try:
        stats = importer.import_all_metrics(import_dirs)
        
        # Generate and display report
        report = importer.generate_import_report()
        print(report)
        
        # Save report
        report_path = Path("data/processed/import_report.txt")
        with open(report_path, 'w') as f:
            f.write(report)
        logger.info(f"Report saved to: {report_path}")
        
        # Export sample data for verification
        sample_data = importer.db.export_to_dict(limit=10)
        sample_path = Path("data/processed/sample_imported_metrics.json")
        with open(sample_path, 'w') as f:
            json.dump(sample_data, f, indent=2)
        
        logger.info("\n[SUCCESS] Import completed successfully!")
        logger.info(f"[STATS] Database contains {stats['imported']:,} metrics from {len(stats['sources'])} sources")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise


if __name__ == "__main__":
    main()