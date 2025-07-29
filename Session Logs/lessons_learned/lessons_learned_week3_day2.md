# Lessons Learned: Best Practices for Data Cleanup Systems

## For Junior Developers: What We Learned in Week 3 Day 2

### 1. 🔍 Always Test with Real Data First

**What Happened**: We created a "perfect" template, but testing on Source 8 revealed three critical bugs that would have corrupted all remaining data.

**Best Practice**: 
- Test your code on actual data before scaling up
- Don't assume test data represents all edge cases
- One real-world test is worth 100 synthetic tests

**Example**:
```python
# Bad: Assuming all years are metric values
if 1900 <= value <= 2030:
    process_as_year_metric(value)

# Good: Check context for citations
if 1900 <= value <= 2030 and value == year:
    if re.search(r'\(\d{4}\)', context):  # It's a citation!
        skip_record()
```

### 2. 🎯 Root Cause Analysis > Quick Fixes

**What Happened**: CSV parsing kept failing. We tried 3 different "fixes" before discovering the test fixture was creating an empty file.

**Best Practice**:
- When something fails mysteriously, create a minimal reproduction
- Use print debugging or debugger to understand exact behavior
- Don't guess - investigate

**Debugging Approach**:
```python
# Create minimal test case
print("Step 1: File exists?", os.path.exists(file))
print("Step 2: File size?", os.path.getsize(file))
print("Step 3: File contents?", open(file, 'rb').read())
# Now you can see exactly what's wrong
```

### 3. 📐 Design Schemas Before Code

**What Happened**: We discovered validation needs by trial and error, then retrofitted schemas.

**Best Practice**:
- Define your data expectations explicitly
- Use schemas to drive validation logic
- Document assumptions in the schema

**Schema-Driven Design**:
```python
SCHEMA = {
    "employment_metric": {
        "valid_units": ["number", "percentage"],
        "invalid_units": ["dollars", "millions_usd"],  # ← Prevents nonsense
        "zero_value_valid": False,  # ← 0 employees is suspicious
    }
}
```

### 4. 🧩 Modular Architecture Saves Time

**What Happened**: We refactored monolithic code into modules, making testing and debugging much easier.

**Best Practice**:
- One module = one responsibility
- If a function is >50 lines, consider splitting
- If you're copying code, make it a function

**Good Structure**:
```
project/
├── validator.py      # Only validation logic
├── tracker.py        # Only tracking/metrics
├── processor.py      # Only processing logic
└── tests/           # Test each module separately
```

### 5. 🧪 Write Tests That Should Fail

**What Happened**: Our tests were too "happy path" - they didn't catch real issues.

**Best Practice**:
- Test invalid inputs
- Test edge cases (empty, null, too large)
- Test the bugs you've actually seen

**Example Test**:
```python
def test_citation_year_detected():
    # This SHOULD be removed
    result = validator.validate(
        value=2024, 
        year=2024, 
        context="According to Smith (2024)..."
    )
    assert result.action == "remove"
    assert "citation" in result.reason
```

### 6. 🛡️ Defensive Programming is Not Optional

**What Happened**: Missing values caused cryptic errors deep in the code.

**Best Practice**:
- Check inputs at entry points
- Fail fast with clear messages
- Never assume data is clean

**Defensive Code**:
```python
def process_record(row):
    # Check everything first
    if pd.isna(row['value']):
        return skip_with_reason("Missing value")
    if not isinstance(row['year'], (int, float)):
        return skip_with_reason(f"Invalid year type: {type(row['year'])}")
    # Now safe to process
```

### 7. 📊 Measure Everything

**What Happened**: We added quality tracking and immediately saw patterns in the data.

**Best Practice**:
- Log what you're doing
- Track metrics over time
- Use data to prove improvements

**Quality Metrics**:
```python
- Records processed
- Removal rate
- Modification rate  
- Quality score
- Processing time
- Confidence distribution
```

### 8. 🔄 Make It Reusable from the Start

**What Happened**: We had to refactor for reusability after building for one project.

**Best Practice**:
- Parameterize file paths
- Externalize configuration
- Think "next project" while building

**Reusable Design**:
```python
# Bad: Hardcoded
df = pd.read_csv('data/exports/data_sources_20250719.csv')

# Good: Configurable
def __init__(self, data_sources_file='data/exports/data_sources_20250719.csv'):
    self.df = pd.read_csv(data_sources_file)
```

### 9. 📝 Document Weird Decisions

**What Happened**: "productiv" pattern looked like a typo but was intentional (catches productivity, productive, etc.)

**Best Practice**:
- Comment non-obvious code
- Explain "why" not "what"
- Future you will thank present you

**Good Documentation**:
```python
# Using "productiv" as prefix to match all variations:
# productivity, productive, productiveness
patterns_required = ["productiv", "efficiency", "output"]
```

### 10. 🎭 Domain Knowledge + Tech Skills = Success

**What Happened**: You (the economist) caught that "employment_metric" with "millions_usd" made no sense.

**Best Practice**:
- Collaborate with domain experts
- Question suspicious patterns
- Don't just process - understand

### 11. 🚨 Know Your Red Flags

**What Happened**: We learned that certain patterns always indicate problems.

**Red Flags in Data**:
- Value equals year (likely a citation)
- Removal rate >80% (something's wrong)
- Metric type doesn't match unit
- Zero with specific quantities in context
- Percentages >100% for rates

### 12. 🔧 Tools Are Not Solutions

**What Happened**: We kept creating new tools instead of fixing the root problem.

**Best Practice**:
- Understand the problem before coding
- Simple solutions are often best
- More code ≠ better solution

## The Meta-Lesson

**The most important lesson**: Good software engineering is about:
1. **Understanding** the problem (not guessing)
2. **Designing** a solution (not coding immediately)
3. **Testing** with real scenarios (not just happy paths)
4. **Iterating** based on feedback (not defending your first attempt)

## Questions Junior Developers Should Ask

1. "What could go wrong with this data?"
2. "How will I know if my code is working correctly?"
3. "What would make this easier to debug?"
4. "How can I test this without processing all data?"
5. "What assumptions am I making?"
6. "Is this the simplest solution?"
7. "What would the next developer need to know?"

## Final Advice

> "Every bug is a missing test. Every confusing error is a missing validation. Every repeated code block is a missing function. Every hardcoded value is a missing parameter."

Remember: The goal isn't to write code quickly - it's to write code that works correctly, can be maintained, and solves the actual problem.