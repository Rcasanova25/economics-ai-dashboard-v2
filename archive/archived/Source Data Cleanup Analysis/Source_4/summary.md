# Source 4 Cleanup Analysis Report

**File**: ai-and-the-global-economy.pdf  
**Analyzed**: 2025-07-23T14:54:51.772223  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 540 | 100% |
| Records Kept | 97 | 18.0% |
| Records Removed | 433 | 80.2% |
| Records Modified | 10 | 1.9% |

## Quality Metrics

- **Quality Score**: 17.96%
- **Issues Found**: 443
- **Removal Rate**: 80.19%
- **Modification Rate**: 1.85%

## Duplicate Handling

- **Duplicate Groups**: 113
- **Duplicates Removed**: 427

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 427 |
| Financial units should not appear with employment metrics | 3 |
| Invalid unit 'billions_usd' for adoption_metric | 2 |
| Citation years should not be metric values | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → adoption_metric | 4 |
| general_rate → productivity_metric | 3 |
| general_rate → employment_metric | 2 |
| general_rate → cost_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 433 (80.2%)
- **Medium (70-85%)**: 107 (19.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
