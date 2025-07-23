# Week 2: PDF Processing Pipeline - Complete Documentation

**Completion Date:** January 19, 2025  
**Senior Developer:** Claude  
**Student:** Entry-level developer with economics background

---

## Overview

Week 2 focused on building a comprehensive PDF processing pipeline to automate data extraction from economic and AI research papers. We successfully extracted **12,258 metrics** from 22 PDF sources, replacing manual data extraction with an automated, scalable solution.

---

## Architecture Implemented

### 1. PDF Processing Pipeline Structure

```
src/
├── pipeline/
│   ├── __init__.py
│   ├── pdf_processor.py          # Base PDF processing classes
│   └── extractors/
│       ├── __init__.py
│       ├── stanford_hai.py       # Stanford HAI specialized extractor
│       ├── oecd.py              # OECD specialized extractor
│       ├── mckinsey.py          # McKinsey specialized extractor
│       ├── goldman_sachs.py     # Goldman Sachs specialized extractor
│       ├── academic.py          # Academic papers extractor
│       └── universal.py         # Universal fallback extractor
└── database/
    ├── __init__.py
    ├── models.py                # SQLAlchemy ORM models
    └── operations.py            # Database CRUD operations
```

### 2. Key Design Decisions

1. **Hybrid Extraction Strategy**: Specialized extractors for known sources + universal fallback
2. **SQLAlchemy ORM**: For database abstraction and query safety
3. **Confidence Scoring**: Track reliability of extracted data
4. **Conflict Detection**: Identify contradictory information across sources
5. **Table Extraction**: Java + tabula-py for complex PDF tables

---

## Step-by-Step Implementation

### Step 1: Base PDF Processor (pdf_processor.py)

```python
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import logging

@dataclass
class ExtractedMetric:
    """Represents a single extracted metric."""
    metric_type: str
    value: float
    unit: str
    year: int
    context: str
    confidence: float = 1.0
    sector: Optional[str] = None
    region: Optional[str] = None
    page_number: Optional[int] = None

class BasePDFExtractor(ABC):
    """Abstract base class for PDF extractors."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def extract(self, text: str, pdf_path: Path) -> List[ExtractedMetric]:
        """Extract metrics from PDF text."""
        pass
    
    def extract_tables(self, pdf_path: Path) -> List[pd.DataFrame]:
        """Extract tables using tabula-py."""
        try:
            import tabula
            tables = tabula.read_pdf(
                str(pdf_path),
                pages='all',
                multiple_tables=True,
                lattice=True
            )
            return tables
        except Exception as e:
            self.logger.warning(f"Table extraction failed: {e}")
            return []
```

### Step 2: Specialized Extractors

**Stanford HAI Extractor** (stanford_hai.py):
```python
class StanfordHAIExtractor(BasePDFExtractor):
    """Specialized extractor for Stanford HAI reports."""
    
    def extract(self, text: str, pdf_path: Path) -> List[ExtractedMetric]:
        metrics = []
        
        # Pattern for AI adoption rates
        adoption_pattern = r'(\d{4}).*?adoption.*?(\d+\.?\d*)\s*%'
        for match in re.finditer(adoption_pattern, text, re.IGNORECASE):
            year = int(match.group(1))
            value = float(match.group(2))
            
            metrics.append(ExtractedMetric(
                metric_type='adoption_rate',
                value=value,
                unit='percentage',
                year=year,
                context=match.group(0)[:200],
                confidence=0.95
            ))
        
        # Extract investment figures
        investment_pattern = r'\$(\d+(?:\.\d+)?)\s*(billion|million)'
        # ... more patterns
        
        return metrics
```

### Step 3: Database Schema (models.py)

```python
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DataSource(Base):
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    organization = Column(String(255))
    pdf_path = Column(String(500))
    extraction_date = Column(DateTime, default=datetime.utcnow)
    
    metrics = relationship("AIMetric", back_populates="source")

class AIMetric(Base):
    __tablename__ = 'ai_metrics'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    confidence = Column(Float, default=1.0)
    
    source = relationship("DataSource", back_populates="metrics")
    
    __table_args__ = (
        Index('idx_metric_type_year', 'metric_type', 'year'),
    )
```

### Step 4: Main Extraction Script (extract_all_pdfs.py)

```python
def process_pdf(pdf_path: Path) -> Dict:
    """Process a single PDF file."""
    
    # Select appropriate extractor
    extractor = select_extractor(pdf_path.name)
    
    # Extract text
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    
    # Extract metrics
    metrics = extractor.extract(text, pdf_path)
    
    # Extract tables if needed
    if isinstance(extractor, (StanfordHAIExtractor, OECDExtractor)):
        tables = extractor.extract_tables(pdf_path)
        # Process tables...
    
    return {
        'pdf_name': pdf_path.name,
        'metrics': [metric_to_dict(m) for m in metrics],
        'extraction_date': datetime.now().isoformat()
    }
```

### Step 5: Java Installation for Table Extraction

Created `install_java.bat`:
```batch
@echo off
echo Installing Java for PDF table extraction...

:: Check if Java is already installed
java -version 2>nul
if %errorlevel% == 0 (
    echo Java is already installed!
    java -version
    exit /b 0
)

:: Download OpenJDK 17
echo Downloading OpenJDK 17...
powershell -Command "Invoke-WebRequest -Uri 'https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_windows-x64_bin.zip' -OutFile 'openjdk-17.zip'"

:: Extract and install
echo Extracting Java...
powershell -Command "Expand-Archive -Path 'openjdk-17.zip' -DestinationPath 'C:\Program Files\Java' -Force"

:: Add to PATH
echo Adding Java to PATH...
setx PATH "%PATH%;C:\Program Files\Java\jdk-17.0.2\bin" /M

echo Java installation complete!
```

