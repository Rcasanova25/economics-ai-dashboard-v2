"""
Stanford-Aligned PDF Extractor
Extracts economic metrics using Stanford AI Index structure as template
"""

import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import fitz  # PyMuPDF
import logging

from economic_metrics_schema import (
    EconomicMetric, MetricCategory, MetricType, Unit,
    GeographicScope, Sector, CompanySize, DataQuality,
    EXTRACTION_TARGETS, validate_metric
)


class StanfordAlignedExtractor:
    """Extract economic metrics aligned with Stanford AI Index structure"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.version = "2.0-stanford-aligned"
        
        # Geographic patterns
        self.geographic_patterns = {
            "global": ["global", "worldwide", "international"],
            "regional": ["europe", "asia", "americas", "africa", "middle east"],
            "country": ["united states", "china", "uk", "germany", "japan", "canada", "india", "france"]
        }
        
        # Chart scale pattern to filter out
        self.chart_scale_pattern = re.compile(r'^(0|10|20|30|40|50|60|70|80|90|100)%?$')
        
        # Sector patterns  
        self.sector_patterns = {
            Sector.FINANCIAL_SERVICES: ["banking", "financial services", "insurance", "fintech"],
            Sector.HEALTHCARE: ["healthcare", "medical", "pharma", "biotech"],
            Sector.MANUFACTURING: ["manufacturing", "industrial", "automotive", "aerospace"],
            Sector.TECHNOLOGY: ["technology", "software", "IT", "tech companies"],
            Sector.RETAIL: ["retail", "e-commerce", "consumer goods"]
        }
        
    def extract_from_pdf(self, pdf_path: Path) -> List[EconomicMetric]:
        """Extract all economic metrics from PDF"""
        metrics = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                
                # Extract metrics by category
                for target in EXTRACTION_TARGETS:
                    page_metrics = self._extract_metrics_from_text(
                        text, target, pdf_path.name, page_num
                    )
                    metrics.extend(page_metrics)
                    
            doc.close()
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {e}")
            
        # Validate and filter
        valid_metrics = []
        for metric in metrics:
            is_valid, reason = validate_metric(metric)
            if is_valid:
                valid_metrics.append(metric)
            else:
                self.logger.debug(f"Filtered metric: {reason}")
                
        return valid_metrics
    
    def _extract_metrics_from_text(
        self, text: str, target, source: str, page: int
    ) -> List[EconomicMetric]:
        """Extract specific metric type from text"""
        metrics = []
        
        # Split into sentences for context
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            # Quick check if sentence might contain target metric
            if not any(kw in sentence.lower() for kw in target.keywords):
                continue
                
            # Extract numeric values with context
            numeric_matches = re.finditer(
                r'(\d+(?:\.\d+)?)\s*(%|percent|billion|million|USD|companies|firms)?',
                sentence
            )
            
            for match in numeric_matches:
                value_str = match.group(1)
                unit_hint = match.group(2) or ""
                
                try:
                    value = float(value_str)
                    
                    # Skip if looks like a year
                    if 2000 <= value <= 2030 and not unit_hint:
                        continue
                        
                    # Determine unit
                    unit = self._determine_unit(unit_hint, value, target)
                    if not unit:
                        continue
                        
                    # Extract additional context
                    year = self._extract_year(sentence)
                    geo_scope, geo_detail = self._extract_geography(sentence)
                    sector, sector_detail = self._extract_sector(sentence)
                    company_size = self._extract_company_size(sentence)
                    
                    # Determine specific metric type
                    metric_type = self._determine_metric_type(sentence, target)
                    
                    # Create metric
                    metric = EconomicMetric(
                        metric_id=f"{source}_{page}_{len(metrics)}",
                        source_document=source,
                        page_number=page,
                        year=year,
                        time_period=str(year) if year else None,
                        forecast_year=self._extract_forecast_year(sentence),
                        category=target.category,
                        metric_type=metric_type,
                        value=value,
                        unit=unit,
                        geographic_scope=geo_scope,
                        geographic_detail=geo_detail,
                        sector=sector,
                        sector_detail=sector_detail,
                        company_size=company_size,
                        description=self._generate_description(sentence, metric_type),
                        methodology=self._extract_methodology(sentence),
                        sample_size=self._extract_sample_size(sentence),
                        context=sentence[:500],  # Limit context length
                        data_quality=self._assess_quality(sentence, value, unit),
                        confidence_score=self._calculate_confidence(sentence, target),
                        is_projection="forecast" in sentence.lower() or "expected" in sentence.lower(),
                        extracted_at=datetime.now(),
                        extractor_version=self.version
                    )
                    
                    # Skip chart scale artifacts
                    if self.chart_scale_pattern.match(str(value)):
                        continue
                    
                    metrics.append(metric)
                    
                except ValueError:
                    continue
                    
        return metrics
    
    def _determine_unit(self, hint: str, value: float, target) -> Optional[Unit]:
        """Determine the unit based on context"""
        hint_lower = hint.lower()
        
        if "%" in hint or "percent" in hint_lower:
            return Unit.PERCENTAGE
        elif "billion" in hint_lower:
            return Unit.USD_BILLIONS
        elif "million" in hint_lower:
            return Unit.USD_MILLIONS
        elif any(u in target.units for u in [Unit.USD, Unit.USD_MILLIONS, Unit.USD_BILLIONS]):
            # Default to expected unit for financial metrics
            if value > 1000:
                return Unit.USD_MILLIONS
            elif value < 100:
                return Unit.USD_BILLIONS
                
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year from text"""
        # Look for 4-digit years
        year_matches = re.findall(r'\b(20\d{2})\b', text)
        
        for year_str in year_matches:
            year = int(year_str)
            # Avoid citation years
            if not re.search(rf'\({year}\)', text):
                return year
                
        return None
    
    def _extract_geography(self, text: str) -> Tuple[GeographicScope, Optional[str]]:
        """Extract geographic information"""
        text_lower = text.lower()
        
        # Country name mapping for proper capitalization
        country_proper_names = {
            "united states": "United States",
            "china": "China", 
            "uk": "United Kingdom",
            "germany": "Germany",
            "japan": "Japan",
            "canada": "Canada",
            "india": "India",
            "france": "France"
        }
        
        # Check for specific countries first
        for country in self.geographic_patterns["country"]:
            if country in text_lower:
                return GeographicScope.COUNTRY, country_proper_names.get(country, country.title())
                
        # Check regions
        for region in self.geographic_patterns["regional"]:
            if region in text_lower:
                return GeographicScope.REGIONAL, region.title()
                
        # Check global
        for term in self.geographic_patterns["global"]:
            if term in text_lower:
                return GeographicScope.GLOBAL, None
                
        return GeographicScope.GLOBAL, None  # Default
    
    def _extract_sector(self, text: str) -> Tuple[Sector, Optional[str]]:
        """Extract sector information"""
        text_lower = text.lower()
        
        for sector, patterns in self.sector_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    return sector, pattern.title()
                    
        return Sector.ALL_SECTORS, None
    
    def _extract_company_size(self, text: str) -> Optional[CompanySize]:
        """Extract company size if mentioned"""
        text_lower = text.lower()
        
        if "enterprise" in text_lower or "large companies" in text_lower:
            return CompanySize.ENTERPRISE
        elif "sme" in text_lower or "small business" in text_lower:
            return CompanySize.SMB
        elif "startup" in text_lower:
            return CompanySize.STARTUP
            
        return None
    
    def _determine_metric_type(self, text: str, target) -> MetricType:
        """Determine specific metric type from context"""
        text_lower = text.lower()
        
        # Map keywords to metric types
        for metric_type in target.metric_types:
            if metric_type == MetricType.ADOPTION_RATE and "adopt" in text_lower:
                return metric_type
            elif metric_type == MetricType.JOB_POSTINGS_RATE and "job posting" in text_lower:
                return metric_type
            elif metric_type == MetricType.VC_FUNDING and ("venture" in text_lower or "funding" in text_lower):
                return metric_type
            elif metric_type == MetricType.ROI and "roi" in text_lower:
                return metric_type
                
        # Default to first type in target
        return target.metric_types[0]
    
    def _generate_description(self, text: str, metric_type: MetricType) -> str:
        """Generate a description of what the metric measures"""
        descriptions = {
            MetricType.ADOPTION_RATE: "Percentage of organizations using AI",
            MetricType.JOB_POSTINGS_RATE: "AI-related job postings as percentage of total",
            MetricType.VC_FUNDING: "Venture capital investment in AI companies",
            MetricType.OUTPUT_GAIN: "Productivity improvement from AI implementation",
            MetricType.ROI: "Return on investment from AI initiatives"
        }
        
        return descriptions.get(metric_type, "Economic metric related to AI")
    
    def _extract_methodology(self, text: str) -> Optional[str]:
        """Extract methodology if mentioned"""
        if "survey" in text.lower():
            match = re.search(r'survey\s+of\s+(\d+[\w\s]+)', text, re.I)
            if match:
                return f"Survey methodology: {match.group(1)}"
        return None
    
    def _extract_sample_size(self, text: str) -> Optional[str]:
        """Extract sample size if mentioned"""
        match = re.search(r'(\d+(?:,\d+)?)\s*(?:respondents|companies|firms|organizations)', text, re.I)
        if match:
            return match.group(0)
        return None
    
    def _assess_quality(self, text: str, value: float, unit: Unit) -> DataQuality:
        """Assess data quality based on context clarity"""
        # High quality: explicit statement with clear context
        if all(x in text.lower() for x in ["survey", "found", str(int(value))]):
            return DataQuality.HIGH
        # Low quality: vague or approximate
        elif any(x in text.lower() for x in ["approximately", "around", "estimated"]):
            return DataQuality.LOW
        else:
            return DataQuality.MEDIUM
    
    def _calculate_confidence(self, text: str, target) -> float:
        """Calculate confidence score for extraction"""
        score = 0.5  # Base score
        
        # Boost for keyword matches
        keyword_matches = sum(1 for kw in target.keywords if kw in text.lower())
        score += keyword_matches * 0.1
        
        # Boost for clear numeric statement
        if re.search(r'\d+\.?\d*\s*%', text):
            score += 0.2
            
        # Penalty for hedging language
        if any(hedge in text.lower() for hedge in ["might", "could", "possibly"]):
            score -= 0.2
            
        return min(max(score, 0.0), 1.0)
    
    def _extract_forecast_year(self, text: str) -> Optional[int]:
        """Extract forecast year if this is a projection"""
        match = re.search(r'by\s+(20\d{2})', text, re.I)
        if match:
            return int(match.group(1))
        return None


