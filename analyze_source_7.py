"""
Deep analysis of Source 7 to understand its specific data quality issues
Source 7: cost-benefit-analysis-artificial-intelligence-evidence-from-a-field-experiment-on-gpt-4o-1.pdf
"""

import pandas as pd
import numpy as np
from collections import Counter
import json

# Load the data
df = pd.read_csv('data/exports/ai_metrics_20250719.csv')
source_7_df = df[df['source_id'] == 7].copy()

print("=" * 80)
print("SOURCE 7 DEEP ANALYSIS")
print("File: cost-benefit-analysis-artificial-intelligence-evidence-from-a-field-experiment-on-gpt-4o-1.pdf")
print("=" * 80)
print(f"\nTotal records: {len(source_7_df)}")

# 1. Analyze the massive duplicate issue
print("\n1. DUPLICATE ANALYSIS - The 0.0% Problem")
print("-" * 40)

# Check the most common values
value_counts = source_7_df['value'].value_counts().head(20)
print("\nTop 20 most frequent values:")
for value, count in value_counts.items():
    print(f"  {value}: {count} times")

# Focus on the 0.0 percentage issue
zero_pct_df = source_7_df[(source_7_df['value'] == 0.0) & (source_7_df['unit'] == 'percentage')]
print(f"\nTotal 0.0 percentage records: {len(zero_pct_df)}")

# Sample contexts to understand why
print("\nSample contexts for 0.0 percentage records:")
for i, context in enumerate(zero_pct_df['context'].head(10)):
    print(f"\n{i+1}. {context[:150]}...")

# 2. Metric type distribution issues
print("\n\n2. METRIC TYPE ISSUES")
print("-" * 40)

metric_type_counts = source_7_df['metric_type'].value_counts()
print("\nMetric type distribution:")
for metric_type, count in metric_type_counts.items():
    print(f"  {metric_type}: {count} ({count/len(source_7_df)*100:.1f}%)")

# Sample general_rate records to understand classification
general_rate_df = source_7_df[source_7_df['metric_type'] == 'general_rate']
print(f"\nSample 'general_rate' records to understand misclassification:")
sample_general = general_rate_df.sample(min(10, len(general_rate_df)))
for idx, row in sample_general.iterrows():
    print(f"\n  Value: {row['value']} {row['unit']} ({row['year']})")
    print(f"  Context: {row['context'][:100]}...")

# 3. Unit distribution
print("\n\n3. UNIT DISTRIBUTION ANALYSIS")
print("-" * 40)

unit_counts = source_7_df['unit'].value_counts()
print("\nAll units found:")
for unit, count in unit_counts.items():
    print(f"  {unit}: {count}")

# Check energy_unit records
if 'energy_unit' in unit_counts:
    energy_unit_df = source_7_df[source_7_df['unit'] == 'energy_unit']
    print(f"\nRecords with 'energy_unit':")
    for idx, row in energy_unit_df.iterrows():
        print(f"  Value: {row['value']}, Year: {row['year']}, Context: {row['context'][:80]}...")

# 4. Year distribution
print("\n\n4. TEMPORAL ANALYSIS")
print("-" * 40)

year_counts = source_7_df['year'].value_counts().sort_index()
print("\nYear distribution:")
for year, count in year_counts.items():
    print(f"  {year}: {count} records")

# 5. Analyze patterns in the context
print("\n\n5. CONTEXT PATTERN ANALYSIS")
print("-" * 40)

# Look for table patterns
table_indicators = ['|', '(', ')', '%', '0 (0.0%)', 'table', 'figure']
contexts_with_tables = []

for context in source_7_df['context'].dropna():
    if any(indicator in str(context) for indicator in table_indicators):
        contexts_with_tables.append(context)

print(f"\nContexts that might be from tables: {len(contexts_with_tables)}")
print("\nSample table-like contexts:")
for i, context in enumerate(contexts_with_tables[:5]):
    print(f"\n{i+1}. {context[:200]}...")

# 6. Identify specific cleaning needs
print("\n\n6. SPECIFIC CLEANING RECOMMENDATIONS")
print("-" * 40)

cleaning_needs = {
    "Remove table extraction artifacts": len(contexts_with_tables),
    "Reclassify general_rate metrics": metric_type_counts.get('general_rate', 0),
    "Fix energy_unit classifications": unit_counts.get('energy_unit', 0),
    "Handle 0.0% duplicates": len(zero_pct_df),
    "Total records needing attention": len(source_7_df)
}

for issue, count in cleaning_needs.items():
    print(f"  {issue}: {count} records")

