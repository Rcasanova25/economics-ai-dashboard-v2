# Source 10 Cleanup Analysis Report

**File**: Generative AI at Work.pdf  
**Analyzed**: 2025-07-23T15:06:00.347887  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 298 | 100% |
| Records Kept | 58 | 19.5% |
| Records Removed | 233 | 78.2% |
| Records Modified | 7 | 2.3% |

## Quality Metrics

- **Quality Score**: 19.46%
- **Issues Found**: 240
- **Removal Rate**: 78.19%
- **Modification Rate**: 2.35%

## Duplicate Handling

- **Duplicate Groups**: 66
- **Duplicates Removed**: 232

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 232 |
| Citation years should not be metric values | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → productivity_metric | 5 |
| general_rate → cost_metric | 1 |
| general_rate → employment_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 233 (78.2%)
- **Medium (70-85%)**: 65 (21.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
