# Source 17 Cleanup Analysis Report

**File**: Acemoglu_Macroeconomics-of-AI_May-2024.pdf  
**Analyzed**: 2025-07-23T15:12:58.386813  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 5356 | 100% |
| Records Kept | 791 | 14.8% |
| Records Removed | 4510 | 84.2% |
| Records Modified | 55 | 1.0% |

## Quality Metrics

- **Quality Score**: 14.77%
- **Issues Found**: 4565
- **Removal Rate**: 84.2%
- **Modification Rate**: 1.03%

## Duplicate Handling

- **Duplicate Groups**: 874
- **Duplicates Removed**: 4482

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 4470 |
| Citation year extracted as metric value | 20 |
| Financial units should not appear with employment metrics | 13 |
| Invalid unit 'billions_usd' for adoption_metric | 4 |
| Unexpected unit 'multiple' for cost_metric | 2 |
| Zero employment with specific numbers in context | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → employment_metric | 25 |
| general_rate → adoption_metric | 20 |
| general_rate → productivity_metric | 10 |

## Confidence Distribution

- **High (>85%)**: 4508 (84.2%)
- **Medium (70-85%)**: 848 (15.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
