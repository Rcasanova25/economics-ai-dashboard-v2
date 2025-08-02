# Source 1 Cleanup Analysis Report

**File**: Affects of GenAI on Highskilled Work.pdf  
**Analyzed**: 2025-07-23T14:49:48.161118  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 334 | 100% |
| Records Kept | 80 | 24.0% |
| Records Removed | 249 | 74.6% |
| Records Modified | 5 | 1.5% |

## Quality Metrics

- **Quality Score**: 23.95%
- **Issues Found**: 254
- **Removal Rate**: 74.55%
- **Modification Rate**: 1.5%

## Duplicate Handling

- **Duplicate Groups**: 87
- **Duplicates Removed**: 247

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 244 |
| Citation year extracted as metric value | 4 |
| Invalid unit 'billions_usd' for adoption_metric | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → adoption_metric | 3 |
| general_rate → employment_metric | 1 |
| general_rate → productivity_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 249 (74.6%)
- **Medium (70-85%)**: 85 (25.4%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
