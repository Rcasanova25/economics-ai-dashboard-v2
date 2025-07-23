# PDF Data Extraction Manual for Economists
## A Step-by-Step Guide to Building Reproducible PDF Extractors

**Purpose:** This manual teaches you how to extract structured data from PDF documents using Python, specifically designed for economists who need to process research papers, reports, and data-rich documents.

---

## Table of Contents
1. [Understanding the Extraction Process](#understanding)
2. [Setting Up Your Environment](#setup)
3. [Basic PDF Text Extraction](#basic-extraction)
4. [Pattern Matching for Data](#pattern-matching)
5. [Building Your First Extractor](#first-extractor)
6. [Extracting Tables from PDFs](#table-extraction)
7. [Creating Specialized Extractors](#specialized-extractors)
8. [Handling Different PDF Types](#pdf-types)
9. [Saving Extracted Data](#saving-data)
10. [Complete Working Example](#complete-example)
11. [Troubleshooting Guide](#troubleshooting)

---

## 1. Understanding the Extraction Process {#understanding}

### What We're Building
A system that:
1. Opens PDF files
2. Extracts text and tables
3. Finds specific data (percentages, dollar amounts, years)
4. Structures the data for analysis
5. Saves it in a usable format

### Key Concepts
- **Text Extraction**: Converting PDF content to searchable text
- **Pattern Matching**: Finding specific data formats (like "73.5%" or "$2.5 billion")
- **Data Structuring**: Organizing found data with context and metadata

---

## 2. Setting Up Your Environment {#setup}

### Required Libraries

```python
# Install these packages
pip install PyMuPDF==1.23.8      # For PDF text extraction
pip install tabula-py            # For table extraction (requires Java)
pip install pandas               # For data handling
pip install sqlalchemy>=2.0.30   # For database storage
```

### Basic Imports

```python
# Standard imports for any PDF extraction project
import re                      # For pattern matching
import json                    # For saving data
from pathlib import Path       # For file handling
from datetime import datetime  # For timestamps
from typing import List, Dict  # For type hints

# PDF processing
import fitz                    # PyMuPDF
import tabula                  # For tables

# Data handling
import pandas as pd
```

---

## 3. Basic PDF Text Extraction {#basic-extraction}

### Step 1: Open and Read a PDF

```python
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to your PDF file
        
    Returns:
        All text from the PDF as a single string
    """
    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    
    # Extract text from each page
    all_text = ""
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text()
        all_text += f"\n--- Page {page_number + 1} ---\n"
        all_text += text
    
    # Close the PDF
    pdf_document.close()
    
    return all_text

# Example usage
pdf_text = extract_text_from_pdf("research_paper.pdf")
print(pdf_text[:500])  # Print first 500 characters
```

### Understanding the Code:
- `fitz.open()` - Opens the PDF file
- `len(pdf_document)` - Gets total number of pages
- `page.get_text()` - Extracts text from a single page
- We add page markers to track where data comes from

---

## 4. Pattern Matching for Data {#pattern-matching}

### Common Economic Data Patterns

```python
# Pattern 1: Percentages (e.g., "73.5%", "increased by 45%")
percentage_pattern = r'(\d+\.?\d*)\s*%'

# Pattern 2: Dollar amounts (e.g., "$2.5 billion", "$450 million")
dollar_pattern = r'\$\s*(\d+\.?\d*)\s*(billion|million|trillion)'

# Pattern 3: Years (e.g., "2024", "in 2023")
year_pattern = r'\b(20\d{2})\b'

# Pattern 4: Growth rates (e.g., "grew by 12.5%")
growth_pattern = r'(grew|increased|decreased|declined)\s+by\s+(\d+\.?\d*)\s*%'
```

### How to Use Patterns

```python
def find_percentages(text: str) -> List[Dict]:
    """
    Find all percentages in text with context.
    
    Returns:
        List of dictionaries with value and context
    """
    results = []
    
    # Find all matches
    for match in re.finditer(r'(\d+\.?\d*)\s*%', text):
        # Get the matched value
        value = float(match.group(1))
        
        # Get surrounding context (50 characters before and after)
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()
        
        results.append({
            'value': value,
            'unit': 'percentage',
            'context': context,
            'position': match.start()
        })
    
    return results

# Example usage
text = "AI adoption increased to 73.5% in 2024, up from 45% in 2023."
percentages = find_percentages(text)
print(percentages)
```

---

## 5. Building Your First Extractor {#first-extractor}

### Complete Basic Extractor

```python
class SimpleEconomicExtractor:
    """
    A basic extractor for economic data from PDFs.
    """
    
    def __init__(self):
        # Define patterns we'll look for
        self.patterns = {
            'percentage': r'(\d+\.?\d*)\s*%',
            'dollar_amount': r'\$\s*(\d+\.?\d*)\s*(billion|million)',
            'year': r'\b(20\d{2})\b',
        }
    
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract all economic metrics from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted metrics
        """
        # Step 1: Extract text
        text = self.extract_text(pdf_path)
        
        # Step 2: Find metrics
        metrics = {
            'percentages': self.find_percentages(text),
            'dollar_amounts': self.find_dollar_amounts(text),
            'years': self.find_years(text),
            'metadata': {
                'file': pdf_path,
                'extraction_date': datetime.now().isoformat(),
                'pages': self.count_pages(pdf_path)
            }
        }
        
        return metrics
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF."""
        pdf = fitz.open(pdf_path)
        text = ""
        for page in pdf:
            text += page.get_text()
        pdf.close()
        return text
    
    def find_percentages(self, text: str) -> List[Dict]:
        """Find all percentages with context."""
        results = []
        
        for match in re.finditer(self.patterns['percentage'], text):
            value = float(match.group(1))
            
            # Get context
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].replace('\n', ' ').strip()
            
            # Try to find associated year
            year_match = re.search(self.patterns['year'], context)
            year = int(year_match.group(1)) if year_match else None
            
            results.append({
                'value': value,
                'unit': 'percentage',
                'context': context,
                'year': year
            })
        
        return results
    
    def find_dollar_amounts(self, text: str) -> List[Dict]:
        """Find all dollar amounts with context."""
        results = []
        
        for match in re.finditer(self.patterns['dollar_amount'], text):
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            # Convert to standard unit (millions)
            if unit == 'billion':
                value = value * 1000  # Convert to millions
                unit = 'millions_usd'
            else:
                unit = 'millions_usd'
            
            # Get context
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].replace('\n', ' ').strip()
            
            # Try to find associated year
            year_match = re.search(self.patterns['year'], context)
            year = int(year_match.group(1)) if year_match else None
            
            results.append({
                'value': value,
                'unit': unit,
                'context': context,
                'year': year
            })
        
        return results
    
    def find_years(self, text: str) -> List[int]:
        """Find all years mentioned."""
        years = []
        for match in re.finditer(self.patterns['year'], text):
            year = int(match.group(1))
            if 2000 <= year <= 2030:  # Reasonable range
                years.append(year)
        return sorted(list(set(years)))
    
    def count_pages(self, pdf_path: str) -> int:
        """Count pages in PDF."""
        pdf = fitz.open(pdf_path)
        pages = len(pdf)
        pdf.close()
        return pages

# How to use it
extractor = SimpleEconomicExtractor()
results = extractor.extract_from_pdf("economic_report.pdf")

# Display results
print(f"Found {len(results['percentages'])} percentages")
print(f"Found {len(results['dollar_amounts'])} dollar amounts")
print(f"Years covered: {results['years']}")
```

---

## 6. Extracting Tables from PDFs {#table-extraction}

### Setting Up Table Extraction

```python
def extract_tables_from_pdf(pdf_path: str) -> List[pd.DataFrame]:
    """
    Extract all tables from a PDF.
    
    Note: Requires Java to be installed!
    
    Returns:
        List of pandas DataFrames, one per table
    """
    try:
        # Extract all tables
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',  # Extract from all pages
            multiple_tables=True,  # Get all tables
            lattice=True  # Use line detection
        )
        
        print(f"Found {len(tables)} tables")
        
        # Clean up tables
        cleaned_tables = []
        for i, table in enumerate(tables):
            # Remove empty rows
            table = table.dropna(how='all')
            
            # Remove empty columns
            table = table.dropna(axis=1, how='all')
            
            if not table.empty:
                cleaned_tables.append(table)
                print(f"Table {i+1}: {table.shape[0]} rows x {table.shape[1]} columns")
        
        return cleaned_tables
        
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

# Example: Extract data from tables
def process_economic_table(table: pd.DataFrame) -> List[Dict]:
    """
    Process a table to extract economic metrics.
    """
    metrics = []
    
    # Look for year columns
    year_columns = [col for col in table.columns if re.match(r'20\d{2}', str(col))]
    
    if year_columns:
        for _, row in table.iterrows():
            metric_name = str(row.iloc[0])  # First column usually has metric name
            
            for year_col in year_columns:
                try:
                    value = float(str(row[year_col]).replace(',', '').replace('$', ''))
                    metrics.append({
                        'metric': metric_name,
                        'year': int(year_col),
                        'value': value,
                        'source': 'table'
                    })
                except:
                    continue
    
    return metrics
```

---

## 7. Creating Specialized Extractors {#specialized-extractors}

### Template for Report-Specific Extractor

```python
class IMFReportExtractor:
    """
    Specialized extractor for IMF economic reports.
    
    This shows how to create extractors for specific report formats.
    """
    
    def __init__(self):
        # IMF-specific patterns
        self.patterns = {
            'gdp_growth': r'GDP growth.*?(\d+\.?\d*)\s*%',
            'inflation': r'inflation.*?(\d+\.?\d*)\s*%',
            'unemployment': r'unemployment.*?(\d+\.?\d*)\s*%',
            'fiscal_deficit': r'fiscal deficit.*?(\d+\.?\d*)\s*%.*?GDP'
        }
        
        # Keywords to identify metric types
        self.metric_keywords = {
            'gdp': ['GDP', 'gross domestic product', 'economic growth'],
            'inflation': ['inflation', 'CPI', 'price index'],
            'employment': ['unemployment', 'employment', 'jobs'],
            'fiscal': ['deficit', 'debt', 'fiscal', 'budget']
        }
    
    def extract(self, pdf_path: str) -> List[Dict]:
        """Extract IMF-specific metrics."""
        # Extract text
        pdf = fitz.open(pdf_path)
        full_text = ""
        
        for page_num, page in enumerate(pdf):
            text = page.get_text()
            full_text += text
            
            # Also check for specific sections
            if "Executive Summary" in text:
                # Priority extraction from summary
                self.extract_from_summary(text)
        
        pdf.close()
        
        # Extract metrics
        metrics = []
        
        # GDP Growth
        for match in re.finditer(self.patterns['gdp_growth'], full_text, re.IGNORECASE):
            metrics.append({
                'type': 'gdp_growth',
                'value': float(match.group(1)),
                'unit': 'percentage',
                'context': self.get_context(full_text, match.start())
            })
        
        # Add year information
        metrics = self.add_year_info(metrics, full_text)
        
        return metrics
    
    def get_context(self, text: str, position: int, window: int = 200) -> str:
        """Get surrounding context."""
        start = max(0, position - window)
        end = min(len(text), position + window)
        return text[start:end].replace('\n', ' ').strip()
    
    def add_year_info(self, metrics: List[Dict], text: str) -> List[Dict]:
        """Add year information to metrics based on context."""
        for metric in metrics:
            # Look for year in context
            year_match = re.search(r'\b(20\d{2})\b', metric['context'])
            if year_match:
                metric['year'] = int(year_match.group(1))
            else:
                # Default to current year
                metric['year'] = datetime.now().year
        
        return metrics
```

---

## 8. Handling Different PDF Types {#pdf-types}

### Detecting PDF Type and Selecting Extractor

```python
def select_appropriate_extractor(pdf_path: str) -> object:
    """
    Automatically select the right extractor based on PDF content.
    """
    # Read first few pages to identify report type
    pdf = fitz.open(pdf_path)
    first_pages_text = ""
    
    for i in range(min(3, len(pdf))):
        first_pages_text += pdf[i].get_text()
    
    pdf.close()
    
    # Check for identifying markers
    if "International Monetary Fund" in first_pages_text:
        return IMFReportExtractor()
    elif "World Bank" in first_pages_text:
        return WorldBankExtractor()
    elif "OECD" in first_pages_text:
        return OECDExtractor()
    else:
        # Default to general extractor
        return SimpleEconomicExtractor()

# Usage
pdf_file = "economic_report_2024.pdf"
extractor = select_appropriate_extractor(pdf_file)
results = extractor.extract(pdf_file)
```

---

## 9. Saving Extracted Data {#saving-data}

### Save to JSON (Recommended for Flexibility)

```python
def save_to_json(data: Dict, output_path: str):
    """
    Save extracted data to JSON file.
    """
    # Ensure path exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save with formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Data saved to: {output_file}")

# Example usage
save_to_json(results, "extracted_data/imf_report_2024.json")
```

### Save to CSV (For Excel)

```python
def save_to_csv(metrics: List[Dict], output_path: str):
    """
    Save metrics to CSV for Excel analysis.
    """
    # Convert to DataFrame
    df = pd.DataFrame(metrics)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Data saved to: {output_path}")
    
    # Also create a summary
    summary = df.groupby(['type', 'year'])['value'].agg(['mean', 'count'])
    summary.to_csv(output_path.replace('.csv', '_summary.csv'))
```

### Save to Database (For Large Projects)

```python
def save_to_database(metrics: List[Dict], db_path: str = "economic_data.db"):
    """
    Save metrics to SQLite database.
    """
    import sqlite3
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            value REAL,
            unit TEXT,
            year INTEGER,
            context TEXT,
            source_file TEXT,
            extraction_date TEXT
        )
    ''')
    
    # Insert data
    for metric in metrics:
        cursor.execute('''
            INSERT INTO metrics (type, value, unit, year, context, source_file, extraction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.get('type'),
            metric.get('value'),
            metric.get('unit'),
            metric.get('year'),
            metric.get('context'),
            metric.get('source_file'),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print(f"Saved {len(metrics)} metrics to database")
```

---

## 10. Complete Working Example {#complete-example}

### Full Pipeline: Extract, Process, and Save

```python
"""
Complete PDF extraction pipeline for economic reports.
Save this as: extract_economic_data.py
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

import fitz  # PyMuPDF
import pandas as pd


class EconomicDataExtractor:
    """Complete extractor for economic PDFs."""
    
    def __init__(self):
        # Define all patterns we need
        self.patterns = {
            # Basic metrics
            'percentage': r'(\d+\.?\d*)\s*%',
            'dollar': r'\$\s*(\d+\.?\d*)\s*(billion|million|trillion)',
            'year': r'\b(20\d{2})\b',
            
            # Specific economic indicators
            'gdp_growth': r'GDP\s+growth.*?(\d+\.?\d*)\s*%',
            'inflation': r'inflation\s+rate.*?(\d+\.?\d*)\s*%',
            'unemployment': r'unemployment.*?(\d+\.?\d*)\s*%',
            'interest_rate': r'interest\s+rate.*?(\d+\.?\d*)\s*%',
            
            # AI-specific metrics
            'ai_adoption': r'AI\s+adoption.*?(\d+\.?\d*)\s*%',
            'ai_investment': r'AI\s+investment.*?\$\s*(\d+\.?\d*)\s*(billion|million)'
        }
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Main method to process a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with all extracted data
        """
        print(f"Processing: {pdf_path}")
        
        # Extract text
        text = self._extract_text(pdf_path)
        
        # Extract different types of metrics
        results = {
            'metadata': {
                'source_file': str(pdf_path),
                'extraction_date': datetime.now().isoformat(),
                'pages': self._count_pages(pdf_path)
            },
            'metrics': [],
            'summary': {}
        }
        
        # Extract all metrics
        results['metrics'].extend(self._extract_economic_indicators(text))
        results['metrics'].extend(self._extract_ai_metrics(text))
        results['metrics'].extend(self._extract_general_metrics(text))
        
        # Create summary
        results['summary'] = self._create_summary(results['metrics'])
        
        print(f"Extracted {len(results['metrics'])} metrics")
        
        return results
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract all text from PDF."""
        pdf = fitz.open(pdf_path)
        text = ""
        
        for page_num, page in enumerate(pdf):
            page_text = page.get_text()
            text += f"\n[Page {page_num + 1}]\n{page_text}"
        
        pdf.close()
        return text
    
    def _extract_economic_indicators(self, text: str) -> List[Dict]:
        """Extract standard economic indicators."""
        metrics = []
        
        # GDP Growth
        for match in re.finditer(self.patterns['gdp_growth'], text, re.IGNORECASE):
            value = float(match.group(1))
            context = self._get_context(text, match.start())
            year = self._find_year_in_context(context)
            
            metrics.append({
                'type': 'gdp_growth',
                'value': value,
                'unit': 'percentage',
                'year': year,
                'context': context,
                'confidence': 0.9  # High confidence for specific patterns
            })
        
        # Inflation
        for match in re.finditer(self.patterns['inflation'], text, re.IGNORECASE):
            value = float(match.group(1))
            context = self._get_context(text, match.start())
            year = self._find_year_in_context(context)
            
            metrics.append({
                'type': 'inflation_rate',
                'value': value,
                'unit': 'percentage',
                'year': year,
                'context': context,
                'confidence': 0.9
            })
        
        return metrics
    
    def _extract_ai_metrics(self, text: str) -> List[Dict]:
        """Extract AI-related metrics."""
        metrics = []
        
        # AI Adoption
        for match in re.finditer(self.patterns['ai_adoption'], text, re.IGNORECASE):
            value = float(match.group(1))
            context = self._get_context(text, match.start())
            year = self._find_year_in_context(context)
            
            metrics.append({
                'type': 'ai_adoption_rate',
                'value': value,
                'unit': 'percentage',
                'year': year,
                'context': context,
                'confidence': 0.85
            })
        
        # AI Investment
        for match in re.finditer(self.patterns['ai_investment'], text, re.IGNORECASE):
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            # Standardize to millions
            if unit == 'billion':
                value *= 1000
            elif unit == 'trillion':
                value *= 1000000
            
            context = self._get_context(text, match.start())
            year = self._find_year_in_context(context)
            
            metrics.append({
                'type': 'ai_investment',
                'value': value,
                'unit': 'millions_usd',
                'year': year,
                'context': context,
                'confidence': 0.85
            })
        
        return metrics
    
    def _extract_general_metrics(self, text: str) -> List[Dict]:
        """Extract general percentages and amounts."""
        metrics = []
        
        # Only extract if we have context clues
        keywords = {
            'adoption': ['adoption', 'usage', 'implementation'],
            'growth': ['growth', 'increase', 'expansion'],
            'investment': ['investment', 'funding', 'capital']
        }
        
        # General percentages
        for match in re.finditer(self.patterns['percentage'], text):
            value = float(match.group(1))
            context = self._get_context(text, match.start(), window=150)
            
            # Classify based on context
            metric_type = 'general_percentage'
            for type_name, words in keywords.items():
                if any(word in context.lower() for word in words):
                    metric_type = type_name
                    break
            
            # Only add if we can identify the year
            year = self._find_year_in_context(context)
            if year:
                metrics.append({
                    'type': metric_type,
                    'value': value,
                    'unit': 'percentage',
                    'year': year,
                    'context': context,
                    'confidence': 0.7  # Lower confidence for general patterns
                })
        
        return metrics
    
    def _get_context(self, text: str, position: int, window: int = 200) -> str:
        """Get surrounding context for a match."""
        start = max(0, position - window)
        end = min(len(text), position + window)
        context = text[start:end]
        
        # Clean up context
        context = ' '.join(context.split())  # Normalize whitespace
        context = context.replace('[Page', ' [Page')  # Fix page markers
        
        return context
    
    def _find_year_in_context(self, context: str) -> int:
        """Find year in context, return None if not found."""
        year_matches = re.findall(self.patterns['year'], context)
        
        if year_matches:
            # Return the most recent valid year
            years = [int(y) for y in year_matches if 2000 <= int(y) <= 2030]
            return max(years) if years else None
        
        return None
    
    def _count_pages(self, pdf_path: str) -> int:
        """Count pages in PDF."""
        pdf = fitz.open(pdf_path)
        pages = len(pdf)
        pdf.close()
        return pages
    
    def _create_summary(self, metrics: List[Dict]) -> Dict:
        """Create summary statistics."""
        if not metrics:
            return {}
        
        df = pd.DataFrame(metrics)
        
        summary = {
            'total_metrics': len(metrics),
            'metric_types': df['type'].value_counts().to_dict(),
            'year_range': {
                'min': df['year'].min() if 'year' in df else None,
                'max': df['year'].max() if 'year' in df else None
            },
            'confidence': {
                'mean': df['confidence'].mean() if 'confidence' in df else None,
                'min': df['confidence'].min() if 'confidence' in df else None
            }
        }
        
        return summary
    
    def save_results(self, results: Dict, output_dir: str = "extracted_data"):
        """Save results to JSON and CSV."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate filename from source
        source_name = Path(results['metadata']['source_file']).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON
        json_file = output_path / f"{source_name}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"JSON saved to: {json_file}")
        
        # Save CSV
        if results['metrics']:
            df = pd.DataFrame(results['metrics'])
            csv_file = output_path / f"{source_name}_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"CSV saved to: {csv_file}")
        
        return json_file, csv_file


# Main execution
if __name__ == "__main__":
    # Create extractor
    extractor = EconomicDataExtractor()
    
    # Process a PDF
    pdf_file = "path/to/your/economic_report.pdf"
    
    if Path(pdf_file).exists():
        # Extract data
        results = extractor.process_pdf(pdf_file)
        
        # Save results
        extractor.save_results(results)
        
        # Print summary
        print("\nExtraction Summary:")
        print(f"Total metrics: {results['summary']['total_metrics']}")
        print(f"Metric types: {results['summary']['metric_types']}")
        print(f"Year range: {results['summary']['year_range']}")
    else:
        print(f"PDF file not found: {pdf_file}")
```

---

## 11. Troubleshooting Guide {#troubleshooting}

### Common Issues and Solutions

#### Issue 1: No Data Extracted
```python
# Problem: Pattern too specific
bad_pattern = r'GDP growth rate of exactly (\d+\.?\d*)%'

# Solution: More flexible pattern
good_pattern = r'GDP\s+growth.*?(\d+\.?\d*)\s*%'
```

#### Issue 2: Wrong Values Extracted
```python
# Problem: Capturing wrong numbers
text = "In 2023, GDP grew by 3.5% (compared to 2.1% in 2022)"

# Solution: Use context to validate
def validate_metric(value, context):
    # Check if this is the main value or a comparison
    if "compared to" in context and context.index(str(value)) > context.index("compared"):
        return False  # This is the comparison value
    return True
```

#### Issue 3: Tables Not Extracting
```python
# Check Java installation
import subprocess

def check_java():
    try:
        result = subprocess.run(['java', '-version'], capture_output=True)
        print("Java is installed")
        return True
    except:
        print("Java not found. Please install Java for table extraction")
        return False
```

#### Issue 4: Memory Issues with Large PDFs
```python
def process_large_pdf(pdf_path: str, chunk_size: int = 10):
    """Process large PDFs in chunks."""
    pdf = fitz.open(pdf_path)
    total_pages = len(pdf)
    
    all_metrics = []
    
    for start_page in range(0, total_pages, chunk_size):
        end_page = min(start_page + chunk_size, total_pages)
        
        # Extract chunk
        chunk_text = ""
        for page_num in range(start_page, end_page):
            chunk_text += pdf[page_num].get_text()
        
        # Process chunk
        metrics = extract_metrics_from_text(chunk_text)
        all_metrics.extend(metrics)
        
        print(f"Processed pages {start_page+1}-{end_page}")
    
    pdf.close()
    return all_metrics
```

---

## Quick Reference Card

### Essential Patterns for Economic Data
```python
patterns = {
    'percentage': r'(\d+\.?\d*)\s*%',
    'currency': r'\$\s*(\d+\.?\d*)\s*(billion|million|thousand)?',
    'year': r'\b(19|20)\d{2}\b',
    'quarter': r'Q[1-4]\s+(\d{4})',
    'growth': r'(grew|growth|increased?)\s+(?:by\s+)?(\d+\.?\d*)\s*%',
    'decline': r'(fell|declined?|decreased?)\s+(?:by\s+)?(\d+\.?\d*)\s*%'
}
```

### Basic Extraction Function
```python
def quick_extract(pdf_path):
    # Extract text
    pdf = fitz.open(pdf_path)
    text = ""
    for page in pdf:
        text += page.get_text()
    pdf.close()
    
    # Find all percentages
    percentages = re.findall(r'(\d+\.?\d*)\s*%', text)
    
    # Find all dollar amounts
    dollars = re.findall(r'\$\s*(\d+\.?\d*)\s*(billion|million)?', text)
    
    return {
        'percentages': percentages,
        'dollar_amounts': dollars
    }
```

---

## Next Steps

1. **Practice**: Start with simple PDFs and gradually increase complexity
2. **Customize**: Adapt patterns for your specific economic reports
3. **Validate**: Always verify extracted data against the source
4. **Scale**: Build a library of extractors for different report types
5. **Automate**: Create scripts to process multiple PDFs automatically

Remember: The key to successful PDF extraction is understanding your data patterns and iterating on your extraction rules.