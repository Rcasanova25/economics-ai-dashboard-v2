# Week 3 Plan: Data Cleaning & Professional Standards

**Date:** January 19, 2025  
**Senior Developer Review:** CRITICAL ISSUES FOUND - Must address during Week 3, not after!

---

## 🚨 CRITICAL: Start Week 3 With These Issues

### Day 1 Morning: Version Control & Testing Setup (BEFORE ANY NEW WORK)

#### 1. Initialize Git Repository
```bash
cd economics-ai-dashboard-v2
git init
git add .
git commit -m "Initial commit: Week 2 complete - PDF extraction pipeline"

# Create .gitignore if missing
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "data/raw_pdfs/" >> .gitignore
echo "*.db" >> .gitignore

git add .gitignore
git commit -m "Add .gitignore for Python project"
```

#### 2. Create Test Structure
```
tests/
├── __init__.py
├── test_extractors/
│   ├── __init__.py
│   ├── test_stanford_hai.py
│   ├── test_goldman_sachs.py
│   └── test_universal.py
├── test_database/
│   ├── __init__.py
│   └── test_operations.py
└── test_data_quality/
    ├── __init__.py
    └── test_metrics_validation.py
```

#### 3. Write Critical Tests FIRST
```python
# tests/test_data_quality/test_metrics_validation.py
import pytest
from datetime import datetime

class TestMetricValidation:
    """Tests to ensure data quality BEFORE it enters database"""
    
    def test_year_is_reasonable(self):
        """Years should be between 2000-2030"""
        assert validate_year(2024) == True
        assert validate_year(1999) == False
        assert validate_year(2050) == False
    
    def test_investment_values_reasonable(self):
        """Investment values should be within reasonable bounds"""
        # $0-10 trillion is reasonable for global AI investment
        assert validate_investment(100, 'billions_usd') == True
        assert validate_investment(50000, 'billions_usd') == False  # $50T too high
        
    def test_percentage_bounds(self):
        """Percentages should be 0-100 (or -100 to 100 for changes)"""
        assert validate_percentage(75.5) == True
        assert validate_percentage(150) == False
        assert validate_percentage(-25) == True  # Allow negative for declines
```

---

## Week 3 Day-by-Day Plan (Revised)

### Day 1: Foundation & Quality Gates
**Morning:**
- ✅ Set up git repository
- ✅ Create test structure
- ✅ Write data validation tests

**Afternoon:**
- Create data validation module
- Run validation on existing 12,258 metrics
- Document all quality issues found

**Deliverable:** `data_quality_report.md` with all issues

### Day 2: Data Cleaning Implementation
**Morning:**
- Build cleaning scripts based on quality report
- Implement validation functions that tests require
- Create backup of original data

**Afternoon:**
- Clean the data systematically:
  - Remove duplicates
  - Fix outliers
  - Standardize units
  - Classify "general_rate" metrics

**Deliverable:** `cleaned_metrics.db` with validation passed

### Day 3: Economic Categorization
**Morning:**
- Review context fields to understand metrics
- Create economic taxonomy:
  ```python
  ECONOMIC_CATEGORIES = {
      'adoption': ['adoption_rate', 'implementation_rate', 'usage_rate'],
      'investment': ['ai_investment', 'r&d_spending', 'infrastructure_cost'],
      'productivity': ['efficiency_gain', 'output_increase', 'time_saved'],
      'employment': ['jobs_created', 'jobs_displaced', 'skill_demand'],
      'cost_benefit': ['roi', 'payback_period', 'cost_savings']
  }
  ```

**Afternoon:**
- Recategorize all metrics
- Add economic metadata
- Write tests for categorization

**Deliverable:** Properly categorized dataset

### Day 4: Dashboard Polish
**Morning:**
- Update dashboard to use cleaned data
- Add data quality indicators
- Show confidence scores

**Afternoon:**
- Add economic narrative to each page
- Create "About the Data" section
- Implement export functionality

**Deliverable:** Professional dashboard with clean data

### Day 5: Documentation & Deployment Prep
**Morning:**
- Write comprehensive README
- Create deployment guide
- Document data cleaning methodology

**Afternoon:**
- Set up GitHub repository
- Create GitHub Pages for documentation
- Final testing and review

**Deliverable:** Portfolio-ready project

---

## Senior Developer Checkpoints

### Before Starting ANY New Feature:
```python
# Ask yourself:
1. Have I written tests for this?
2. Have I committed my last changes?
3. Will this pass code review?
4. Is this documented?
```

### Daily Git Workflow:
```bash
# Start of day
git status
git pull (if working with remote)

# Before each feature
git checkout -b feature/data-cleaning

# After each logical unit of work
git add .
git commit -m "Add data validation for year ranges"

# End of day
git push origin feature/data-cleaning
```

### Testing Workflow:
```bash
# Before committing any code
pytest tests/
pytest --cov=src tests/  # Check coverage

# Aim for 80% coverage minimum
```

---

## Configuration Management (Fix This Week)

### Create `.env.example`:
```
DATABASE_PATH=data/processed/economics_ai.db
LOG_LEVEL=INFO
EXPORT_PATH=data/exports
PDF_PATH=data/raw_pdfs
```

### Create `config.py`:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_PATH = Path(os.getenv('DATABASE_PATH', 'data/processed/economics_ai.db'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    EXPORT_PATH = Path(os.getenv('EXPORT_PATH', 'data/exports'))
    
    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        if not cls.DATABASE_PATH.parent.exists():
            raise ConfigError(f"Database directory does not exist: {cls.DATABASE_PATH.parent}")
```

---

## Data Quality Checklist (Run Daily)

- [ ] All tests passing
- [ ] No hardcoded paths in code
- [ ] All changes committed to git
- [ ] Documentation updated
- [ ] No print statements (use logging)
- [ ] Error handling for all external operations
- [ ] Data validation before database insertion

---

## What Success Looks Like

By end of Week 3, you should have:

1. **Clean Git History** showing iterative development
2. **80%+ Test Coverage** with meaningful tests
3. **Validated Data** with documented cleaning process
4. **Professional Code** that would pass senior review
5. **Economic Insights** not just technical extraction

**Remember:** A senior developer catches issues DURING development, not after. Use this plan to build quality in from the start.

---

## The Economic Story

As you clean the data, document the economic narrative:
- What trends are emerging?
- Which sources conflict and why?
- What insights would interest AI companies?
- How does this data inform AI economic policy?

Your value is not just in cleaning data, but in understanding what it means economically.