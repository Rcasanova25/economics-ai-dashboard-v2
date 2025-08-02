"""
Enhanced Stanford-Aligned PDF Extractor
Improvements based on test results:
1. Better chart/table detection
2. Country-value pair extraction
3. Deduplication of chart artifacts
4. Enhanced context preservation
"""

import re
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import fitz
import logging
from collections import defaultdict

from economic_metrics_schema import (
    EconomicMetric, MetricCategory, MetricType, Unit,
    GeographicScope, Sector, CompanySize, DataQuality,
    EXTRACTION_TARGETS, validate_metric
)


class EnhancedStanfordExtractor:
    """Enhanced extractor with better pattern recognition"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.version = "2.1-enhanced"
        
        # Enhanced country patterns with common variations
        self.country_patterns = {
            "United States": ["united states", "usa", "u.s.", "us", "america"],
            "United Kingdom": ["united kingdom", "uk", "u.k.", "britain"],
            "Germany": ["germany", "german"],
            "France": ["france", "french"],
            "India": ["india", "indian"],
            "China": ["china", "chinese"],
            "Japan": ["japan", "japanese"],
            "Canada": ["canada", "canadian"],
            "Australia": ["australia", "australian"],
            "Netherlands": ["netherlands", "dutch"],
            "Singapore": ["singapore"],
            "South Korea": ["south korea", "korea", "korean"]
        }
        
        # Chart scale patterns to filter out
        self.chart_scale_pattern = re.compile(
            r'^(0|10|20|30|40|50|60|70|80|90|100)%?$|^(0\.0|1\.0|2\.0)$'
        )
        
        # Patterns that indicate a metric-country pair
        self.country_value_patterns = [
            r'([\w\s]+?)[\s:]+(\d+(?:\.\d+)?)\s*%',  # Country: 45%
            r'(\d+(?:\.\d+)?)\s*%\s+(?:in|for)\s+([\w\s]+)',  # 45% in Country
            r'([\w\s]+?)\s+\((\d+(?:\.\d+)?)\s*%\)',  # Country (45%)
        ]
        
    def extract_from_pdf(self, pdf_path: Path) -> List[EconomicMetric]:
        """Extract all economic metrics from PDF with enhanced logic"""
        metrics = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                
                # First, extract structured data (country-value pairs)
                structured_metrics = self._extract_structured_metrics(
                    text, pdf_path.name, page_num
                )
                metrics.extend(structured_metrics)
                
                # Then, extract other metrics with deduplication
                for target in EXTRACTION_TARGETS:
                    page_metrics = self._extract_metrics_from_text(
                        text, target, pdf_path.name, page_num
                    )
                    
                    # Filter out likely chart artifacts
                    filtered_metrics = self._filter_chart_artifacts(page_metrics)
                    metrics.extend(filtered_metrics)
                    
            doc.close()
            
        except Exception as e:
            self.logger.error(f"Error processing {pdf_path}: {e}")
            
        # Deduplicate and validate
        unique_metrics = self._deduplicate_metrics(metrics)
        
        valid_metrics = []
        for metric in unique_metrics:
            is_valid, reason = validate_metric(metric)
            if is_valid:
                valid_metrics.append(metric)
            else:
                self.logger.debug(f"Filtered metric: {reason}")
                
        return valid_metrics
    
    def _extract_structured_metrics(
        self, text: str, source: str, page: int
    ) -> List[EconomicMetric]:
        """Extract country-value pairs and other structured data"""
        metrics = []
        
        # Look for adoption rates by country
        adoption_by_country = self._extract_country_adoption_rates(text)
        
        for country, rate in adoption_by_country.items():
            metric = EconomicMetric(
                metric_id=f"{source}_{page}_country_{len(metrics)}",
                source_document=source,
                page_number=page,
                year=self._extract_year(text),
                time_period=None,
                forecast_year=None,
                category=MetricCategory.ADOPTION,
                metric_type=MetricType.ADOPTION_RATE,
                value=rate,
                unit=Unit.PERCENTAGE,
                geographic_scope=GeographicScope.COUNTRY,
                geographic_detail=country,
                sector=Sector.ALL_SECTORS,
                sector_detail=None,
                company_size=self._extract_company_size_from_context(text),
                description=f"GAI adoption rate in {country}",
                methodology=self._extract_methodology(text),
                sample_size=self._extract_sample_size(text),
                context=self._extract_relevant_context(text, country, rate),
                data_quality=DataQuality.HIGH,
                confidence_score=0.9,
                is_projection=False,
                extracted_at=datetime.now(),
                extractor_version=self.version
            )
            metrics.append(metric)
            
        return metrics
    
    def _extract_country_adoption_rates(self, text: str) -> Dict[str, float]:
        """Extract adoption rates by country"""
        country_rates = {}
        
        # Clean text for better matching
        text_clean = ' '.join(text.split())
        
        for country, variations in self.country_patterns.items():
            for variation in variations:
                # Try each pattern
                for pattern in self.country_value_patterns:
                    matches = re.finditer(pattern, text_clean, re.IGNORECASE)
                    
                    for match in matches:
                        if len(match.groups()) == 2:
                            # Determine which group is country vs value
                            group1, group2 = match.groups()
                            
                            if variation in group1.lower():
                                try:
                                    value = float(group2)
                                    if 0 <= value <= 100:
                                        country_rates[country] = value
                                        break
                                except ValueError:
                                    pass
                            elif variation in group2.lower():
                                try:
                                    value = float(group1)
                                    if 0 <= value <= 100:
                                        country_rates[country] = value
                                        break
                                except ValueError:
                                    pass
                                    
        return country_rates
    
    def _filter_chart_artifacts(self, metrics: List[EconomicMetric]) -> List[EconomicMetric]:
        """Filter out likely chart scale markers and artifacts"""
        filtered = []
        
        for metric in metrics:
            # Skip if value matches common chart scale pattern
            if self.chart_scale_pattern.match(str(metric.value)):
                self.logger.debug(f"Filtered chart artifact: {metric.value}")
                continue
                
            # Skip if context suggests it's a scale marker
            context_lower = metric.context.lower()
            if all(term not in context_lower for term in 
                   ['adoption', 'using', 'implemented', 'companies', 'businesses', 
                    'organizations', 'increase', 'decrease', 'growth']):
                if metric.value in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
                    continue
                    
            filtered.append(metric)
            
        return filtered
    
    def _deduplicate_metrics(self, metrics: List[EconomicMetric]) -> List[EconomicMetric]:
        """Remove duplicate metrics based on value, page, and context similarity"""
        unique = []
        seen = set()
        
        for metric in metrics:
            # Create a signature for deduplication
            sig = (
                metric.page_number,
                metric.value,
                metric.unit.value,
                metric.geographic_detail or metric.geographic_scope.value,
                metric.category.value
            )
            
            if sig not in seen:
                seen.add(sig)
                unique.append(metric)
                
        return unique
    
    def _extract_relevant_context(self, text: str, country: str, value: float) -> str:
        """Extract the most relevant context around a country-value pair"""
        # Find sentence containing both country and value
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            if country.lower() in sentence.lower() and str(value) in sentence:
                return sentence[:500]
                
        # Fallback to broader context
        text_lower = text.lower()
        country_lower = country.lower()
        
        # Find country mention and extract surrounding context
        country_pos = text_lower.find(country_lower)
        if country_pos != -1:
            start = max(0, country_pos - 100)
            end = min(len(text), country_pos + 200)
            return text[start:end].strip()
            
        return text[:500]
    
    def _extract_company_size_from_context(self, text: str) -> Optional[CompanySize]:
        """Enhanced company size extraction"""
        text_lower = text.lower()
        
        # Check for explicit size mentions
        if "large business" in text_lower or "large companies" in text_lower:
            return CompanySize.ENTERPRISE
        elif "medium business" in text_lower or "medium companies" in text_lower:
            return CompanySize.MID_MARKET
        elif "small business" in text_lower or "smb" in text_lower:
            return CompanySize.SMB
        elif "startup" in text_lower:
            return CompanySize.STARTUP
            
        # Check for employee count patterns
        emp_match = re.search(r'(\d+)[\s\+]*(employee|worker)', text_lower)
        if emp_match:
            count = int(emp_match.group(1))
            if count >= 1000:
                return CompanySize.ENTERPRISE
            elif count >= 100:
                return CompanySize.MID_MARKET
            else:
                return CompanySize.SMB
                
        return None
    
    def _extract_metrics_from_text(
        self, text: str, target, source: str, page: int
    ) -> List[EconomicMetric]:
        """Extract metrics with enhanced pattern matching"""
        metrics = []
        
        # Split into meaningful chunks (not just sentences)
        chunks = self._split_into_chunks(text)
        
        for chunk in chunks:
            # Skip if chunk doesn't contain relevant keywords
            if not any(kw in chunk.lower() for kw in target.keywords):
                continue
                
            # Enhanced numeric extraction
            numeric_data = self._extract_numeric_values(chunk, target)
            
            for value, unit, confidence in numeric_data:
                # Skip if it's a year or citation
                if self._is_year_or_citation(value, chunk):
                    continue
                    
                # Extract all dimensions
                year = self._extract_year(chunk)
                geo_scope, geo_detail = self._extract_geography_enhanced(chunk)
                sector, sector_detail = self._extract_sector_enhanced(chunk)
                company_size = self._extract_company_size_from_context(chunk)
                
                # Determine specific metric type with better logic
                metric_type = self._determine_metric_type_enhanced(chunk, target, value)
                
                metric = EconomicMetric(
                    metric_id=f"{source}_{page}_{len(metrics)}",
                    source_document=source,
                    page_number=page,
                    year=year,
                    time_period=str(year) if year else None,
                    forecast_year=self._extract_forecast_year(chunk),
                    category=target.category,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    geographic_scope=geo_scope,
                    geographic_detail=geo_detail,
                    sector=sector,
                    sector_detail=sector_detail,
                    company_size=company_size,
                    description=self._generate_contextual_description(chunk, metric_type, value),
                    methodology=self._extract_methodology(chunk),
                    sample_size=self._extract_sample_size(chunk),
                    context=chunk[:500],
                    data_quality=self._assess_quality_enhanced(chunk, value, confidence),
                    confidence_score=confidence,
                    is_projection=self._is_projection(chunk),
                    extracted_at=datetime.now(),
                    extractor_version=self.version
                )
                
                metrics.append(metric)
                
        return metrics
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into meaningful chunks (paragraphs, list items, etc.)"""
        chunks = []
        
        # Split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(para.strip()) > 20:  # Meaningful content
                chunks.append(para.strip())
                
        # Also split by bullet points or numbered lists
        list_pattern = re.compile(r'[•\-\*]\s*(.+?)(?=[•\-\*]|\n\n|$)', re.DOTALL)
        for match in list_pattern.finditer(text):
            chunks.append(match.group(1).strip())
            
        return chunks
    
    def _extract_numeric_values(
        self, text: str, target
    ) -> List[Tuple[float, Unit, float]]:
        """Extract numeric values with units and confidence"""
        values = []
        
        # Pattern for percentages with context
        pct_pattern = re.compile(
            r'(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?([\w\s]+?)(?:\s+(?:have|are|use|adopt|report))?'
        )
        
        # Pattern for financial values
        fin_pattern = re.compile(
            r'\$?\s*(\d+(?:\.\d+)?)\s*(billion|million|B|M)\s*(?:USD)?'
        )
        
        # Extract percentages
        for match in pct_pattern.finditer(text):
            value = float(match.group(1))
            context = match.group(2)
            
            # Assess confidence based on context clarity
            confidence = 0.8
            if any(kw in context.lower() for kw in ['companies', 'businesses', 'organizations']):
                confidence = 0.9
                
            values.append((value, Unit.PERCENTAGE, confidence))
            
        # Extract financial values
        for match in fin_pattern.finditer(text):
            value = float(match.group(1))
            magnitude = match.group(2).lower()
            
            unit = Unit.USD_BILLIONS if 'b' in magnitude else Unit.USD_MILLIONS
            values.append((value, unit, 0.85))
            
        return values
    
    def _is_year_or_citation(self, value: float, text: str) -> bool:
        """Check if a numeric value is likely a year or citation"""
        if 2000 <= value <= 2030:
            # Check for citation pattern
            if re.search(rf'\({int(value)}\)', text):
                return True
            # Check if it's the only number in that range
            if not re.search(r'\d+\s*%|\$\s*\d+', text):
                return True
        return False
    
    def _extract_geography_enhanced(self, text: str) -> Tuple[GeographicScope, Optional[str]]:
        """Enhanced geographic extraction"""
        text_lower = text.lower()
        
        # Check for specific countries
        for country, variations in self.country_patterns.items():
            for variation in variations:
                if variation in text_lower:
                    return GeographicScope.COUNTRY, country
                    
        # Check for regions
        regions = {
            "Europe": ["europe", "european", "eu"],
            "Asia": ["asia", "asian", "apac", "asia-pacific"],
            "North America": ["north america", "americas"],
            "Global": ["global", "worldwide", "international"]
        }
        
        for region, patterns in regions.items():
            for pattern in patterns:
                if pattern in text_lower:
                    scope = GeographicScope.GLOBAL if region == "Global" else GeographicScope.REGIONAL
                    return scope, region if scope == GeographicScope.REGIONAL else None
                    
        return GeographicScope.GLOBAL, None
    
    def _extract_sector_enhanced(self, text: str) -> Tuple[Sector, Optional[str]]:
        """Enhanced sector extraction with more patterns"""
        text_lower = text.lower()
        
        sector_patterns = {
            Sector.FINANCIAL_SERVICES: ["banking", "financial services", "insurance", "fintech", "investment"],
            Sector.HEALTHCARE: ["healthcare", "medical", "pharma", "hospital", "clinical"],
            Sector.MANUFACTURING: ["manufacturing", "industrial", "automotive", "factory", "production"],
            Sector.TECHNOLOGY: ["technology", "software", "IT", "tech", "digital", "cloud"],
            Sector.RETAIL: ["retail", "e-commerce", "consumer", "shopping", "store"],
            Sector.ENERGY: ["energy", "oil", "gas", "utilities", "power"],
            Sector.EDUCATION: ["education", "university", "school", "learning", "academic"]
        }
        
        # Count matches for each sector
        sector_scores = defaultdict(int)
        
        for sector, patterns in sector_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    sector_scores[sector] += 1
                    
        # Return sector with most matches
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            # Find which pattern matched
            for pattern in sector_patterns[best_sector]:
                if pattern in text_lower:
                    return best_sector, pattern.title()
                    
        return Sector.ALL_SECTORS, None
    
    def _determine_metric_type_enhanced(
        self, text: str, target, value: float
    ) -> MetricType:
        """Enhanced metric type determination"""
        text_lower = text.lower()
        
        # More specific patterns for each metric type
        type_patterns = {
            MetricType.ADOPTION_RATE: [
                "adopt", "using ai", "implemented", "deployed", "have ai"
            ],
            MetricType.JOB_POSTINGS_RATE: [
                "job posting", "job opening", "hiring", "recruitment", "talent"
            ],
            MetricType.VC_FUNDING: [
                "venture", "funding", "investment", "capital", "raised"
            ],
            MetricType.OUTPUT_GAIN: [
                "productivity", "output", "efficiency", "performance gain"
            ],
            MetricType.ROI: [
                "roi", "return on investment", "payback", "returns"
            ],
            MetricType.COST_REDUCTION: [
                "cost saving", "reduce cost", "cost reduction", "save"
            ],
            MetricType.GROWTH_RATE: [
                "growth", "increase", "cagr", "expansion"
            ]
        }
        
        # Score each type based on pattern matches
        type_scores = defaultdict(int)
        
        for metric_type in target.metric_types:
            if metric_type in type_patterns:
                for pattern in type_patterns[metric_type]:
                    if pattern in text_lower:
                        type_scores[metric_type] += 1
                        
        # Return highest scoring type
        if type_scores:
            return max(type_scores, key=type_scores.get)
            
        return target.metric_types[0]
    
    def _generate_contextual_description(
        self, text: str, metric_type: MetricType, value: float
    ) -> str:
        """Generate description based on actual context"""
        text_lower = text.lower()
        
        # Try to extract what the percentage/value represents
        patterns = [
            rf'{value}%?\s+of\s+([\w\s]+?)(?:\s+(?:have|are|use))',
            rf'([\w\s]+?)\s+(?:is|are|was|were)\s+{value}%?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return f"{match.group(1).strip()} - {metric_type.value}"
                
        # Fallback to generic description
        return f"{metric_type.value} metric: {value}"
    
    def _assess_quality_enhanced(
        self, text: str, value: float, confidence: float
    ) -> DataQuality:
        """Enhanced quality assessment"""
        if confidence >= 0.85:
            return DataQuality.HIGH
        elif confidence >= 0.7:
            return DataQuality.MEDIUM
        else:
            return DataQuality.LOW
    
    def _is_projection(self, text: str) -> bool:
        """Check if metric is a future projection"""
        projection_terms = [
            "forecast", "expected", "projected", "will", "by 20",
            "anticipate", "predict", "estimate", "outlook"
        ]
        
        text_lower = text.lower()
        return any(term in text_lower for term in projection_terms)
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract year with better citation filtering"""
        # Look for year in specific contexts
        year_patterns = [
            r'in\s+(20\d{2})',
            r'as\s+of\s+(20\d{2})',
            r'(20\d{2})\s+survey',
            r'(20\d{2})\s+data',
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
                
        # Fallback to any 4-digit year not in parentheses
        years = re.findall(r'\b(20\d{2})\b', text)
        for year_str in years:
            year = int(year_str)
            if not re.search(rf'\({year}\)', text):
                return year
                
        return None
    
    def _extract_methodology(self, text: str) -> Optional[str]:
        """Extract methodology information"""
        method_patterns = [
            r'survey\s+of\s+([\w\s,]+)',
            r'based\s+on\s+([\w\s,]+)',
            r'analysis\s+of\s+([\w\s,]+)',
            r'study\s+of\s+([\w\s,]+)',
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
                
        return None
    
    def _extract_sample_size(self, text: str) -> Optional[str]:
        """Extract sample size information"""
        patterns = [
            r'(\d+[,\d]*)\s*(?:respondents|companies|firms|organizations|businesses)',
            r'n\s*=\s*(\d+[,\d]*)',
            r'sample\s+of\s+(\d+[,\d]*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
                
        return None
    
    def _extract_forecast_year(self, text: str) -> Optional[int]:
        """Extract target year for projections"""
        patterns = [
            r'by\s+(20\d{2})',
            r'in\s+(20\d{2})',
            r'through\s+(20\d{2})',
        ]
        
        # Only if text contains projection indicators
        if self._is_projection(text):
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    year = int(match.group(1))
                    if year > datetime.now().year:
                        return year
                        
        return None