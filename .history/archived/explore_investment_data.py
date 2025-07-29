"""
Investment Data Explorer

This tool helps you understand the investment data before creating visualizations.
As an economist, you need to see patterns, outliers, and the story in the data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.operations import MetricsDatabase

# Initialize database
db = MetricsDatabase()

print("=" * 80)
print("INVESTMENT DATA EXPLORATION TOOL")
print("=" * 80)

# Get all investment-related metrics
investment_metrics = db.get_metrics_by_type('investment')
ai_investment_metrics = db.get_metrics_by_type('ai_investment')
dollar_metrics = db.get_metrics_by_type('dollar_amounts')

# Combine all
all_metrics = investment_metrics + ai_investment_metrics + dollar_metrics

print(f"\nTotal investment-related metrics: {len(all_metrics)}")
print(f"- 'investment' type: {len(investment_metrics)}")
print(f"- 'ai_investment' type: {len(ai_investment_metrics)}")
print(f"- 'dollar_amounts' type: {len(dollar_metrics)}")

# Convert to DataFrame for analysis
df = pd.DataFrame(all_metrics)

print("\n" + "=" * 80)
print("1. DATA OVERVIEW")
print("=" * 80)

print("\nColumns in data:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nFirst few rows to understand structure:")
print(df.head())

if 'metric_type' in df.columns:
    print("\nUnique metric types:")
    print(df['metric_type'].value_counts())

print("\nUnique units:")
print(df['unit'].value_counts())

print("\n" + "=" * 80)
print("2. INVESTMENT METRICS ONLY (millions/billions USD)")
print("=" * 80)

# Filter for actual investment data
investment_df = df[df['unit'].isin(['millions_usd', 'billions_usd'])].copy()
print(f"\nFound {len(investment_df)} metrics with USD values")

if len(investment_df) > 0:
    # Normalize to billions for comparison
    investment_df['value_billions'] = investment_df.apply(
        lambda row: row['value'] / 1000 if row['unit'] == 'millions_usd' else row['value'],
        axis=1
    )
    
    print("\nYear distribution:")
    print(investment_df['year'].value_counts().sort_index())
    
    print("\nValue statistics (in billions USD):")
    print(investment_df['value_billions'].describe())
    
    print("\nTop 10 largest investments:")
    top_investments = investment_df.nlargest(10, 'value_billions')[
        ['year', 'value_billions', 'source', 'context']
    ]
    for idx, row in top_investments.iterrows():
        print(f"\n{row['year']}: ${row['value_billions']:.1f}B")
        print(f"  Source: {row['source'][:50]}")
        if pd.notna(row['context']):
            print(f"  Context: {row['context'][:100]}...")
    
    print("\n" + "=" * 80)
    print("3. INVESTMENT BY SOURCE")
    print("=" * 80)
    
    # Group by source
    by_source = investment_df.groupby('source').agg({
        'value_billions': ['sum', 'count', 'mean'],
        'year': ['min', 'max']
    }).round(2)
    
    print("\nInvestment metrics by source:")
    print(by_source)
    
    print("\n" + "=" * 80)
    print("4. INVESTMENT TRENDS BY YEAR")
    print("=" * 80)
    
    # Group by year
    by_year = investment_df.groupby('year').agg({
        'value_billions': ['sum', 'count', 'mean', 'std']
    }).round(2)
    
    print("\nYearly investment totals:")
    print(by_year)
    
    # Calculate YoY growth
    yearly_totals = investment_df.groupby('year')['value_billions'].sum().sort_index()
    yoy_growth = yearly_totals.pct_change() * 100
    
    print("\nYear-over-Year growth rates:")
    for year in yoy_growth.index[1:]:
        if not np.isnan(yoy_growth[year]):
            print(f"{year}: {yoy_growth[year]:.1f}%")

print("\n" + "=" * 80)
print("5. DATA QUALITY ISSUES")
print("=" * 80)

# Check for missing values
print("\nMissing values per column:")
print(df.isnull().sum())

# Check for outliers in investment data
if len(investment_df) > 0:
    Q1 = investment_df['value_billions'].quantile(0.25)
    Q3 = investment_df['value_billions'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = investment_df[
        (investment_df['value_billions'] < Q1 - 1.5 * IQR) | 
        (investment_df['value_billions'] > Q3 + 1.5 * IQR)
    ]
    
    print(f"\nPotential outliers (using IQR method): {len(outliers)}")
    if len(outliers) > 0:
        print("Outlier examples:")
        for idx, row in outliers.head(5).iterrows():
            print(f"  ${row['value_billions']:.1f}B ({row['year']}) - {row['source'][:40]}")

print("\n" + "=" * 80)
print("6. CONTEXT ANALYSIS")
print("=" * 80)

# Look for specific investment types in context
if 'context' in df.columns:
    contexts = df['context'].dropna()
    
    investment_types = {
        'Infrastructure': ['infrastructure', 'data center', 'compute', 'gpu'],
        'R&D': ['research', 'r&d', 'development', 'innovation'],
        'Venture Capital': ['venture', 'vc', 'startup', 'funding round'],
        'Corporate': ['corporate', 'enterprise', 'company investment'],
        'Government': ['government', 'public', 'national', 'federal']
    }
    
    print("\nInvestment type mentions in context:")
    for inv_type, keywords in investment_types.items():
        count = sum(1 for context in contexts if any(kw in context.lower() for kw in keywords))
        print(f"  {inv_type}: {count} mentions")

print("\n" + "=" * 80)
print("7. RECOMMENDATIONS FOR VISUALIZATION")
print("=" * 80)

print("""
Based on this analysis, consider:

1. FOCUS ON RELIABLE DATA:
   - Filter for metrics with high confidence scores
   - Use data from authoritative sources (Stanford HAI, McKinsey, etc.)
   - Handle outliers appropriately

2. TELL THE STORY:
   - Show investment growth trajectory (if clear trend exists)
   - Highlight major investment milestones
   - Compare different types of AI investment

3. ADD CONTEXT:
   - Include annotations for major events
   - Show investment as % of GDP or tech sector
   - Compare to other technology waves

4. BE TRANSPARENT:
   - Show data sources clearly
   - Indicate confidence levels
   - Note any data limitations
""")

# Save cleaned data for further analysis
if len(investment_df) > 0:
    output_file = "data/processed/investment_data_cleaned.csv"
    investment_df.to_csv(output_file, index=False)
    print(f"\nCleaned investment data saved to: {output_file}")

print("\n" + "=" * 80)