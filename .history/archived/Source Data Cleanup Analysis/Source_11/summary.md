# Source 11 Cleanup Analysis Report

**File**: gs-new-decade-begins.pdf  
**Analyzed**: 2025-07-23T15:08:35.325270  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 162 | 100% |
| Records Kept | 29 | 17.9% |
| Records Removed | 131 | 80.9% |
| Records Modified | 2 | 1.2% |

## Quality Metrics

- **Quality Score**: 17.9%
- **Issues Found**: 133
- **Removal Rate**: 80.86%
- **Modification Rate**: 1.23%

## Duplicate Handling

- **Duplicate Groups**: 31
- **Duplicates Removed**: 131

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 131 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → employment_metric | 2 |

## Confidence Distribution

- **High (>85%)**: 131 (80.9%)
- **Medium (70-85%)**: 31 (19.1%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
