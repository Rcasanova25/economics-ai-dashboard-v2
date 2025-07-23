# Source 2 Cleanup Analysis Report

**File**: AI strategy.pdf  
**Analyzed**: 2025-07-23T13:45:27.261751  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 420 | 100% |
| Records Kept | 71 | 16.9% |
| Records Removed | 336 | 80.0% |
| Records Modified | 13 | 3.1% |

## Quality Metrics

- **Quality Score**: 16.9%
- **Issues Found**: 349
- **Removal Rate**: 80.0%
- **Modification Rate**: 3.1%

## Duplicate Handling

- **Duplicate Groups**: 84
- **Duplicates Removed**: 336

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 336 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → adoption_metric | 11 |
| general_rate → employment_metric | 1 |
| general_rate → productivity_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 336 (80.0%)
- **Medium (70-85%)**: 84 (20.0%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
