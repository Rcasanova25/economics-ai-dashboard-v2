"""
Enhanced PDF Extractor with Schema-Based Validation
Version: 1.0
Date: January 24, 2025

This is the new extraction system that addresses all identified issues:
- Deduplication at extraction time
- Sector-aware extraction
- Proper metric classification
- Context-based confidence scoring
- No citation years as metrics
- Validated units per metric type
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import logging
from datetime import datetime
import hashlib
import json
from dataclasses import dataclass, asdict
import fitz  # PyMuPDF

# Import our schema
from extraction_sector_metric_schema_final import (
    SectorType, MetricCategory, MetricDefinition,
    SECTOR_SCHEMA, METRIC_DEFINITIONS,
    classify_sector, validate_metric
)


@dataclass
class ExtractedMetric:
    """Data class for extracted metrics"""
    value: float
    unit: str
    metric_type: str
    sector: str
    context: str
    source_page: int
    source_paragraph: int
    confidence: float
    year: int
    extraction_method: str
    validation_issues: List[str]
    company: Optional[str] = None
    

class EnhancedPDFExtractor:
    """
    Main extraction class that implements all best practices:
    - Schema-based validation
    - Deduplication during extraction
    - Sector classification
    - Quality scoring
    """
    
    def __init__(self, pdf_path: Path, debug: bool = False):
        self.pdf_path = pdf_path
        self.pdf_name = pdf_path.name
        self.debug = debug
        
        # Set up logging
        self.logger = logging.getLogger(f"PDFExtractor.{self.pdf_name}")
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            
        # Storage for metrics
        self.extracted_metrics: List[ExtractedMetric] = []
        self.seen_hashes: Set[str] = set()  # For deduplication
        self.extraction_stats = {
            "total_pages": 0,
            "metrics_found": 0,
            "duplicates_skipped": 0,
            "low_confidence_skipped": 0,
            "citations_skipped": 0
        }
        
        # Load PDF
        self.doc = fitz.open(str(pdf_path))
        self.extraction_stats["total_pages"] = len(self.doc)
        
    def extract_all_metrics(self) -> List[Dict]:
        """
        Main extraction method that processes entire PDF
        """
        self.logger.info(f"Starting extraction from {self.pdf_name}")
        
        # Extract text with structure preservation
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            # Extract text blocks (maintains paragraph structure)
            blocks = page.get_text("blocks")
            
            for block_num, block in enumerate(blocks):
                if len(block) >= 5:  # Valid text block
                    text = block[4]  # Text content is at index 4
                    
                    # Process this text block
                    self._process_text_block(text, page_num, block_num)
                    
        # Post-processing
        self._apply_cross_validation()
        
        # Convert to dictionaries for output
        metrics_as_dicts = [asdict(m) for m in self.extracted_metrics]
        
        self.logger.info(f"Extraction complete. Found {len(metrics_as_dicts)} unique metrics")
        self.logger.info(f"Stats: {json.dumps(self.extraction_stats, indent=2)}")
        
        return metrics_as_dicts
    
    def _process_text_block(self, text: str, page_num: int, block_num: int):
        """
        Process a single text block for metrics
        """
        # Clean text
        text = self._clean_text(text)
        if len(text) < 20:  # Too short to contain meaningful metrics
            return
            
        # First, classify sector for this block
        sector, sector_confidence = classify_sector(text)
        
        # Find all numeric patterns
        numeric_patterns = self._find_numeric_patterns(text)
        
        for pattern_match in numeric_patterns:
            # Extract context around the number
            context = self._extract_context(text, pattern_match)
            
            # Parse the numeric value and potential unit
            value, unit = self._parse_numeric_value(pattern_match, context)
            
            if value is None:
                continue
                
            # Skip if this looks like a citation year
            if self._is_citation_year(value, context):
                self.extraction_stats["citations_skipped"] += 1
                continue
                
            # Classify metric type based on context
            metric_type = self._classify_metric_type(context, value, unit, sector)
            
            # Validate the metric
            validation_result = validate_metric(value, unit, metric_type, sector, context)
            
            # Calculate overall confidence
            confidence = self._calculate_confidence(
                validation_result["confidence"],
                sector_confidence,
                len(context)
            )
            
            # Skip low confidence
            if confidence < 0.3:
                self.extraction_stats["low_confidence_skipped"] += 1
                continue
                
            # Create metric object
            metric = ExtractedMetric(
                value=value,
                unit=unit,
                metric_type=metric_type,
                sector=sector.value,
                context=context,
                source_page=page_num,
                source_paragraph=block_num,
                confidence=confidence,
                year=self._extract_year(context),
                extraction_method="pattern_matching",
                validation_issues=validation_result["issues"],
                company=self._extract_company(context)
            )
            
            # Check for duplicates
            if not self._is_duplicate(metric):
                self.extracted_metrics.append(metric)
                self.extraction_stats["metrics_found"] += 1
            else:
                self.extraction_stats["duplicates_skipped"] += 1
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\,\-\%\$\(\)\:]', ' ', text)
        return text.strip()
    
    def _find_numeric_patterns(self, text: str) -> List[re.Match]:
        """Find all numeric patterns in text"""
        patterns = [
            # Percentage patterns
            r'(\d+\.?\d*)\s*(?:%|percent|percentage)',
            # Currency patterns  
            r'(?:\$|USD)?\s*(\d+\.?\d*)\s*(?:billion|million|thousand|bn|mn|k)',
            # Number with units
            r'(\d+\.?\d*)\s*(?:MW|GW|TWh|MWh|GWh)',
            # Plain numbers with context
            r'(\d+\.?\d*)\s+(?:companies|organizations|firms|employees|workers|jobs)',
            # Decimal numbers
            r'(\d+\.\d+)',
            # Whole numbers (but not years)
            r'(?<!\d)(\d{1,6})(?!\d)(?!\s*(?:year|years))'
        ]
        
        matches = []
        for pattern in patterns:
            matches.extend(re.finditer(pattern, text, re.IGNORECASE))
            
        # Sort by position to process in order
        matches.sort(key=lambda x: x.start())
        
        return matches
    
    def _extract_context(self, text: str, match: re.Match, window: int = 150) -> str:
        """Extract context around a numeric match"""
        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)
        
        # Try to align with sentence boundaries
        context = text[start:end]
        
        # Find sentence start
        sentence_start = context.rfind('.', 0, window)
        if sentence_start > 0:
            context = context[sentence_start + 1:]
            
        # Find sentence end
        sentence_end = context.find('.', window)
        if sentence_end > 0:
            context = context[:sentence_end + 1]
            
        return context.strip()
    
    def _parse_numeric_value(self, match: re.Match, context: str) -> Tuple[Optional[float], Optional[str]]:
        """Parse numeric value and determine unit"""
        try:
            # Extract the numeric part
            value_str = match.group(1) if match.lastindex else match.group(0)
            value = float(value_str.replace(',', ''))
            
            # Determine unit from context
            context_lower = context.lower()
            match_text = match.group(0).lower()
            
            # Currency units
            if any(x in match_text for x in ['billion', 'bn']):
                value *= 1000  # Convert to millions
                unit = "millions_usd"
            elif any(x in match_text for x in ['million', 'mn']):
                unit = "millions_usd"
            elif any(x in match_text for x in ['thousand', 'k']):
                value /= 1000  # Convert to millions
                unit = "millions_usd"
            # Percentage
            elif any(x in match_text for x in ['%', 'percent']):
                unit = "percentage"
            # Energy units
            elif 'gwh' in match_text:
                unit = "gwh"
            elif 'mwh' in match_text:
                unit = "mwh"
            elif 'twh' in match_text:
                unit = "twh"
            elif 'gw' in match_text:
                unit = "gigawatts"
            elif 'mw' in match_text:
                unit = "megawatts"
            # CO2 units
            elif any(x in context_lower for x in ['tons co2', 'tonnes co2', 'mt co2']):
                unit = "tons_co2"
            # Count units
            elif any(x in context_lower for x in ['companies', 'organizations', 'firms']):
                unit = "count"
            elif any(x in context_lower for x in ['employees', 'workers', 'jobs']):
                unit = "number"
            else:
                unit = "number"  # Default
                
            return value, unit
            
        except (ValueError, AttributeError):
            return None, None
    
    def _is_citation_year(self, value: float, context: str) -> bool:
        """Check if a value is likely a citation year"""
        # Check if value is in year range
        if not (1900 <= value <= 2030):
            return False
            
        # Check for citation patterns
        citation_patterns = [
            r'\(\d{4}\)',  # (2024)
            r'et al\.?\s*\(?\d{4}',  # et al. 2024
            r'[A-Z][a-z]+\s+\(\d{4}\)',  # Smith (2024)
            r'[A-Z][a-z]+\s+and\s+[A-Z][a-z]+\s*\(\d{4}',  # Smith and Jones (2024)
            r'\[\d+\]',  # [1] style citations
            r'(?:paper|study|research|article|report)\s+(?:by|from)',
        ]
        
        context_lower = context.lower()
        for pattern in citation_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True
                
        # Additional keywords that suggest citations
        citation_keywords = ['bibliography', 'references', 'cited', 'publication']
        if any(keyword in context_lower for keyword in citation_keywords):
            return True
            
        return False
    
    def _classify_metric_type(self, context: str, value: float, unit: str, 
                             sector: SectorType) -> str:
        """Classify metric type based on context and schema"""
        context_lower = context.lower()
        
        # Check each metric definition
        best_match = None
        best_score = 0
        
        for metric_key, metric_def in METRIC_DEFINITIONS.items():
            score = 0
            
            # Check if unit matches
            if unit in metric_def.valid_units:
                score += 0.3
            
            # Check required context
            if metric_def.required_context:
                matches = sum(1 for keyword in metric_def.required_context 
                            if keyword in context_lower)
                if matches > 0:
                    score += 0.5 * (matches / len(metric_def.required_context))
            
            # Check excluded context (negative score)
            if metric_def.excluded_context:
                excluded = sum(1 for keyword in metric_def.excluded_context 
                             if keyword in context_lower)
                if excluded > 0:
                    score -= 0.3
            
            # Bonus for sector alignment
            if sector in SECTOR_SCHEMA and metric_def.category in SECTOR_SCHEMA[sector]["metrics_focus"]:
                score += 0.2
                
            if score > best_score:
                best_score = score
                best_match = metric_key
                
        return best_match or "unknown_metric"
    
    def _calculate_confidence(self, validation_confidence: float, 
                            sector_confidence: float,
                            context_length: int) -> float:
        """Calculate overall confidence score"""
        # Base confidence from validation
        confidence = validation_confidence
        
        # Adjust for sector confidence
        confidence *= (0.7 + 0.3 * sector_confidence)
        
        # Adjust for context quality
        if context_length < 50:
            confidence *= 0.8
        elif context_length > 200:
            confidence *= 1.1
            
        # Cap at 0.99
        return min(confidence, 0.99)
    
    def _extract_year(self, context: str) -> int:
        """Extract year from context, avoiding citation years"""
        # Look for year patterns that aren't citations
        year_patterns = [
            r'(?:in|by|during|for)\s+(\d{4})',
            r'(\d{4})\s+(?:forecast|projection|estimate)',
            r'(?:year|FY)\s+(\d{4})',
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                year = int(match.group(1))
                if 2000 <= year <= 2030:
                    return year
                    
        # Default to 2024 if no year found
        return 2024
    
    def _extract_company(self, context: str) -> Optional[str]:
        """Extract company name from context if present"""
        # This is simplified - in production you'd use NER
        # For now, look for capitalized sequences
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        matches = re.findall(company_pattern, context)
        
        # Filter out common words
        common_words = {'The', 'This', 'These', 'That', 'Those', 'According', 'Based'}
        
        for match in matches:
            if match not in common_words and len(match) > 3:
                return match
                
        return None
    
    def _is_duplicate(self, metric: ExtractedMetric) -> bool:
        """Check if metric is duplicate using semantic hashing"""
        # Create semantic hash
        hash_components = [
            str(metric.value),
            metric.unit,
            metric.metric_type,
            metric.sector,
            str(metric.year)
        ]
        
        # For near-duplicate detection, round values
        if metric.unit == "percentage":
            hash_components[0] = str(round(metric.value, 1))
        else:
            hash_components[0] = str(round(metric.value, 0))
            
        semantic_hash = hashlib.md5('|'.join(hash_components).encode()).hexdigest()
        
        if semantic_hash in self.seen_hashes:
            # Check if this is a better quality version
            for existing in self.extracted_metrics:
                existing_hash = self._get_metric_hash(existing)
                if existing_hash == semantic_hash:
                    # Keep the one with higher confidence
                    if metric.confidence > existing.confidence:
                        self.extracted_metrics.remove(existing)
                        self.seen_hashes.add(semantic_hash)
                        return False
                    else:
                        return True
            return True
        else:
            self.seen_hashes.add(semantic_hash)
            return False
    
    def _get_metric_hash(self, metric: ExtractedMetric) -> str:
        """Get semantic hash for a metric"""
        hash_components = [
            str(metric.value),
            metric.unit,
            metric.metric_type,
            metric.sector,
            str(metric.year)
        ]
        
        if metric.unit == "percentage":
            hash_components[0] = str(round(metric.value, 1))
        else:
            hash_components[0] = str(round(metric.value, 0))
            
        return hashlib.md5('|'.join(hash_components).encode()).hexdigest()
    
    def _apply_cross_validation(self):
        """Apply cross-validation rules to extracted metrics"""
        # Group metrics by sector
        sector_metrics = {}
        for metric in self.extracted_metrics:
            if metric.sector not in sector_metrics:
                sector_metrics[metric.sector] = []
            sector_metrics[metric.sector].append(metric)
            
        # Apply sector-specific validation
        for sector, metrics in sector_metrics.items():
            # Example: Check for unrealistic adoption rates
            adoption_metrics = [m for m in metrics 
                              if m.metric_type == "ai_adoption_rate"]
            if len(adoption_metrics) > 1:
                # Flag outliers
                values = [m.value for m in adoption_metrics]
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                for metric in adoption_metrics:
                    if abs(metric.value - mean_val) > 2 * std_val:
                        metric.confidence *= 0.8
                        metric.validation_issues.append("Outlier compared to other adoption rates")
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of extraction"""
        if not self.extracted_metrics:
            return {"error": "No metrics extracted"}
            
        # Group by sector
        sector_counts = {}
        for metric in self.extracted_metrics:
            sector_counts[metric.sector] = sector_counts.get(metric.sector, 0) + 1
            
        # Group by metric type
        metric_type_counts = {}
        for metric in self.extracted_metrics:
            metric_type_counts[metric.metric_type] = metric_type_counts.get(metric.metric_type, 0) + 1
            
        # Confidence distribution
        confidences = [m.confidence for m in self.extracted_metrics]
        
        return {
            "total_metrics": len(self.extracted_metrics),
            "extraction_stats": self.extraction_stats,
            "sectors": sector_counts,
            "metric_types": metric_type_counts,
            "confidence": {
                "mean": np.mean(confidences),
                "min": np.min(confidences),
                "max": np.max(confidences),
                "low_confidence_count": sum(1 for c in confidences if c < 0.5)
            },
            "quality_indicators": {
                "duplicate_rate": self.extraction_stats["duplicates_skipped"] / 
                                (self.extraction_stats["metrics_found"] + 
                                 self.extraction_stats["duplicates_skipped"]) 
                                if self.extraction_stats["metrics_found"] > 0 else 0,
                "citation_filter_rate": self.extraction_stats["citations_skipped"] /
                                      (self.extraction_stats["metrics_found"] + 
                                       self.extraction_stats["citations_skipped"])
                                      if self.extraction_stats["metrics_found"] > 0 else 0
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test with a sample PDF
    pdf_path = Path("sample.pdf")  # Replace with actual path
    
    if pdf_path.exists():
        extractor = EnhancedPDFExtractor(pdf_path, debug=True)
        metrics = extractor.extract_all_metrics()
        
        # Print summary
        print("\nExtraction Summary:")
        print("-" * 50)
        summary = extractor.get_summary_statistics()
        print(json.dumps(summary, indent=2))
        
        # Show sample metrics
        print("\nSample Extracted Metrics:")
        print("-" * 50)
        for metric in metrics[:5]:
            print(f"Value: {metric['value']} {metric['unit']}")
            print(f"Type: {metric['metric_type']}")
            print(f"Sector: {metric['sector']}")
            print(f"Confidence: {metric['confidence']:.2f}")
            print(f"Context: {metric['context'][:100]}...")
            print()
    else:
        print(f"Please provide a valid PDF path. {pdf_path} not found.")