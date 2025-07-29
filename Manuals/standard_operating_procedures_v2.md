# Standard Operating Procedures - Economics of AI Dashboard
**Version**: 2.0  
**Updated**: July 24, 2025  
**Status**: Active - Incorporates Phase 1 Lessons

## Purpose
This SOP guides the development of economic analysis dashboards from PDF sources, incorporating hard-learned lessons from the initial ICT adoption dashboard project.

## CRITICAL: Pre-Development Validation

### 1. Data Source Validation (MANDATORY)
Before writing ANY code:

1. **Manual Review** (2-3 hours)
   - Open 3 source PDFs
   - Search for specific metrics you need
   - Copy 5-10 example data points
   - Verify they contain quantitative data, not just mentions

2. **Feasibility Checklist**
   - [ ] Sources contain numerical economic metrics?
   - [ ] Metrics have clear units (%, $, jobs)?
   - [ ] Data is extractable (not in images)?
   - [ ] Sufficient data density (>10 metrics per document)?
   - [ ] Temporal data available for trends?

3. **Go/No-Go Decision**
   - If <3 checkboxes: STOP and find better sources
   - If 3-4 checkboxes: Reduce scope and proceed cautiously
   - If 5 checkboxes: Proceed with development

### 2. Scope Definition

**Start Small**
- Phase 1: Single sector, single metric type
- Phase 2: Single sector, multiple metrics
- Phase 3: Multiple sectors, focused metrics
- Never: All sectors, all metrics in one phase

**Example Scoping**
- ❌ BAD: "Economics of AI across all sectors"
- ✅ GOOD: "ICT sector AI adoption rates"
- ✅ BETTER: "Financial services AI ROI metrics from 5 reports"

## Development Process

### Phase 1: Proof of Concept (1-2 days)
1. Extract from 2-3 best sources
2. Validate extraction quality
3. Create simple visualization
4. Get stakeholder feedback
5. **CRITICAL**: Be ready to pivot or stop

### Phase 2: Scale if Successful (3-5 days)
1. Add remaining sources
2. Enhance extraction rules
3. Build full dashboard
4. Document limitations honestly

### Phase 3: Iterate and Improve (Ongoing)
1. Add new sources quarterly
2. Refine extraction based on patterns
3. Expand scope incrementally

## Technical Standards

### Extraction System Design
```python
# Schema-based validation (proven approach)
class MetricSchema:
    metric_types = [...]  # Define explicitly
    valid_units = [...]   # Define explicitly
    sector_patterns = {}  # Sector-specific patterns
    
# Deduplication at extraction (not post-process)
def extract_metric():
    if is_duplicate(metric):
        return None
    return validated_metric
```

### Data Quality Thresholds
- Removal rate >10%: Review process
- Unknown sector >30%: Improve classification
- Generic counts >50%: Wrong data sources

### Context Windows
- Minimum: 10 words before/after
- Optimal: 20-30 words or full sentence
- For sectors: Check full paragraph

## Communication Protocols

### With Stakeholders
1. **Set Realistic Expectations**
   - "This shows adoption patterns, not economic impact"
   - "Phase 1 focuses on data availability assessment"
   - "Full economic analysis requires industry reports"

2. **Regular Reality Checks**
   - Daily: "Is this data useful?"
   - Weekly: "Should we pivot?"
   - End of phase: "What did we learn?"

### With Development Team
1. **Encourage Honest Feedback**
   - "This might not work because..."
   - "The data doesn't support..."
   - "We should consider pivoting..."

2. **Avoid Reflexive Agreement**
   - Question assumptions
   - Propose alternatives
   - Share concerns early

## Data Source Recommendations

### Tier 1 (Preferred)
- Industry analyst reports (Gartner, IDC, Forrester)
- Company financial reports (10-K, earnings)
- Government economic statistics
- Structured survey results

### Tier 2 (Acceptable)
- Industry association reports
- Consulting firm studies (McKinsey, BCG)
- Economic research with data appendices

### Tier 3 (Avoid)
- Academic discussion papers
- Policy recommendations
- Conceptual frameworks
- Literature reviews

## Success Metrics

### Phase 1 Success
- Extracted 50+ relevant metrics
- Clear visualization delivered
- Honest assessment of limitations
- Foundation for Phase 2

### Project Success
- Delivering useful insights
- Not pretending to have data we don't
- Building incrementally
- Learning from each phase

## Lessons Learned Integration

### From ICT Dashboard Project
1. **Extraction quality ≠ Data quality**
2. **Academic PDFs lack economic metrics**
3. **Focused delivery > Ambitious failure**
4. **Brutal honesty enables pivots**

### Action Items
- Always validate sources first
- Start with narrow scope
- Pivot fast when needed
- Deliver something real

## Review Schedule
- After each phase completion
- When pivoting scope
- Quarterly updates
- Major lesson learned triggers immediate update

---

**Remember**: It's better to deliver a focused, honest analysis of what you have than to pretend you have comprehensive economic data that doesn't exist in your sources.

**The Prime Directive**: Validate data availability BEFORE building systems.