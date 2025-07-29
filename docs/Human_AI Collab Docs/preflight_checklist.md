# Pre-Flight Checklist for Data Processing

**STOP - DO NOT PROCEED WITHOUT COMPLETING ALL ITEMS**

## Before ANY Batch Processing

### 1. Review Documentation
- [ ] Read `CLAUDE.md`
- [ ] Read `lessons_learned_week3_day2.md`
- [ ] Read all batch summaries from previous runs
- [ ] Check for any updates to Standard Operating Procedures
- [ ] Review documented red flags and issues

### 2. Verify Known Issues Are Implemented
- [ ] ICT (Information & Communication Technology) sector preservation
- [ ] Meaningful zero value detection (0% growth rates from surveys)
- [ ] Citation year detection (value = year)
- [ ] Cross-metric validation (employment ≠ financial units)
- [ ] Unit standardization checks

### 3. Code Review
- [ ] All documented issues have corresponding code changes
- [ ] Test coverage exists for each known issue
- [ ] Validation schema reflects current requirements

### 4. Test Run Protocol
- [ ] Run on ONE source first
- [ ] Manually review 10 samples from each category:
  - [ ] Records to keep
  - [ ] Records to remove  
  - [ ] Records to modify
- [ ] Verify no ICT data in removal list
- [ ] Verify no meaningful zeros in removal list
- [ ] Check duplicate tracking includes kept_record_id

### 5. Approval Gates
- [ ] Test source results reviewed by user
- [ ] Explicit approval received for batch processing
- [ ] Success criteria clearly defined

### 6. During Processing
- [ ] Monitor for anomalies (>80% removal rate)
- [ ] Check quality scores against expectations
- [ ] Stop if unexpected patterns emerge

### 7. Post-Processing
- [ ] Generate summary report
- [ ] Document any new issues found
- [ ] Update this checklist with new items

## Red Flags - STOP Processing If:
- Removal rate >80% on any source
- ICT/technology terms found in removals
- Zero values with survey/study context in removals  
- Quality score <20% without known cause
- Any validation logic not matching documentation

## Success Criteria (Must Define Before Processing)
- [ ] Expected removal rate: ____%
- [ ] Expected quality score range: ____% - ____%
- [ ] ICT data preservation verified: Yes/No
- [ ] Meaningful zeros preserved: Yes/No
- [ ] No citation years in kept records: Yes/No

## Required Files Before Start:
- [ ] metric_validator.py (with ICT and zero protections)
- [ ] metric_validation_schema.py (updated for current requirements)
- [ ] quality_tracker.py (functioning)
- [ ] source_cleanup_enhanced.py (with all protections)
- [ ] All test files passing

**By proceeding past this checklist, you confirm all items are complete.**

Date: _____________
Reviewed by: _____________