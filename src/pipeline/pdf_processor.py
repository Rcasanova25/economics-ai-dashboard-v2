"""
PDF Processing Pipeline - Base Classes

As an economist, you're used to extracting data from reports manually.
This module automates that process using modern Python libraries.

Key Libraries for PDF Processing:
1. PyMuPDF (fitz) - Fast, reliable text extraction
2. pandas - For handling tabular data (you know this from economic analysis)
3. re (regex) - For finding patterns in text (like "GDP growth: X%")
4. tabula-py - Best tool for extracting tables from PDFs
5. camelot-py - Alternative for complex table extraction
"""

import fitz  # PyMuPDF
import pandas as pd
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from abc import ABC, abstractmethod
import tabula  # For table extraction - much better than manual parsing!

# Set up logging - this helps us debug when things go wrong
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor(ABC):
    """
    Base class for PDF extraction.
    Think of this as a template for all PDF extractors.
    
    In economics terms: This is like having a standard methodology
    that you adapt for different types of reports.
    """
    
    def __init__(self, pdf_path: Path):
        """Initialize with a PDF file path"""
        self.pdf_path = Path(pdf_path)
        self.pdf_name = self.pdf_path.stem
        self.doc = None
        self._metadata = {}
        
    def __enter__(self):
        """Open the PDF when entering context"""
        try:
            self.doc = fitz.open(str(self.pdf_path))
            logger.info(f"Opened PDF: {self.pdf_name} ({self.doc.page_count} pages)")
            return self
        except Exception as e:
            logger.error(f"Failed to open PDF {self.pdf_path}: {e}")
            raise
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the PDF when exiting context"""
        if self.doc:
            self.doc.close()
            
    @abstractmethod
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """
        Extract economic metrics from the PDF.
        Each extractor must implement this based on the PDF structure.
        """
        pass
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page"""
        try:
            page = self.doc[page_num]
            return page.get_text()
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num}: {e}")
            return ""
    
    def extract_all_text(self) -> str:
        """Extract text from entire PDF"""
        all_text = []
        for page_num in range(self.doc.page_count):
            all_text.append(self.extract_text_from_page(page_num))
        return "\n".join(all_text)
    
    def find_pages_with_keyword(self, keyword: str, case_sensitive: bool = False) -> List[int]:
        """
        Find all pages containing a keyword.
        Useful for finding specific sections like "Executive Summary" or "GDP Analysis"
        """
        pages = []
        for page_num in range(self.doc.page_count):
            text = self.extract_text_from_page(page_num)
            if not case_sensitive:
                if keyword.lower() in text.lower():
                    pages.append(page_num)
            else:
                if keyword in text:
                    pages.append(page_num)
        return pages
    
    def extract_tables_from_page(self, page_num: int) -> List[pd.DataFrame]:
        """
        Extract tables from a specific page using tabula-py.
        This is the BEST method for extracting tables from PDFs.
        
        tabula-py uses Java's tabula-java library which is specifically
        designed for table extraction and handles:
        - Complex table structures
        - Merged cells
        - Multi-line cells
        - Tables spanning multiple pages
        """
        tables = []
        try:
            # Extract tables from specific page
            # lattice=True works best for tables with clear borders
            # stream=True works for tables without borders
            # We'll try both methods
            
            # Method 1: Lattice (for bordered tables)
            try:
                tables_lattice = tabula.read_pdf(
                    str(self.pdf_path),
                    pages=page_num + 1,  # tabula uses 1-based indexing
                    lattice=True,
                    pandas_options={'header': None}
                )
                tables.extend(tables_lattice)
                logger.info(f"Extracted {len(tables_lattice)} bordered tables from page {page_num}")
            except Exception as e:
                logger.debug(f"Lattice method failed on page {page_num}: {e}")
            
            # Method 2: Stream (for borderless tables)
            try:
                tables_stream = tabula.read_pdf(
                    str(self.pdf_path),
                    pages=page_num + 1,
                    stream=True,
                    pandas_options={'header': None}
                )
                # Only add if we didn't already get these tables
                if not tables:
                    tables.extend(tables_stream)
                    logger.info(f"Extracted {len(tables_stream)} borderless tables from page {page_num}")
            except Exception as e:
                logger.debug(f"Stream method failed on page {page_num}: {e}")
                
            # Clean up tables
            cleaned_tables = []
            for table in tables:
                if not table.empty and len(table) > 1:  # Skip empty or single-row tables
                    # Basic cleaning
                    table = table.dropna(how='all')  # Remove empty rows
                    table = table.dropna(axis=1, how='all')  # Remove empty columns
                    if not table.empty:
                        cleaned_tables.append(table)
                        
            return cleaned_tables
            
        except Exception as e:
            logger.error(f"Error extracting tables from page {page_num}: {e}")
            return []
    
    def extract_all_tables(self) -> Dict[int, List[pd.DataFrame]]:
        """Extract all tables from the PDF"""
        all_tables = {}
        
        try:
            # Try to extract all tables at once (more efficient)
            tables = tabula.read_pdf(
                str(self.pdf_path),
                pages='all',
                multiple_tables=True,
                lattice=True
            )
            
            # Group by page (this is approximate)
            for i, table in enumerate(tables):
                if not table.empty:
                    all_tables[i] = [table]
                    
            logger.info(f"Extracted {len(tables)} tables from entire PDF")
            
        except Exception as e:
            logger.warning(f"Bulk extraction failed, trying page by page: {e}")
            # Fall back to page-by-page extraction
            for page_num in range(self.doc.page_count):
                page_tables = self.extract_tables_from_page(page_num)
                if page_tables:
                    all_tables[page_num] = page_tables
                    
        return all_tables
    
    def extract_numbers_with_context(self, pattern: str, context_words: int = 10) -> List[Dict[str, Any]]:
        """
        Extract numbers matching a pattern along with surrounding context.
        
        Example pattern: r'(\d+\.?\d*)\s*%' finds percentages
        This is like highlighting key statistics in a report.
        """
        results = []
        text = self.extract_all_text()
        
        # Find all matches
        for match in re.finditer(pattern, text):
            start = max(0, match.start() - context_words * 6)  # Rough estimate
            end = min(len(text), match.end() + context_words * 6)
            
            context = text[start:end].strip()
            context = ' '.join(context.split())  # Clean up whitespace
            
            results.append({
                'value': match.group(0),
                'context': context,
                'position': match.start()
            })
            
        return results
    
    def extract_key_statistics(self) -> Dict[str, List[Dict]]:
        """
        Extract common economic statistics including AI-specific metrics.
        This method looks for patterns commonly found in economic reports.
        """
        statistics = {
            'percentages': [],
            'dollar_amounts': [],
            'costs': [],  # NEW: Cost analysis
            'revenues': [],  # NEW: Revenue analysis
            'labor_metrics': [],  # NEW: Labor/workforce metrics
            'growth_rates': [],
            'years': [],
            'token_metrics': [],  # NEW: For AI token costs
            'energy_metrics': []  # NEW: Energy consumption metrics
        }
        
        # Extract percentages with context
        percentages = self.extract_numbers_with_context(r'(\d+\.?\d*)\s*%')
        statistics['percentages'] = percentages
        
        # Extract dollar amounts (billions/millions)
        dollar_pattern = r'\$\s*(\d+\.?\d*)\s*(billion|million|thousand|B|M|K)?'
        dollars = self.extract_numbers_with_context(dollar_pattern)
        statistics['dollar_amounts'] = dollars
        
        # Extract costs (including total cost of ownership)
        cost_patterns = [
            r'(?:total\s+)?cost(?:s)?\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)\s*(billion|million|B|M)?',
            r'TCO\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)\s*(billion|million|B|M)?',
            r'(?:training|education)\s+cost(?:s)?\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)',
            r'cost\s+per\s+(?:employee|worker|user)\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)'
        ]
        for pattern in cost_patterns:
            costs = self.extract_numbers_with_context(pattern)
            statistics['costs'].extend(costs)
        
        # Extract revenues
        revenue_patterns = [
            r'revenue(?:s)?\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)\s*(billion|million|B|M)?',
            r'profit(?:s)?\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)\s*(billion|million|B|M)?',
            r'earnings\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)\s*(billion|million|B|M)?'
        ]
        for pattern in revenue_patterns:
            revenues = self.extract_numbers_with_context(pattern)
            statistics['revenues'].extend(revenues)
        
        # Extract labor/workforce metrics
        labor_patterns = [
            r'(\d+\.?\d*)\s*(?:million|thousand)?\s*(?:jobs|workers|employees)',
            r'workforce\s+(?:of|:)?\s*(\d+\.?\d*)\s*(?:million|thousand)?',
            r'employment\s+(?:rate|level)\s+(?:of|:)?\s*(\d+\.?\d*)\s*%',
            r'(?:un)?employment\s+(?:rate)?\s+(?:of|:)?\s*(\d+\.?\d*)\s*%',
            r'labor\s+(?:force|productivity)\s+(?:growth|increase|decrease)\s+(?:of|:)?\s*(\d+\.?\d*)\s*%'
        ]
        for pattern in labor_patterns:
            labor = self.extract_numbers_with_context(pattern)
            statistics['labor_metrics'].extend(labor)
        
        # Extract token/tokenization metrics (AI-specific)
        token_patterns = [
            r'(\d+\.?\d*)\s*(?:billion|million|B|M)?\s*tokens',
            r'token(?:s)?\s+(?:cost|price)\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)',
            r'cost\s+per\s+(?:thousand|million)\s+tokens?\s+(?:of|:)?\s*\$?\s*(\d+\.?\d*)'
        ]
        for pattern in token_patterns:
            tokens = self.extract_numbers_with_context(pattern)
            statistics['token_metrics'].extend(tokens)
        
        # Extract energy consumption metrics (AI-specific)
        energy_patterns = [
            r'(\d+\.?\d*)\s*(?:MW|megawatts?|GW|gigawatts?|kWh|MWh|GWh)',
            r'energy\s+consumption\s+(?:of|:)?\s*(\d+\.?\d*)\s*(?:MW|GW|kWh|MWh|GWh)?',
            r'power\s+(?:usage|consumption|requirement)\s+(?:of|:)?\s*(\d+\.?\d*)\s*(?:MW|GW|watts?)?',
            r'(\d+\.?\d*)\s*(?:tons?|tonnes?)\s+(?:of\s+)?CO2',
            r'carbon\s+(?:footprint|emissions?)\s+(?:of|:)?\s*(\d+\.?\d*)\s*(?:tons?|tonnes?)',
            r'electricity\s+(?:usage|consumption)\s+(?:of|:)?\s*(\d+\.?\d*)',
            r'data\s+center\s+(?:energy|power)\s+(?:usage|consumption)\s+(?:of|:)?\s*(\d+\.?\d*)',
            r'training\s+(?:energy|power)\s+(?:consumption|usage)\s+(?:of|:)?\s*(\d+\.?\d*)',
            r'inference\s+(?:energy|power)\s+(?:consumption|usage)\s+(?:of|:)?\s*(\d+\.?\d*)'
        ]
        for pattern in energy_patterns:
            energy = self.extract_numbers_with_context(pattern)
            statistics['energy_metrics'].extend(energy)
        
        # Extract years (useful for time series data)
        year_pattern = r'\b(19\d{2}|20\d{2})\b'  # Extended to include 1900s
        years = self.extract_numbers_with_context(year_pattern)
        statistics['years'] = years
        
        # Extract growth rates (e.g., "grew by X%", "increased X%")
        growth_pattern = r'(grew|increased|rose|gained|expanded|decreased|fell|declined|contracted)\s+(?:by\s+)?(\d+\.?\d*)\s*%'
        growth = self.extract_numbers_with_context(growth_pattern)
        statistics['growth_rates'] = growth
        
        return statistics


