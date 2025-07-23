# Standard Operating Procedures - Economics AI Dashboard
**Established**: July 21, 2025  
**Authors**: Senior Developer (AI) & Junior Developer (Economics Expert)  
**Purpose**: Codify best practices and procedures learned during Week 3 data cleanup

> ## 📊 **"The Dashboard is only as good as its Data"**
> *This mantra guides every decision in our data cleanup process*

## Core Principles

1. **Review Before Execute**: NEVER execute destructive operations without explicit review and approval
2. **Domain Expertise Matters**: Always consider economic context before removing data
3. **First Occurrence Preservation**: When removing duplicates, ALWAYS keep the first occurrence
4. **Full Traceability**: Every action must be documented with original IDs and confidence scores
5. **Backup Before Modify**: Create verified backups before any data modifications

## Data Cleanup Standard Procedure

### Phase 1: Analysis (READ-ONLY)
```bash
# Run analysis only - DO NOT EXECUTE CLEANUP
python source_cleanup_template.py <source_id> <input_csv>

# Or with integrated workflow
python src/pipeline/run_source_cleanup.py <source_id> --start-file <input_csv> --analyze-only
```

**Output Review Checklist**:
- [ ] Review `Source Data Cleanup Analysis/Source_X/initial_analysis.csv`
- [ ] Check `records_to_remove.csv` - verify no valuable data
- [ ] Check `records_to_modify.csv` - verify classifications are correct
- [ ] Check `records_to_keep.csv` - ensure important metrics preserved
- [ ] Read `cleanup_summary.txt` for statistics

### Phase 2: Decision Point (MANDATORY PAUSE)

**Questions to Answer**:
1. Are any valuable metrics being removed? (Check context carefully)
2. Are domain-specific terms (like "ICT") being misclassified?
3. Do the duplicate counts make sense?
4. Are the metric reclassifications appropriate?

**Red Flags**:
- Removal rate > 50% (investigate further)
- High-value financial metrics marked for removal
- Sector-specific data (ICT, Manufacturing) marked as garbage
- All occurrences of a value marked for removal (check duplicate handling)

### Phase 3: Execute (ONLY AFTER APPROVAL)

**If Approved**:
```bash
# Execute with backup
python src/pipeline/run_source_cleanup.py <source_id> --start-file <input_csv> --auto-confirm
```

**If Changes Needed**:
1. Modify the analysis logic in source_cleanup_template.py
2. Re-run analysis
3. Review again

## Critical Checks Before Execution

### 1. Duplicate Handling Verification
```python
# CORRECT - Preserves first occurrence
if idx == dup_info['first']:
    # Keep this record
elif idx in dup_info['duplicates']:
    # Remove this record

# WRONG - Removes all occurrences
if is_duplicate:
    # Remove this record
```

### 2. Context Awareness Check
- "24 billions_usd" with context "Figure 9" → Likely extraction artifact
- "0.0%" with context "no change in productivity" → Meaningful zero, keep
- "ICT" in context → Information & Communication Technology, not garbage

### 3. Unit Validation
- `billions_usd` with small values + context mentioning "thousands" → Fix unit
- `energy_unit` with year-like values (2023, 2024) → Reclassify as year

## Infrastructure Requirements

### Before Starting ANY Cleanup:

1. **Version Control**
   ```bash
   git status  # Ensure clean working directory
   git add .
   git commit -m "Pre-cleanup checkpoint for Source X"
   ```

2. **Backup System**
   - Automated backups with checksums
   - Verify backup created before proceeding
   - Keep last 10 backups minimum

3. **Testing**
   ```bash
   pytest tests/test_data_cleanup.py -v  # Must pass
   ```

4. **Logging**
   - Structured logging enabled
   - Separate log file per cleanup session
   - Both human-readable and JSON formats

## Common Pitfalls to Avoid

1. **Creating Scripts for Simple Tasks**
   - ❌ Writing a Python script to find one data point
   - ✅ Using grep, pandas operations, or SQL queries

2. **Ignoring Domain Context**
   - ❌ Removing "ICT" data as garbage
   - ✅ Recognizing ICT = Information & Communication Technology

3. **Silent Failures**
   - ❌ Continuing after errors without investigation
   - ✅ Stop, investigate, fix root cause

4. **Rushing Through Process**
   - ❌ Running analysis and cleanup in one step
   - ✅ Separate analysis, review, and execution phases

## Emergency Procedures

### If Data Was Accidentally Deleted:
1. **STOP** all operations immediately
2. Locate the latest backup in `backups/` directory
3. Verify backup integrity with checksum
4. Restore using BackupManager
5. Document what happened in session log

### If Unsure About Data:
1. Default to **KEEPING** the data
2. Mark for manual review
3. Consult domain expert (economist)
4. Document decision reasoning

## Review Checklist

Before marking ANY source as complete:

- [ ] Analysis was run separately from execution
- [ ] All CSV files were reviewed
- [ ] Domain expert approved removals
- [ ] Backup was created and verified
- [ ] Tests still pass
- [ ] Git commit created
- [ ] Session log updated

## Continuous Improvement

After each source cleanup:
1. Document any new patterns discovered
2. Update classification logic if needed
3. Add test cases for edge cases
4. Update this procedures document

## Sign-Off Requirement

**No cleanup execution without explicit approval**: "I have reviewed the analysis and approve the cleanup execution for Source X"

---

*Remember: It's better to keep questionable data than to accidentally delete valuable information. When in doubt, keep it and mark for manual review.*