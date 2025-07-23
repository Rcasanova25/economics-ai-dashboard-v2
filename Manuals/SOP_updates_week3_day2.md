# Standard Operating Procedures - Updates from Week 3 Day 2

## New Procedures to Add to SOP

### 1. Pre-Analysis Testing Protocol
**Before running cleanup on all sources:**
- Test the cleanup template on ONE source first
- Review the results for unexpected patterns
- Look specifically for:
  - Citation years matching value fields
  - Unit-metric type mismatches
  - Zero values with contradicting context
  - Unusually high removal rates (>80% is a red flag)

### 2. Schema-First Development
**Before writing validation logic:**
- Define explicit schemas for each metric type
- Include:
  - Valid and invalid units
  - Acceptable value ranges
  - Required context patterns
  - Known error patterns
- Document domain-specific assumptions

### 3. Root Cause Analysis Protocol
**When encountering test failures:**
- DO NOT apply quick fixes without understanding
- Create minimal reproduction cases
- Use debugging scripts to isolate the issue
- Document the root cause before implementing solution
- Verify the fix addresses the actual problem, not symptoms

### 4. Modular Architecture Requirements
**For reusable data processing tools:**
- Separate validation logic from processing logic
- Create independent modules for:
  - Validation (metric_validator.py)
  - Tracking/metrics (quality_tracker.py)
  - Processing (main analyzer)
- Each module should be independently testable

### 5. Comprehensive Testing Standards
**Minimum test coverage must include:**
- Unit tests for each validation rule
- Integration tests for full pipeline
- Edge cases (empty data, missing fields, malformed input)
- Test data should represent real-world scenarios
- Include tests that SHOULD fail to ensure validation works

### 6. Quality Tracking Requirements
**Every cleanup run must:**
- Record metrics (kept/removed/modified counts)
- Calculate quality scores
- Track removal reasons with counts
- Store historical data for trend analysis
- Export summaries in multiple formats (JSON, MD, CSV)

### 7. Citation Detection Rules
**New validation requirement:**
- If value == year AND context contains citation patterns
- Patterns to check: "(YYYY)", "et al. YYYY", "Author (YYYY)"
- Confidence: 95% for removal
- This prevents publication years from becoming metrics

### 8. Cross-Metric Validation
**Logical consistency checks:**
- Employment metrics cannot have financial units
- Financial metrics cannot have count units
- Adoption rates cannot exceed 100%
- Zero employees is suspicious unless context indicates change metric

### 9. Output File Standards
**Cleanup output structure:**
```
Source_X/
├── initial_analysis.csv (all records with proposed actions)
├── records_to_keep.csv
├── records_to_remove.csv
├── records_to_modify.csv
├── summary.json (machine-readable)
├── summary.md (human-readable)
└── cleanup_summary.txt (legacy format)
```

### 10. Confidence Score Requirements
**All decisions must include confidence scores:**
- High (>0.85): Automated action acceptable
- Medium (0.70-0.85): Review recommended
- Low (<0.70): Manual review required
- Document confidence calculation logic

### 11. Error Handling Standards
**Defensive programming requirements:**
- Check for null/NaN values before processing
- Validate data types match expectations
- Handle file I/O errors gracefully
- Provide meaningful error messages
- Never silently fail

### 12. Performance Monitoring
**Track processing metrics:**
- Time per source
- Memory usage for large sources
- Records processed per second
- Quality score trends over time

## Updates to Existing Procedures

### Enhanced Review Process (Update to Section 2)
**Add to "Decision Point" phase:**
- Check for citation year extractions
- Verify unit-metric type consistency
- Review high-confidence removals for patterns
- Compare quality scores against expected ranges

### Backup Verification (Update to Section 1)
**Add validation after backup:**
- Verify backup file has same record count
- Check MD5 hash matches
- Test restore process on sample data

## New Mantra

> "Test with one before processing all. The cost of fixing one source is minutes; the cost of fixing all sources is hours."

## Red Flags - Updated List

1. ❌ Removal rate >80% (was >50%)
2. ❌ Citation years in metric values
3. ❌ Employment metrics with financial units
4. ❌ Zero values with specific quantities in context
5. ❌ Adoption rates >100%
6. ❌ Quality score <20% for any source

## Required Skills for Operators

1. **Python Debugging** - Must be able to read error messages and tracebacks
2. **Data Analysis** - Understanding of statistical anomalies
3. **Domain Knowledge** - Economics/business metrics understanding
4. **Git Proficiency** - For version control and rollbacks
5. **Testing Mindset** - Think about what could go wrong