### Step 6: Statistics Conversion Fix

When we discovered Stanford HAI only extracted 2 metrics but found 9,557 statistics:

```python
def classify_statistic(stat: Dict, stat_type: str) -> Dict[str, Any]:
    """Convert raw statistic to structured metric."""
    
    value_str = stat.get('value', '')
    context = stat.get('context', '')
    
    # Parse numeric value
    value_match = re.search(r'([-]?\d+\.?\d*)', value_str)
    if not value_match:
        return None
    
    value = float(value_match.group(1))
    
    # Classify based on context
    if any(word in context.lower() for word in ['adoption', 'using ai']):
        metric_type = 'adoption_rate'
    elif any(word in context.lower() for word in ['investment', 'funding']):
        metric_type = 'investment'
    # ... more classifications
    
    return {
        'metric_type': metric_type,
        'value': value,
        'unit': determine_unit(stat_type, value_str),
        'year': extract_year(context),
        'confidence': 0.8
    }
```

### Step 7: Database Import (import_metrics_to_db.py)

```python
class MetricsImporter:
    def import_json_file(self, json_path: Path) -> Dict:
        """Import metrics from JSON file."""
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validate metrics
        valid_metrics = []
        for metric in data.get('metrics', []):
            is_valid, error = self.validate_metric(metric)
            if is_valid:
                valid_metrics.append(metric)
        
        # Batch import with transaction
        imported, duplicates = self.db.add_metrics_batch(
            valid_metrics, 
            source_name=data.get('pdf_name', json_path.stem)
        )
        
        return {'imported': imported, 'duplicates': duplicates}
```

---

## Key Learning Points

### 1. **Pattern Matching for Data Extraction**
```python
# Good pattern - specific and contextual
adoption_pattern = r'(\d{4}).*?adoption.*?(\d+\.?\d*)\s*%'

# Bad pattern - too generic
number_pattern = r'\d+\.?\d*'
```

### 2. **Error Handling in Production Code**
```python
# Good - specific error handling
try:
    tables = tabula.read_pdf(pdf_path)
except FileNotFoundError:
    logger.error(f"PDF not found: {pdf_path}")
    raise
except Exception as e:
    logger.warning(f"Table extraction failed, continuing: {e}")
    tables = []
```

### 3. **Database Transaction Management**
```python
@contextmanager
def session_scope(engine):
    """Provide transactional scope."""
    session = get_session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### 4. **Data Validation**
```python
def validate_metric(metric: Dict) -> Tuple[bool, str]:
    """Validate before database insertion."""
    
    # Check required fields
    if 'value' not in metric:
        return False, "Missing value"
    
    # Validate numeric
    try:
        float(metric['value'])
    except ValueError:
        return False, f"Invalid value: {metric['value']}"
    
    return True, ""
```

---

## Results Achieved

### Extraction Results:
- **Total PDFs processed:** 22
- **Total metrics extracted:** 12,258
- **Unique metric types:** 36
- **Year range:** 2010-2030
- **Average confidence:** 0.75

### Top Metric Types:
1. General rate: 4,536
2. Percentages: 3,340
3. Dollar amounts: 480
4. Growth rate: 476
5. Employment: 412

### Conflict Detection:
Found significant conflicts (>15% difference) in:
- Adoption rates across sources
- Investment figures for same years
- Productivity predictions

---

## Commands to Run the Pipeline

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Java (if needed for tables)
install_java.bat

# 3. Test Java installation
python test_java_extraction.py

# 4. Run full extraction
python extract_all_pdfs.py

# 5. Convert statistics to metrics
python convert_statistics_to_metrics.py

# 6. Import to database
python import_metrics_to_db.py

# 7. Verify database
python verify_database.py
```

---

## Troubleshooting Guide

### Issue 1: Java Not Found
```
Error: Java not found for table extraction
Solution: Run install_java.bat and restart terminal
```

### Issue 2: Low Metric Count
```
Problem: Stanford HAI only extracted 2 metrics
Solution: Run convert_statistics_to_metrics.py to recover data
Result: Increased from 2 to 229 metrics
```

### Issue 3: Unicode Errors
```
Error: 'charmap' codec can't encode character
Solution: Use encoding='utf-8' when opening files
```

### Issue 4: SQLAlchemy Compatibility
```
Error: Python 3.13 compatibility issue
Solution: Upgrade to sqlalchemy>=2.0.30
```

---

## Best Practices Demonstrated

1. **Modular Architecture**: Separate extractors for different sources
2. **Error Recovery**: Fallback extractors ensure no data loss
3. **Data Quality**: Confidence scoring and conflict detection
4. **Performance**: Batch imports and indexed queries
5. **Maintainability**: Clear code structure and documentation

---

## Next Steps (Week 3)

1. Connect database to Dash dashboard
2. Create interactive visualizations
3. Implement real-time metric updates
4. Add user authentication
5. Deploy to production

---

## Conclusion

Week 2 successfully automated the PDF extraction process, replacing manual data entry with a robust, scalable pipeline. The system extracted over 12,000 metrics with conflict detection and confidence scoring, providing a solid foundation for economic analysis of AI adoption.

The hybrid extraction approach ensures comprehensive data capture while maintaining quality through validation and conflict detection. This pipeline can easily be extended with new extractors as more PDF sources become available.