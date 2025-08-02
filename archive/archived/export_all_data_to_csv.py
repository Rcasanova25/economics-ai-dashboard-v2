"""
Export All Database Data to CSV Files

This exports every table and metric type to separate CSV files
so you can analyze them in Excel, Tableau, or any tool you prefer.
"""

import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

# Create export directory
export_dir = Path("data/exports")
export_dir.mkdir(exist_ok=True)

# Connect directly to SQLite
db_path = "data/processed/economics_ai.db"
conn = sqlite3.connect(db_path)

print("=" * 80)
print("EXPORTING ALL DATA FROM DATABASE")
print("=" * 80)

# Get all tables
tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql_query(tables_query, conn)
print(f"\nFound {len(tables)} tables in database:")
print(tables['name'].tolist())

# Export each table
for table_name in tables['name']:
    print(f"\nExporting table: {table_name}")
    
    # Get all data from table
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    # Save to CSV
    csv_path = export_dir / f"{table_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"  Exported {len(df)} rows to: {csv_path}")
    print(f"  Columns: {df.columns.tolist()}")

# Special export: All investment-related metrics with full details
print("\n" + "=" * 80)
print("CREATING SPECIALIZED EXPORTS")
print("=" * 80)

# Export all metrics with source information
query = """
SELECT 
    m.*,
    s.name as source_name,
    s.organization,
    s.pdf_path,
    s.publication_date
FROM economic_metrics m
LEFT JOIN data_sources s ON m.source_id = s.id
ORDER BY m.year DESC, m.value DESC
"""

try:
    all_metrics_df = pd.read_sql_query(query, conn)
    csv_path = export_dir / f"all_metrics_with_sources_{datetime.now().strftime('%Y%m%d')}.csv"
    all_metrics_df.to_csv(csv_path, index=False)
    print(f"\nExported complete metrics with sources: {csv_path}")
except Exception as e:
    print(f"Note: Could not create joined export: {e}")

# Export investment-specific data
investment_query = """
SELECT * FROM economic_metrics 
WHERE unit IN ('millions_usd', 'billions_usd', 'trillions_usd')
   OR indicator_type LIKE '%investment%'
   OR indicator_type LIKE '%dollar%'
   OR indicator_type LIKE '%funding%'
   OR indicator_type LIKE '%capital%'
ORDER BY year DESC, value DESC
"""

try:
    investment_df = pd.read_sql_query(investment_query, conn)
    csv_path = export_dir / f"investment_metrics_{datetime.now().strftime('%Y%m%d')}.csv"
    investment_df.to_csv(csv_path, index=False)
    print(f"\nExported investment-specific metrics: {csv_path}")
    print(f"  Found {len(investment_df)} investment-related records")
except Exception as e:
    print(f"Note: Could not create investment export: {e}")

# Create a summary statistics file
print("\n" + "=" * 80)
print("CREATING SUMMARY STATISTICS")
print("=" * 80)

# Try to get summary stats
try:
    summary_stats = {}
    
    # Total metrics
    total_metrics = pd.read_sql_query("SELECT COUNT(*) as count FROM economic_metrics", conn)
    summary_stats['total_metrics'] = total_metrics['count'][0]
    
    # Metrics by type
    metrics_by_type = pd.read_sql_query("""
        SELECT indicator_type, COUNT(*) as count 
        FROM economic_metrics 
        GROUP BY indicator_type 
        ORDER BY count DESC
    """, conn)
    
    # Metrics by year
    metrics_by_year = pd.read_sql_query("""
        SELECT year, COUNT(*) as count 
        FROM economic_metrics 
        GROUP BY year 
        ORDER BY year
    """, conn)
    
    # Save summaries
    metrics_by_type.to_csv(export_dir / "summary_by_type.csv", index=False)
    metrics_by_year.to_csv(export_dir / "summary_by_year.csv", index=False)
    
    print("Created summary files:")
    print("  - summary_by_type.csv")
    print("  - summary_by_year.csv")
    
except Exception as e:
    print(f"Could not create summaries: {e}")

conn.close()

print("\n" + "=" * 80)
print("EXPORT COMPLETE!")
print("=" * 80)
print(f"\nAll files exported to: {export_dir.absolute()}")
print("\nYou can now:")
print("1. Open these CSV files in Excel for analysis")
print("2. Import to Tableau or Power BI for visualization")
print("3. Use Python/R for statistical analysis")
print("\nRecommended next steps:")
print("- Open 'all_metrics_with_sources_[date].csv' to see everything")
print("- Open 'investment_metrics_[date].csv' for investment analysis")
print("- Check summary files to understand data distribution")