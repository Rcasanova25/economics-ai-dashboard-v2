# Source 3 Cleanup Analysis Report

**File**: AI use case.pdf  
**Analyzed**: 2025-07-23T14:54:15.672598  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 68 | 100% |
| Records Kept | 15 | 22.1% |
| Records Removed | 51 | 75.0% |
| Records Modified | 2 | 2.9% |

## Quality Metrics

- **Quality Score**: 22.06%
- **Issues Found**: 53
- **Removal Rate**: 75.0%
- **Modification Rate**: 2.94%

## Duplicate Handling

- **Duplicate Groups**: 17
- **Duplicates Removed**: 51

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 51 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → productivity_metric | 2 |

## Confidence Distribution

- **High (>85%)**: 51 (75.0%)
- **Medium (70-85%)**: 17 (25.0%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
