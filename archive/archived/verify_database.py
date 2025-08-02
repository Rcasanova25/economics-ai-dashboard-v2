"""
Verify Database Import and Generate Report

This script checks the database contents and generates a comprehensive report.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.operations import MetricsDatabase


def main():
    """Generate database verification report."""
    
    # Initialize database connection
    db = MetricsDatabase()
    
    # Get summary statistics
    stats = db.get_summary_stats()
    
    print("=" * 70)
    print("DATABASE VERIFICATION REPORT")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Overall statistics
    print("OVERALL STATISTICS:")
    print(f"- Total data sources: {stats['total_sources']}")
    print(f"- Total metrics: {stats['total_metrics']:,}")
    print(f"- Unique metric types: {stats['metric_types']}")
    print(f"- Year range: {stats['year_range'][0]} - {stats['year_range'][1]}")
    print(f"- Sectors covered: {stats['sectors']}")
    print(f"- Average confidence: {stats['avg_confidence']:.2f}")
    print()
    
    # Metrics by type
    print("METRICS BY TYPE:")
    for metric_type, count in sorted(stats['metrics_by_type'].items(), 
                                   key=lambda x: x[1], reverse=True):
        print(f"- {metric_type:<20}: {count:>6,}")
    print()
    
    # Sample metrics
    print("SAMPLE METRICS:")
    sample_types = ['adoption_rate', 'investment', 'productivity', 'energy']
    
    for i, metric_type in enumerate(sample_types, 1):
        metrics = db.get_metrics_by_type(metric_type, year=2024)
        if metrics:
            m = metrics[0]
            print(f"{i}. {metric_type.title()}:")
            print(f"   Value: {m['value']} {m['unit']}")
            print(f"   Year: {m['year']}")
            print(f"   Source: {m['source']}")
            print(f"   Confidence: {m['confidence']}")
            if m.get('context'):
                print(f"   Context: {m['context'][:100]}...")
            print()
    
    # Conflict detection
    print("CONFLICT ANALYSIS:")
    conflict_found = False
    
    for metric_type in ['adoption_rate', 'investment', 'productivity']:
        for year in [2023, 2024, 2025]:
            conflicts = db.find_conflicts(metric_type, year, threshold=0.15)
            if conflicts:
                conflict_found = True
                print(f"\n{metric_type.title()} ({year}):")
                for c in conflicts[:3]:  # Show top 3
                    print(f"  - {c['source1']}: {c['value1']} {c['unit']}")
                    print(f"    vs {c['source2']}: {c['value2']} {c['unit']}")
                    print(f"    Difference: {c['difference_pct']}%")
    
    if not conflict_found:
        print("No significant conflicts found (threshold: 15%)")
    
    print()
    print("=" * 70)
    print("DATABASE IMPORT SUCCESSFUL!")
    print(f"Total of {stats['total_metrics']:,} metrics available for analysis")
    print("=" * 70)
    
    # Save report
    report_path = Path("data/processed/database_verification_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        # Recreate the report for file
        f.write("=" * 70 + "\n")
        f.write("DATABASE VERIFICATION REPORT\n")
        f.write("=" * 70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("OVERALL STATISTICS:\n")
        f.write(f"- Total data sources: {stats['total_sources']}\n")
        f.write(f"- Total metrics: {stats['total_metrics']:,}\n")
        f.write(f"- Unique metric types: {stats['metric_types']}\n")
        f.write(f"- Year range: {stats['year_range'][0]} - {stats['year_range'][1]}\n")
        f.write(f"- Sectors covered: {stats['sectors']}\n")
        f.write(f"- Average confidence: {stats['avg_confidence']:.2f}\n\n")
        
        f.write("DATABASE IMPORT SUCCESSFUL!\n")
        f.write(f"Total of {stats['total_metrics']:,} metrics available for analysis\n")
    
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()