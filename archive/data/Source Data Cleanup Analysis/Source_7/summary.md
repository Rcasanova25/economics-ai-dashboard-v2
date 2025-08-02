# Source 7 Cleanup Analysis Report

**File**: cost-benefit-analysis-artificial-intelligence-evidence-from-a-field-experiment-on-gpt-4o-1.pdf  
**Analyzed**: 2025-07-23T16:30:25.991726  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 2472 | 100% |
| Records Kept | 1097 | 44.4% |
| Records Removed | 1366 | 55.3% |
| Records Modified | 9 | 0.4% |

## Quality Metrics

- **Quality Score**: 44.38%
- **Issues Found**: 1375
- **Removal Rate**: 55.26%
- **Modification Rate**: 0.36%

## Duplicate Handling

- **Duplicate Groups**: 129
- **Duplicates Removed**: 2343

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 1351 |
| Citation year extracted as metric value | 8 |
| Financial units should not appear with employment metrics | 7 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate -> employment_metric | 7 |
| general_rate -> adoption_metric | 2 |

## Confidence Distribution

- **High (>85%)**: 2364 (95.6%)
- **Medium (70-85%)**: 108 (4.4%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
