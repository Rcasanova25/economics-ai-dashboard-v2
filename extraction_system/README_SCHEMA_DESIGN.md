# Economic Metrics Extraction Schema Design

## Overview
This schema is designed to extract meaningful economic metrics from the 5 remaining high-quality PDFs, using Stanford AI Index data structure as a template.

## Key Design Principles

### 1. **Schema-First Approach**
Unlike Phase 1 where we extracted everything and filtered later, we now define exactly what we want upfront:
- Specific metric categories (Labor, Investment, Adoption, etc.)
- Expected value ranges
- Valid units for each metric type
- Required vs optional fields

### 2. **Stanford Alignment**
The schema mirrors Stanford's proven structure:
```
Stanford: Year | Metric Value | Geographic/Category Dimension
Our Schema: Year | Value | Unit | Category | Type | Geography | Sector | Context
```

### 3. **Multi-Dimensional Classification**
Each metric is classified across multiple dimensions:
- **Temporal**: Year, time period, forecast year
- **Geographic**: Global → Regional → Country with details
- **Sectoral**: Industry verticals 
- **Company Size**: Enterprise, SMB, Startup
- **Quality**: High/Medium/Low confidence

### 4. **Built-in Validation**
- Value range checks (e.g., percentages 0-100)
- Unit-category alignment (no financial units for employment metrics)
- Year validation (2010-2030 range)
- Citation year detection and filtering

### 5. **Extraction Targets**
Pre-defined patterns for each metric category:
```python
Labor Market: "job postings", "AI talent", patterns like "X% of job postings"
Investment: "funding", "venture capital", patterns like "$X billion"
Adoption: "using AI", "deployed", patterns like "X% of companies"
```

## How It Solves Phase 1 Problems

| Phase 1 Problem | Schema Solution |
|----------------|-----------------|
| 47% unknown sector | Pre-defined sector enum with patterns |
| Generic counts | Specific metric types only |
| Citation years | Built-in detection and filtering |
| No economic focus | Categories aligned with economic analysis |
| Low confidence | Quality scoring and confidence levels |

## Usage Pattern

1. **Define what you want**: Use EXTRACTION_TARGETS
2. **Extract with validation**: Built-in business rules
3. **Multi-source reconciliation**: Track source document
4. **Quality assurance**: Confidence scoring

## Next Steps

1. Test extraction on one McKinsey PDF section
2. Refine patterns based on actual content
3. Add specialized extractors for complex tables
4. Build reconciliation logic for conflicting data points

The schema is extensible - we can add new sectors, metric types, or geographic regions as we discover them in the PDFs.