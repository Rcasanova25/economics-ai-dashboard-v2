# Success Criteria for Test Source Processing

## Expected Outcomes Based on Previous Analysis

### Removal Rates by Source (Historical)
- Sources 1-5: Average 78.2% removal
- Sources 6-10: Average 89.4% removal  
- Sources 11-15: Average 69.9% removal
- Sources 16-22: Average 83.1% removal
- **Overall Average: 82.7% removal**

### Expected Quality Scores
- Batch 1: 22.4% average
- Batch 2: 16.7% average
- Batch 3: 23.6% average
- Batch 4: 32.4% average (skewed by small sources)
- **Overall Average: 23.8%**

## Success Criteria for Test Run

### Primary Success Metrics
1. **ICT Data Preservation**
   - ✅ Success: Any record with ICT/telecom/digital infrastructure context is KEPT
   - ❌ Failure: ICT data found in records_to_remove.csv
   
2. **Meaningful Zero Preservation**
   - ✅ Success: Zero values with survey/study/research context are KEPT
   - ❌ Failure: Meaningful zeros found in records_to_remove.csv

3. **Citation Year Detection**
   - ✅ Success: No records where value=year with citation context in records_to_keep.csv
   - ❌ Failure: Citation years preserved as metrics

4. **Cross-Metric Validation**
   - ✅ Success: No employment metrics with financial units
   - ❌ Failure: Unit-metric mismatches in kept records

### Secondary Success Metrics
1. **Removal Rate**: 60-90% (consistent with historical data)
2. **Quality Score**: 15-35% (consistent with historical range)
3. **Duplicate Detection**: All duplicates have kept_record_id reference
4. **Confidence Scores**: All decisions include confidence 0.0-1.0

### Warning Thresholds
- ⚠️ Removal rate >95%: Possible over-removal
- ⚠️ Removal rate <50%: Possible under-removal  
- ⚠️ Quality score <10%: Major data quality issues
- ⚠️ Zero confidence scores: Validation logic error

### Test Source Selection
Choose a source that:
1. Previously showed ICT data (check batch summaries)
2. Has moderate size (100-500 records)
3. Had quality issues in previous run
4. Known to have survey/research data

### Verification Steps
1. Run analyzer on selected source
2. Check records_to_keep.csv for:
   - At least one "ICT sector data - preserved" reason
   - Zero values with survey context preserved
3. Check records_to_remove.csv for:
   - No ICT-related contexts
   - No meaningful zeros
   - Citation years properly identified
4. Review summary statistics against thresholds

## Decision Matrix

| Outcome | Action |
|---------|--------|
| All primary metrics pass | Proceed with batch processing |
| Any primary metric fails | Stop and fix issue |
| Warning threshold hit | Review samples before proceeding |
| Multiple warnings | Investigate root cause |