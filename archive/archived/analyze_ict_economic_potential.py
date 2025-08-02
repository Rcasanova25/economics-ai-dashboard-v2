"""
Quick analysis to see what ICT economic data we actually have
"""
import pandas as pd
from pathlib import Path

# Load cleaned data
extraction_dirs = list(Path('.').glob('extraction_output_*'))
latest_dir = sorted(extraction_dirs)[-1]
cleaned_csv = latest_dir / 'cleaned_data' / 'cleaned_metrics.csv'

df = pd.read_csv(cleaned_csv)

# Filter to ICT
ict_df = df[df['sector'] == 'information_communication_technology']

print(f"Total ICT metrics: {len(ict_df)}")
print("\nMetric type breakdown:")
print(ict_df['metric_type'].value_counts())

print("\nUnit breakdown:")
print(ict_df['unit'].value_counts())

# Look for economic indicators
economic_types = ['ai_investment_amount', 'productivity_improvement', 
                  'job_creation', 'job_displacement', 'energy_consumption']

economic_df = ict_df[ict_df['metric_type'].isin(economic_types)]
print(f"\nEconomic metrics in ICT: {len(economic_df)}")
print(economic_df['metric_type'].value_counts())

# Sample some actual data
if len(economic_df) > 0:
    print("\nSample economic metrics:")
    for idx, row in economic_df.head(10).iterrows():
        print(f"\n- Type: {row['metric_type']}")
        print(f"  Value: {row['value']} {row['unit']}")
        print(f"  Context: {row['context'][:150]}...")

# Check for financial data
financial_df = ict_df[ict_df['unit'].str.contains('usd|dollar|euro|investment', case=False, na=False)]
print(f"\nFinancial metrics in ICT: {len(financial_df)}")

# Look for patterns in context
print("\nSearching contexts for economic terms...")
economic_terms = ['revenue', 'cost', 'investment', 'roi', 'return', 'productivity', 
                  'efficiency', 'savings', 'budget', 'spending', 'economic']

for term in economic_terms:
    count = ict_df['context'].str.contains(term, case=False, na=False).sum()
    if count > 0:
        print(f"- '{term}': {count} mentions")