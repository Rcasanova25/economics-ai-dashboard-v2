# Source 17 Cleanup Analysis Report

**File**: Acemoglu_Macroeconomics-of-AI_May-2024.pdf  
**Analyzed**: 2025-07-24T14:36:56.777745  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 5356 | 100% |
| Records Kept | 1303 | 24.3% |
| Records Removed | 3999 | 74.7% |
| Records Modified | 54 | 1.0% |

## Quality Metrics

- **Quality Score**: 24.33%
- **Issues Found**: 4053
- **Removal Rate**: 74.66%
- **Modification Rate**: 1.01%

## Duplicate Handling

- **Duplicate Groups**: 874
- **Duplicates Removed**: 4482

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 3959 |
| Citation year extracted as metric value | 20 |
| Financial units should not appear with employment metrics | 13 |
| Invalid unit 'billions_usd' for adoption_metric | 4 |
| Unexpected unit 'multiple' for cost_metric | 2 |
| Zero employment with specific numbers in context | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate -> employment_metric | 24 |
| general_rate -> adoption_metric | 20 |
| general_rate -> productivity_metric | 10 |

## Confidence Distribution

- **High (>85%)**: 4511 (84.2%)
- **Medium (70-85%)**: 845 (15.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
