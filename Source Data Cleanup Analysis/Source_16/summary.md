# Source 16 Cleanup Analysis Report

**File**: wpiea2024231-print-pdf.pdf  
**Analyzed**: 2025-07-23T15:12:56.363797  
**Schema Version**: 1.1

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Records | 244 | 100% |
| Records Kept | 52 | 21.3% |
| Records Removed | 181 | 74.2% |
| Records Modified | 11 | 4.5% |

## Quality Metrics

- **Quality Score**: 21.31%
- **Issues Found**: 192
- **Removal Rate**: 74.18%
- **Modification Rate**: 4.51%

## Duplicate Handling

- **Duplicate Groups**: 67
- **Duplicates Removed**: 177

## Top Removal Reasons

| Reason | Count |
|--------|-------|
| Duplicate record | 168 |
| Citation year extracted as metric value | 12 |
| Financial units should not appear with employment metrics | 1 |

## Modification Types

| Type | Count |
|------|-------|
| general_rate → employment_metric | 9 |
| general_rate → adoption_metric | 1 |
| general_rate → productivity_metric | 1 |

## Confidence Distribution

- **High (>85%)**: 181 (74.2%)
- **Medium (70-85%)**: 63 (25.8%)
- **Low (<70%)**: 0 (0.0%)

## Next Steps

1. Review the CSV files to validate proposed actions
2. Pay special attention to low-confidence decisions
3. Verify that important metrics are preserved
4. Check metric reclassifications make economic sense
5. Approve or modify the cleanup plan before execution
