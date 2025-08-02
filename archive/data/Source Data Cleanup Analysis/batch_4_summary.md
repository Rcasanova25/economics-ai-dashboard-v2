# Batch 4 Analysis Summary (Sources 16-22)

**Date**: July 23, 2025  
**Analyzer Version**: Enhanced with kept_record_id tracking for duplicates

## Overview

| Source | Name | Total | Keep | Remove | Modify | Quality Score |
|--------|------|-------|------|--------|--------|---------------|
| 16 | wpiea2024231-print-pdf.pdf | 244 | 52 | 181 | 11 | 21.3% |
| 17 | Acemoglu_Macroeconomics-of-AI_May-2024.pdf | 5,356 | 791 | 4,510 | 55 | 14.8% |
| 18 | Artificial Intelligence, Scientific Discovery, and Product Innovation.pdf | 202 | 53 | 149 | 0 | 26.2% |
| 19 | Economic_Impacts_Paper.pdf | 118 | 30 | 88 | 0 | 25.4% |
| 20 | Machines of mind_ The case for an AI-powered productivity boom.pdf | 36 | 14 | 22 | 0 | 38.9% |
| 21 | oecd-artificial-intelligence-review-2025.pdf | 2 | 1 | 1 | 0 | 50.0% |
| 22 | The Productivity Puzzle_ AI, Technology Adoption and the Workforce _ Richmond Fed.pdf | 4 | 2 | 2 | 0 | 50.0% |

## Key Findings

### Batch Statistics
- **Total Records**: 5,962
- **Records to Keep**: 943 (15.8%)
- **Records to Remove**: 4,953 (83.1%)
- **Records to Modify**: 66 (1.1%)
- **Average Quality Score**: 32.4%*

*Note: Sources 21-22 have very few records, skewing the average upward

### Notable Patterns

1. **Source 17 (Acemoglu)** - Largest dataset:
   - 5,356 records (43.5% of all data)
   - 84.2% duplicates removed
   - 20.1% zero values
   - Contains multiple problematic units

2. **Sources 21-22** - Minimal data:
   - Only 2-4 records each
   - 50% quality scores due to small sample size

3. **Unit Issues Persist**:
   - Energy units, CO2 emissions, "unknown", "multiple"
   - Concentrated in larger sources

## Complete Dataset Analysis (Sources 1-22)

### Final Statistics
- **Total Records**: 12,258
- **Records to Keep**: 1,959 (16.0%)
- **Records to Remove**: 10,141 (82.7%)
- **Records to Modify**: 158 (1.3%)

### Duplicate Analysis by Batch
| Batch | Sources | Total Records | Duplicates | Duplicate Rate |
|-------|---------|---------------|------------|----------------|
| 1 | 1-5 | 1,488 | 1,163 | 78.2% |
| 2 | 6-10 | 3,404 | 3,043 | 89.4% |
| 3 | 11-15 | 1,404 | 982 | 69.9% |
| 4 | 16-22 | 5,962 | 4,953 | 83.1% |
| **Total** | **1-22** | **12,258** | **10,141** | **82.7%** |

### Quality Score Trends
```
Batch 1: 22.4%
Batch 2: 16.7%  
Batch 3: 23.6%
Batch 4: 32.4% (skewed by tiny sources)
Overall: 23.8%
```

## Key Insights

1. **Massive Duplicate Problem**: 82.7% of all records are duplicates
2. **Source 17 Dominates**: Contains 43.5% of all data
3. **Consistent Issues**:
   - Citation years extracted as metrics
   - Zero values (especially in duplicates)
   - Problematic units (energy, CO2, unknown)
   - Vague metric classifications

4. **Data Quality Varies Widely**:
   - Best: Source 12 (HAI Index) - 36.5%
   - Worst: Source 8 - 5.0%
   - Average: 23.8%

## Recommendations

1. **Execute Duplicate Removal**: With 82.7% duplicates, this is critical
2. **Review Large Sources**: Especially Source 17 with 5,356 records
3. **Address Unit Issues**: Standardize or remove problematic units
4. **Consider Re-extraction**: For sources with <10% quality scores

## Next Steps

1. Review duplicate patterns and confirm removal strategy
2. Execute cleanup to create deduplicated dataset
3. Perform deeper analysis on clean data with proper context