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

## Current State (2025-07-24) - MAJOR PROJECT PIVOT

### What We Built
- ✅ Complete extraction system rewrite with schema validation
- ✅ Successfully extracted 12,858 metrics from 23 PDFs
- ✅ Cleaned data with only 4.1% removal rate
- ✅ Delivered ICT AI Adoption Dashboard as Phase 1

### What We Learned - THE HARD TRUTH
After perfect technical execution, data analysis revealed:
- **47% unknown sector** - Context windows too small
- **64% generic counts** - "Company X uses AI" not economic metrics
- **0.7% productivity data** - Almost no real economic impact metrics
- **PDFs wrong for purpose** - Academic papers discuss AI conceptually

### The Strategic Pivot
**Original Goal**: Economics of AI Dashboard (all sectors, all metrics)
**Reality Check**: "You're trying to build a Ferrari dashboard on a Yugo dataset"
**New Goal**: ICT AI Adoption Dashboard (focused, honest, achievable)

## Critical Lessons for Future Work

### 1. Data Source Selection
**STOP** using academic PDFs for economic analysis. **START** with:
- Industry analyst reports (Gartner, IDC, Forrester)
- Company financial reports
- Government economic data
- Structured survey results

### 2. Validation Before Building
**ALWAYS**:
1. Manually read 2-3 source documents first
2. Confirm they contain the metrics you need
3. Build proof-of-concept on subset
4. Reality check with stakeholder

### 3. Technical Success ≠ Project Success
Our extraction system worked perfectly but extracted the wrong type of data. Always ask: "Is this data useful for the stated goal?"

## Next Phase Requirements
1. ✅ COMPLETED: ICT Adoption Dashboard (Phase 1) 
2. 🔄 NEEDED: New data sources with actual economic metrics
3. 🔄 NEEDED: Narrower scope (single sector, specific metrics)
4. 🔄 NEEDED: Partnership with data providers

## Command Reference
```bash
# Test single source first
python source_cleanup_enhanced.py 1 data/exports/ai_metrics_20250719.csv

# After approval, run batch
for i in {1..5}; do python source_cleanup_enhanced.py $i data/exports/ai_metrics_20250719.csv; done
```

## Holistic Data Quality Approach

### IMPORTANT: Focus on Overall Data Quality
While specific issues like ICT preservation and meaningful zeros are important, they are just examples of a broader data quality mission. The real goal is:

1. **Cross-Sector Analysis** - Enable meaningful comparisons across ALL sectors (Manufacturing, Healthcare, Financial, etc.)
2. **Data Integrity** - Every metric should make economic sense in context
3. **Continuous Improvement** - Each iteration teaches us new patterns to handle
4. **Celebrate Progress** - Extraction improved from 82.7% duplicates to proper deduplication!

### New Issues Discovered (2025-01-24)
- Numbers in compound terms extracted as metrics (COVID-19 → 19, Fortune 500 → 500)
- This is GOOD - we're learning and improving the system

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

## The Power of Honest Collaboration

### What Worked
1. **Brutal Honesty** - "Ferrari on Yugo dataset" feedback enabled strategic pivot
2. **Fast Pivot** - Recognized data limitations and adjusted scope within same session
3. **Delivered Value** - ICT Adoption Dashboard is real and useful, if limited
4. **Learning Focus** - Both parties learned from failure and adjusted

### What Didn't Work Initially
1. **Reflexive Agreement** - Early "You're absolutely right" responses delayed recognition of issues
2. **Scope Creep** - Trying to analyze all sectors from 22 sources
3. **Assumption Validation** - Assumed PDFs had economic data without checking

### For Future Sessions
- Question assumptions early and often
- Prototype on small samples first
- Celebrate honest pivots over stubborn persistence
- Deliver something real over something imaginary

---
**Last Updated**: 2025-07-24
**Version**: 2.0
**Status**: ACTIVE - Phase 1 Complete, Phase 2 Planning Needed
**Major Change**: Project pivoted from broad economic analysis to focused ICT adoption tracking