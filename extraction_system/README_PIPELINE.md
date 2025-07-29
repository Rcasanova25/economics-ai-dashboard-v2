# Multi-Stage Extraction Pipeline with Human Validation

## Overview
This system combines automated extraction with human validation to ensure high-quality economic metrics from PDFs.

## Architecture

### 1. Multi-Stage Pipeline (`multi_stage_pipeline.py`)
Extracts metric candidates through 5 stages:

**Stage 1: Text Extraction**
- Inline percentages, financial values, growth rates
- Pattern: "73% of companies", "$5.2 billion investment"

**Stage 2: Table Extraction** 
- Uses tabula-py for structured tables
- Preserves row/column context

**Stage 3: Pattern Matching**
- Report-specific patterns (McKinsey, OECD, etc.)
- High-confidence targeted extraction

**Stage 4: Deduplication**
- Removes duplicate values from same page
- Keeps highest confidence version

**Stage 5: Enrichment**
- Suggests categories and types
- Flags potential issues

### 2. Validation UI (`validation_ui.py`)
Web interface for human review:

**Features:**
- Sequential review of candidates
- Accept/Reject/Modify decisions
- Pre-populated AI suggestions
- Progress tracking
- Batch save functionality

**Output:**
- Validated metrics in JSON
- Ready for Stanford-schema conversion

## Usage

### Step 1: Extract Candidates
```python
from multi_stage_pipeline import MultiStagePipeline

pipeline = MultiStagePipeline()
candidates = pipeline.extract_from_pdf("path/to/pdf")
```

Output: `extraction_output/filename_candidates.json`

### Step 2: Validate via UI
```bash
python validation_ui.py
```

1. Open http://localhost:8050
2. Select candidates file
3. Review each candidate:
   - **Accept**: Metric is correct
   - **Reject**: Not a real metric
   - **Modify**: Needs correction
   - **Skip**: Review later
4. Click "Save Progress" periodically

Output: `extraction_output/filename_validated.json`

### Step 3: Create Final Dataset
```python
from validation_ui import create_final_dataset

create_final_dataset(
    "extraction_output/filename_validated.json",
    "final_metrics.csv"
)
```

## Quality Metrics

**Typical Results:**
- Stage 1 (Text): 100-200 candidates
- Stage 2 (Tables): 20-50 candidates
- Stage 3 (Patterns): 10-30 candidates
- After dedup: 50-100 unique candidates
- After validation: 20-40 high-quality metrics

**Time Investment:**
- Extraction: 1-2 minutes per PDF
- Validation: 10-15 minutes per PDF
- Total: ~15 minutes for 20-40 quality metrics

## Advantages

1. **Comprehensive Coverage**: Multiple extraction methods catch different metric types
2. **Quality Control**: Human validates every metric
3. **Efficient**: Pre-populated suggestions speed up validation
4. **Traceable**: Every decision is logged
5. **Replicable**: Same process works for any PDF

## Best Practices

1. **Start with High-Confidence**: Review high-confidence candidates first
2. **Use Notes Field**: Document why you rejected/modified
3. **Save Often**: Click save every 10-20 candidates
4. **Check Context**: Always read surrounding text
5. **Be Conservative**: When in doubt, reject

## Extending the System

### Add New Extraction Patterns
Edit `_stage3_pattern_matching()` in pipeline:
```python
patterns = [
    r'your_new_pattern',
]
```

### Add New Categories
Edit `economic_metrics_schema.py`:
```python
class MetricCategory(Enum):
    NEW_CATEGORY = "new_category"
```

### Customize UI
Edit `validation_ui.py` layout for additional fields.

## Troubleshooting

**No tables extracted**: PDF might use images instead of text tables
**Too many candidates**: Adjust confidence thresholds
**UI not loading**: Check if port 8050 is free

## Future Enhancements

1. **ML Classification**: Train on validated data
2. **Batch Operations**: Validate multiple similar metrics at once  
3. **Collaboration**: Multiple reviewers with conflict resolution
4. **Auto-validation**: High-confidence metrics auto-approved

---

This pipeline balances automation with human expertise to deliver quality economic data extraction at scale.