class EconomicMetricExtractor:
    """
    Specialized class for extracting specific economic metrics.
    This is what you'll use most often for economic reports.
    """
    
    # Updated economic indicators with your suggestions
    INDICATORS = {
        'gdp': ['GDP', 'gross domestic product', 'economic output'],
        'inflation': ['inflation', 'CPI', 'consumer price index', 'price level'],
        'unemployment': ['unemployment', 'jobless rate', 'employment rate'],
        'investment': ['investment', 'capital formation', 'R&D spending'],
        'productivity': ['productivity', 'output per worker', 'efficiency'],
        'adoption': ['adoption rate', 'penetration', 'usage rate', 'implementation'],
        # NEW INDICATORS based on your request:
        'cost': ['cost', 'total cost', 'total cost of ownership', 'TCO', 'expense', 'expenditure'],
        'revenue': ['revenue', 'sales', 'income', 'earnings', 'turnover'],
        'profit': ['profit', 'margin', 'profitability', 'net income', 'EBITDA'],
        'labor': ['labor', 'workforce', 'employment', 'workers', 'employees', 'human capital'],
        'training': ['training', 'education', 'upskilling', 'reskilling', 'learning'],
        'tokens': ['tokens', 'tokenization', 'token cost', 'API calls', 'compute units'],
        'energy': ['energy', 'power', 'electricity', 'consumption', 'MW', 'GW', 'kWh', 'carbon', 'CO2', 'emissions', 'sustainability']
    }
    
    @staticmethod
    def extract_metric_value(text: str, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract a specific metric value from text with improved pattern matching.
        
        Example: extract_metric_value(text, "GDP growth")
        might return {"value": 2.5, "unit": "%", "period": "2024", "context": "..."}
        """
        # Normalize text and metric name
        text_lower = text.lower()
        metric_lower = metric_name.lower()
        
        # Look for the metric
        if metric_lower not in text_lower:
            return None
            
        # Find sentences containing the metric
        sentences = text.split('.')
        relevant_sentences = [s for s in sentences if metric_lower in s.lower()]
        
        if not relevant_sentences:
            return None
            
        # Extract numbers from relevant sentences
        results = []
        for sentence in relevant_sentences:
            # Enhanced patterns for better extraction
            patterns = [
                # Percentage patterns
                rf'{metric_name}.*?(\d+\.?\d*)\s*%',
                rf'(\d+\.?\d*)\s*%.*?{metric_name}',
                rf'{metric_name}\s+(?:was|is|reached|hit)\s+(\d+\.?\d*)\s*%',
                
                # Dollar amount patterns
                rf'{metric_name}.*?\$\s*(\d+\.?\d*)\s*(billion|million|thousand|B|M|K)?',
                rf'\$\s*(\d+\.?\d*)\s*(billion|million|thousand|B|M|K)?.*?{metric_name}',
                
                # Numeric patterns (no unit)
                rf'{metric_name}.*?(\d+\.?\d*)\s+(?:points|units|times)',
                rf'(\d+\.?\d*)\s+(?:points|units|times).*?{metric_name}',
                
                # Year-over-year patterns
                rf'{metric_name}.*?(\d+\.?\d*)\s*%\s*(?:YoY|year-over-year|y/y)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                if matches:
                    for match in matches:
                        result = {
                            'metric': metric_name,
                            'value': match[0] if isinstance(match, tuple) else match,
                            'unit': match[1] if isinstance(match, tuple) and len(match) > 1 else 'number',
                            'context': sentence.strip()
                        }
                        
                        # Try to extract time period
                        year_match = re.search(r'(19\d{2}|20\d{2})', sentence)
                        if year_match:
                            result['year'] = int(year_match.group(1))
                            
                        # Try to extract quarter/month
                        quarter_match = re.search(r'(Q[1-4]|first|second|third|fourth)\s+quarter', sentence, re.IGNORECASE)
                        if quarter_match:
                            result['quarter'] = quarter_match.group(1)
                            
                        results.append(result)
                    
        return results if results else None
    
    @staticmethod
    def extract_time_series_data(text: str, metric_name: str) -> pd.DataFrame:
        """
        Sophisticated extraction of time series data for a metric.
        Returns a DataFrame with years and values, handling various formats.
        
        This handles patterns like:
        - "GDP grew from 2.1% in 2020 to 3.5% in 2023"
        - "2019: $1.2B, 2020: $1.5B, 2021: $2.1B"
        - Table-like structures in text
        """
        data = []
        metric_lower = metric_name.lower()
        
        # Pattern 1: Year followed by metric and value
        pattern1 = r'(?:in\s+)?(\d{4}),?\s+(?:the\s+)?' + metric_name + r'.*?(\d+\.?\d*)\s*(%|billion|million|B|M)?'
        matches1 = re.findall(pattern1, text, re.IGNORECASE)
        
        for year, value, unit in matches1:
            data.append({
                'year': int(year),
                'value': float(value),
                'unit': unit or 'number',
                'metric': metric_name
            })
        
        # Pattern 2: Metric followed by year and value
        pattern2 = metric_name + r'.*?(\d+\.?\d*)\s*(%|billion|million|B|M)?\s+.*?(\d{4})'
        matches2 = re.findall(pattern2, text, re.IGNORECASE)
        
        for value, unit, year in matches2:
            data.append({
                'year': int(year),
                'value': float(value),
                'unit': unit or 'number',
                'metric': metric_name
            })
        
        # Pattern 3: Year: value format (common in tables converted to text)
        pattern3 = r'(\d{4})\s*:\s*\$?\s*(\d+\.?\d*)\s*(%|billion|million|B|M)?'
        if metric_lower in text.lower():
            # Find the section about this metric
            lines = text.split('\n')
            metric_section = []
            capture = False
            
            for line in lines:
                if metric_lower in line.lower():
                    capture = True
                elif capture and line.strip() == '':
                    break
                elif capture:
                    metric_section.append(line)
            
            section_text = '\n'.join(metric_section)
            matches3 = re.findall(pattern3, section_text)
            
            for year, value, unit in matches3:
                data.append({
                    'year': int(year),
                    'value': float(value),
                    'unit': unit or 'number',
                    'metric': metric_name
                })
        
        # Pattern 4: Range format "grew from X in YEAR1 to Y in YEAR2"
        pattern4 = r'(?:grew|increased|decreased|fell)\s+from\s+(\d+\.?\d*)\s*(%|billion|million|B|M)?\s+in\s+(\d{4})\s+to\s+(\d+\.?\d*)\s*(%|billion|million|B|M)?\s+in\s+(\d{4})'
        matches4 = re.findall(pattern4, text, re.IGNORECASE)
        
        for value1, unit1, year1, value2, unit2, year2 in matches4:
            data.append({
                'year': int(year1),
                'value': float(value1),
                'unit': unit1 or unit2 or 'number',
                'metric': metric_name
            })
            data.append({
                'year': int(year2),
                'value': float(value2),
                'unit': unit2 or unit1 or 'number',
                'metric': metric_name
            })
        
        # Remove duplicates and sort by year
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.drop_duplicates(subset=['year', 'metric'])
            df = df.sort_values('year')
            
        return df


class PDFProcessingPipeline:
    """
    Main pipeline for processing multiple PDFs.
    This orchestrates the entire extraction process.
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        
    def process_pdf(self, pdf_path: Path, extractor_class: type) -> Dict[str, Any]:
        """
        Process a single PDF using the specified extractor.
        
        This is like applying your analysis methodology to one report.
        """
        logger.info(f"Processing {pdf_path.name} with {extractor_class.__name__}")
        
        try:
            with extractor_class(pdf_path) as extractor:
                # Extract metrics
                metrics = extractor.extract_metrics()
                
                # Extract general statistics
                stats = extractor.extract_key_statistics()
                
                # Extract all tables
                tables = extractor.extract_all_tables()
                
                # Convert tables to serializable format
                tables_data = {}
                for page_num, page_tables in tables.items():
                    tables_data[f"page_{page_num}"] = [
                        table.to_dict('records') for table in page_tables
                    ]
                
                result = {
                    'pdf_name': pdf_path.name,
                    'pdf_path': str(pdf_path),
                    'extraction_date': datetime.now().isoformat(),
                    'metrics': metrics,
                    'statistics': stats,
                    'tables': tables_data,
                    'page_count': extractor.doc.page_count if extractor.doc else 0
                }
                
                # Save individual result
                output_file = self.output_dir / f"{pdf_path.stem}_extracted.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                    
                logger.info(f"Saved extraction results to {output_file}")
                return result
                
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")
            return {
                'pdf_name': pdf_path.name,
                'error': str(e),
                'extraction_date': datetime.now().isoformat()
            }
    
    def process_all_pdfs(self, pdf_dir: Path, extractor_mapping: Dict[str, type]) -> List[Dict]:
        """
        Process all PDFs in a directory.
        
        extractor_mapping maps PDF name patterns to specific extractors.
        Example: {"stanford": StanfordHAIExtractor, "oecd": OECDExtractor}
        """
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            # Determine which extractor to use
            extractor_class = PDFExtractor  # Default
            
            for pattern, extractor in extractor_mapping.items():
                if pattern.lower() in pdf_path.name.lower():
                    extractor_class = extractor
                    break
                    
            # Process the PDF
            result = self.process_pdf(pdf_path, extractor_class)
            self.results.append(result)
            
        # Save summary
        summary_file = self.output_dir / "extraction_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_pdfs': len(pdf_files),
                'successful': len([r for r in self.results if 'error' not in r]),
                'failed': len([r for r in self.results if 'error' in r]),
                'extraction_date': datetime.now().isoformat(),
                'results': self.results
            }, f, indent=2)
            
        logger.info(f"Processing complete. Summary saved to {summary_file}")
        return self.results