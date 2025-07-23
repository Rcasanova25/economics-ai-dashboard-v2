# Source 15 Cleanup Analysis Report

**File**: the-economic-impact-of-large-language-models.pdf  
**Analyzed**: 2025-07-23T15:08:41.498329  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 272 | 100% |
| Records Kept | 63 | 23.2% |
| Records Removed | 199 | 73.2% |
| Records Modified | 10 | 3.7% |

## Quality Metrics

- **Quality Score**: 23.16%
- **Issues Found**: 209
- **Removal Rate**: 73.16%
- **Modification Rate**: 3.68%

## Duplicate Handling

- **Duplicate Groups**: 75
- **Duplicates Removed**: 197

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 194 |
| Citation year extracted as metric value | 4 |
| Zero employment with specific numbers in context | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → employment_metric | 10 |

## Confidence Distribution

- **High (>85%)**: 199 (73.2%)
- **Medium (70-85%)**: 73 (26.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