def compare_with_stanford(extracted_metrics: List[EconomicMetric], stanford_data_path: Path):
    """Compare extracted metrics with Stanford data for validation"""
    
    # Load a Stanford file for comparison
    stanford_df = pd.read_csv(stanford_data_path)
    
    print("\n=== Extraction Validation ===")
    print(f"Extracted {len(extracted_metrics)} metrics")
    print(f"Stanford file has {len(stanford_df)} rows")
    
    # Group by category
    by_category = {}
    for metric in extracted_metrics:
        cat = metric.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nMetrics by category:")
    for cat, count in by_category.items():
        print(f"  {cat}: {count}")
    
    # Check value ranges
    print("\nValue ranges by unit:")
    by_unit = {}
    for metric in extracted_metrics:
        unit = metric.unit.value
        if unit not in by_unit:
            by_unit[unit] = []
        by_unit[unit].append(metric.value)
    
    for unit, values in by_unit.items():
        print(f"  {unit}: {min(values):.2f} - {max(values):.2f}")


if __name__ == "__main__":
    # Example usage
    extractor = StanfordAlignedExtractor()
    
    # Extract from a sample PDF
    pdf_path = Path("data/raw_pdfs/mckinsey_ai_state_2024.pdf")
    if pdf_path.exists():
        metrics = extractor.extract_from_pdf(pdf_path)
        
        print(f"Extracted {len(metrics)} metrics from {pdf_path.name}")
        
        # Show sample metrics
        for i, metric in enumerate(metrics[:5]):
            print(f"\nMetric {i+1}:")
            print(f"  Category: {metric.category.value}")
            print(f"  Type: {metric.metric_type.value}")
            print(f"  Value: {metric.value} {metric.unit.value}")
            print(f"  Year: {metric.year}")
            print(f"  Geography: {metric.geographic_scope.value} - {metric.geographic_detail}")
            print(f"  Context: {metric.context[:100]}...")