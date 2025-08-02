# Source 6 Cleanup Analysis Report

**File**: Assessing the Impact of Artificial Intelligence Tools on Employee.pdf  
**Analyzed**: 2025-07-23T15:05:54.155226  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 374 | 100% |
| Records Kept | 100 | 26.7% |
| Records Removed | 264 | 70.6% |
| Records Modified | 10 | 2.7% |

## Quality Metrics

- **Quality Score**: 26.74%
- **Issues Found**: 274
- **Removal Rate**: 70.59%
- **Modification Rate**: 2.67%

## Duplicate Handling

- **Duplicate Groups**: 111
- **Duplicates Removed**: 263

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 263 |
| Financial units should not appear with employment metrics | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → adoption_metric | 4 |
| general_rate → productivity_metric | 3 |
| general_rate → employment_metric | 3 |

## Confidence Distribution

- **High (>85%)**: 264 (70.6%)
- **Medium (70-85%)**: 110 (29.4%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
