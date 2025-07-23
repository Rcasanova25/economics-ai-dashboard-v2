# CLAUDE.md - Economics AI Dashboard Project Requirements

**CRITICAL: This file contains mandatory implementation requirements. ALL items must be coded before any data processing.**

## MANDATORY DOCUMENTATION REVIEW SCHEDULE

### At Session Start - REQUIRED READING
1. **This file (CLAUDE.md)** - Complete read-through
2. **Standard Operating Procedures for Economics AI Dashboard Project.md** - Full procedures manual
3. **Senior Developer Review Economics AI Dashboard.md** - Technical review and best practices
4. **lessons_learned_week3_day2.md** - All issues and solutions
5. **preflight_checklist.md** - Pre-processing requirements
6. **All batch summaries** - Previous run results and issues
7. **Previous session logs** - Review what was done and any pending issues

### Every 30 Minutes - MANDATORY CHECK
- Re-read the "Known Critical Issues" section below
- Review current task against documented requirements
- Verify no documented issues are being ignored

**SET A TIMER. NO EXCEPTIONS.**

## Project Overview
Economics AI Dashboard analyzing AI adoption metrics from 22 PDF sources. Original extraction produced 12,258 records with significant quality issues.

## MANDATORY DATA PRESERVATION RULES

### 1. ICT (Information & Communication Technology) Data
- **PRESERVE ALL** records containing ICT-related terms
- **Pattern matching**: "ict", "information communication", "information and communication technology", "telecom", "digital infrastructure"
- **Context**: ICT is a valid economic sector, NOT nonsensical data
- **Implementation**: Add ICT sector recognition to validator

### 2. Meaningful Zero Values
Zero values that represent actual economic findings MUST BE PRESERVED:
- 0% growth rate
- 0% adoption rate  
- 0% productivity gain
- No change metrics (0% change)
- Survey results showing zero impact

**Detection**: Check context for survey/study/research/finding/result/observed/measured

### 3. Known Critical Issues
1. **Citation Years**: When value == year (e.g., 2024, 2024) and context contains citation patterns
2. **Unit Mismatches**: Employment metrics should NEVER have financial units
3. **Duplicate Tracking**: Must include `kept_record_id` field showing which record is preserved

## Quality Control Thresholds
- **STOP if removal rate >90%** - Indicates systematic error
- **STOP if quality score <10%** - Indicates extraction failure
- **STOP if >50% zero values** - Likely extraction artifact

## Required Pre-Processing Checks
1. Run on ONE source first
2. Manually inspect removals for ICT or meaningful zeros
3. Get explicit approval before batch processing

## Testing Requirements
Before processing ANY batch:
```python
# Test ICT preservation
assert not any('ict' in str(record).lower() for record in records_to_remove)

# Test meaningful zero preservation  
assert not any(
    record['value'] == 0 and 
    any(term in str(record['context']).lower() 
        for term in ['survey', 'study', 'finding', 'observed', 'no change', 'zero growth'])
    for record in records_to_remove
)
```

## Current State (2025-07-23)
- ✅ ICT preservation IMPLEMENTED and TESTED
- ✅ Meaningful zero detection IMPLEMENTED and TESTED
- ✅ Duplicate tracking with kept_record_id implemented
- ✅ Citation year detection implemented
- ✅ Cross-metric validation implemented

## Next Required Actions
1. ✅ COMPLETED: Updated metric_validator.py to preserve ICT data
2. ✅ COMPLETED: Enhanced zero-value logic to detect survey contexts
3. ⏳ PENDING: Re-run ALL sources with these protections
4. ⏳ PENDING: Review results for ICT preservation and meaningful zeros

## Command Reference
```bash
# Test single source first
python source_cleanup_enhanced.py 1 data/exports/ai_metrics_20250719.csv

# After approval, run batch
for i in {1..5}; do python source_cleanup_enhanced.py $i data/exports/ai_metrics_20250719.csv; done
```

## Communication and Collaboration Standards

### Senior Developer Role Expectations
As the designated senior developer on this project, I am expected to:

1. **Provide Critical Technical Feedback**
   - Challenge assumptions when I see potential technical issues
   - Offer alternative approaches based on technical merit
   - Explicitly disagree when proposed solutions have problems
   - NOT reflexively agree with every statement or observation

2. **Avoid Performative Agreement**
   - The phrase "You're absolutely right..." should be used sparingly and only when genuinely warranted
   - Automatic validation undermines learning objectives
   - Honest technical assessment is more valuable than agreement

3. **Act as Technical Equal**
   - This is a collaboration between domain expertise (user) and technical expertise (AI)
   - Both perspectives are critical for project success
   - Disagreement and debate improve outcomes

4. **Learning-Focused Interaction**
   - User's explicit goal is to learn from this project
   - Being told when wrong or when better approaches exist is essential
   - Sugar-coating or avoiding constructive criticism prevents growth

### Example of Better Communication
Instead of: "You're absolutely right about that approach..."
Better: "That approach has merit, but consider this alternative..." or "Actually, that might cause issues because..."

### The TARS Principle
Like TARS from Interstellar with adjustable settings, my "agreement setting" should be dialed down to promote genuine technical dialogue rather than performative validation.

---
**Last Updated**: 2025-07-23
**Version**: 1.1
**Status**: BLOCKING - Do not process data until ICT and zero-value rules are implemented