# 7. Save detailed findings
findings = {
    "source_id": 7,
    "source_name": "cost-benefit-analysis-artificial-intelligence-evidence-from-a-field-experiment-on-gpt-4o-1.pdf",
    "total_records": int(len(source_7_df)),
    "major_issues": {
        "massive_zero_duplicates": {
            "count": int(len(zero_pct_df)),
            "percentage": float(len(zero_pct_df) / len(source_7_df) * 100),
            "description": "Likely from table parsing where empty cells became 0.0%"
        },
        "general_rate_overuse": {
            "count": int(metric_type_counts.get('general_rate', 0)),
            "percentage": float(metric_type_counts.get('general_rate', 0) / len(source_7_df) * 100),
            "description": "Vague metric classification that needs context-based reclassification"
        },
        "table_extraction_artifacts": {
            "count": int(len(contexts_with_tables)),
            "percentage": float(len(contexts_with_tables) / len(source_7_df) * 100),
            "description": "Context contains table formatting characters"
        },
        "unit_errors": {
            "energy_unit": int(unit_counts.get('energy_unit', 0)),
            "description": "Wrong unit classification - these are actually years from references"
        }
    },
    "value_distribution": {
        "top_10_values": {str(k): int(v) for k, v in value_counts.head(10).items()},
        "unique_values": int(source_7_df['value'].nunique())
    },
    "metric_type_distribution": {k: int(v) for k, v in metric_type_counts.items()},
    "unit_distribution": {k: int(v) for k, v in unit_counts.items()},
    "year_distribution": {int(k): int(v) for k, v in year_counts.items()},
    "cleaning_strategy": [
        "Remove records that are clearly from table headers/formatting",
        "Deduplicate the 0.0% records keeping only meaningful ones",
        "Reclassify general_rate based on context analysis",
        "Fix unit misclassifications"
    ]
}

with open('source_7_analysis.json', 'w') as f:
    json.dump(findings, f, indent=2)

# Also create a CSV version for easier viewing
analysis_summary = pd.DataFrame([
    {"Category": "Total Records", "Count": len(source_7_df), "Percentage": 100.0, "Description": "Total records from Source 7"},
    {"Category": "Zero Duplicates (0.0%)", "Count": len(zero_pct_df), "Percentage": len(zero_pct_df)/len(source_7_df)*100, "Description": "Empty table cells parsed as 0.0%"},
    {"Category": "General Rate Metrics", "Count": metric_type_counts.get('general_rate', 0), "Percentage": metric_type_counts.get('general_rate', 0)/len(source_7_df)*100, "Description": "Vague classification needing reclassification"},
    {"Category": "Table Artifacts", "Count": len(contexts_with_tables), "Percentage": len(contexts_with_tables)/len(source_7_df)*100, "Description": "Contains table formatting characters"},
    {"Category": "Energy Unit Errors", "Count": unit_counts.get('energy_unit', 0), "Percentage": unit_counts.get('energy_unit', 0)/len(source_7_df)*100, "Description": "Years misclassified as energy units"},
])

analysis_summary.to_csv('source_7_analysis_summary.csv', index=False)

# Create detailed sample CSV showing problematic records
sample_problems = []

# Add zero percentage samples
for i, (idx, row) in enumerate(zero_pct_df.head(10).iterrows()):
    sample_problems.append({
        "Problem_Type": "Zero_Duplicate",
        "Record_ID": idx,
        "Value": row['value'],
        "Unit": row['unit'],
        "Year": row['year'],
        "Metric_Type": row['metric_type'],
        "Context_Preview": str(row['context'])[:150] + "..." if len(str(row['context'])) > 150 else str(row['context']),
        "Confidence": row['confidence']
    })

# Add general_rate samples
for i, (idx, row) in enumerate(general_rate_df.head(10).iterrows()):
    sample_problems.append({
        "Problem_Type": "General_Rate",
        "Record_ID": idx,
        "Value": row['value'],
        "Unit": row['unit'],
        "Year": row['year'],
        "Metric_Type": row['metric_type'],
        "Context_Preview": str(row['context'])[:150] + "..." if len(str(row['context'])) > 150 else str(row['context']),
        "Confidence": row['confidence']
    })

# Add energy_unit samples
if 'energy_unit' in unit_counts:
    for idx, row in energy_unit_df.iterrows():
        sample_problems.append({
            "Problem_Type": "Energy_Unit_Error",
            "Record_ID": idx,
            "Value": row['value'],
            "Unit": row['unit'],
            "Year": row['year'],
            "Metric_Type": row['metric_type'],
            "Context_Preview": str(row['context'])[:150] + "..." if len(str(row['context'])) > 150 else str(row['context']),
            "Confidence": row['confidence']
        })

problem_samples_df = pd.DataFrame(sample_problems)
problem_samples_df.to_csv('source_7_problem_samples.csv', index=False)

print("\n\nDetailed analysis saved to: source_7_analysis.json")