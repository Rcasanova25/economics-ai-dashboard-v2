# Source 13 Cleanup Analysis Report

**File**: Mapping-AI-readiness-final.pdf  
**Analyzed**: 2025-07-23T15:08:38.251722  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 474 | 100% |
| Records Kept | 127 | 26.8% |
| Records Removed | 329 | 69.4% |
| Records Modified | 18 | 3.8% |

## Quality Metrics

- **Quality Score**: 26.79%
- **Issues Found**: 347
- **Removal Rate**: 69.41%
- **Modification Rate**: 3.8%

## Duplicate Handling

- **Duplicate Groups**: 147
- **Duplicates Removed**: 327

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 327 |
| Zero employment with specific numbers in context | 1 |
| Invalid unit 'billions_usd' for adoption_metric | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → employment_metric | 12 |
| general_rate → adoption_metric | 3 |
| general_rate → investment_metric | 2 |
| general_rate → productivity_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 329 (69.4%)
- **Medium (70-85%)**: 145 (30.6%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
