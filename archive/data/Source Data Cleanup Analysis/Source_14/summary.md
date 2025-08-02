# Source 14 Cleanup Analysis Report

**File**: nvidia-cost-trends-ai-inference-at-scale.pdf  
**Analyzed**: 2025-07-23T15:08:39.895157  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 38 | 100% |
| Records Kept | 5 | 13.2% |
| Records Removed | 32 | 84.2% |
| Records Modified | 1 | 2.6% |

## Quality Metrics

- **Quality Score**: 13.16%
- **Issues Found**: 33
- **Removal Rate**: 84.21%
- **Modification Rate**: 2.63%

## Duplicate Handling

- **Duplicate Groups**: 8
- **Duplicates Removed**: 30

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 30 |
| Unexpected unit 'multiple' for cost_metric | 2 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → productivity_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 30 (78.9%)
- **Medium (70-85%)**: 8 (21.1%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
