"""
Goldman Sachs Report Extractor

Specialized extractor for Goldman Sachs economic and AI investment reports.
Focuses on investment trends, market sizing, and economic impact metrics.
"""

import re
from typing import List, Dict, Optional
from pathlib import Path
import logging

from ..pdf_processor import BasePDFExtractor, ExtractedMetric

logger = logging.getLogger(__name__)


class GoldmanSachsExtractor(BasePDFExtractor):
    """
    Specialized extractor for Goldman Sachs research reports.
    
    Targets:
    - AI investment figures and projections
    - Market size estimates
    - Economic growth predictions
    - Sector-specific adoption rates
    - ROI and productivity metrics
    """
    
    def __init__(self):
        super().__init__()
        self.source_confidence = 0.95  # High confidence for GS research
        
    def extract(self, text: str, pdf_path: Path) -> List[ExtractedMetric]:
        """Extract metrics from Goldman Sachs reports."""
        logger.info(f"Extracting Goldman Sachs metrics from {pdf_path.name}")
        
        metrics = []
        
        # Extract different types of metrics
        metrics.extend(self._extract_investment_metrics(text))
        metrics.extend(self._extract_market_size_metrics(text))
        metrics.extend(self._extract_growth_projections(text))
        metrics.extend(self._extract_productivity_metrics(text))
        metrics.extend(self._extract_sector_metrics(text))
        
        # Add source information
        for metric in metrics:
            metric.source = "Goldman Sachs"
            metric.confidence = self.source_confidence
            
        logger.info(f"Extracted {len(metrics)} metrics from Goldman Sachs report")
        return metrics
    
    def _extract_investment_metrics(self, text: str) -> List[ExtractedMetric]:
        """Extract AI investment figures."""
        metrics = []
        
        # Pattern for investment amounts
        # "AI investment could reach $200 billion by 2025"
        # "$100bn in AI infrastructure spending"
        investment_patterns = [
            r'AI investment[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'investment in AI[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'AI infrastructure[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'capital expenditure[^.]*?AI[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
        ]
        
        for pattern in investment_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                unit = match.group(2).lower()
                
                # Normalize units
                if unit in ['billion', 'bn']:
                    value = value * 1000  # Convert to millions
                    unit = 'millions_usd'
                elif unit in ['trillion', 'tn']:
                    value = value * 1000000  # Convert to millions
                    unit = 'millions_usd'
                
                # Extract context and year
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end].replace('\n', ' ')
                
                # Look for year
                year_match = re.search(r'(20\d{2})', context)
                year = int(year_match.group(1)) if year_match else 2025
                
                # Determine investment type
                if 'infrastructure' in context.lower():
                    metric_type = 'ai_infrastructure_investment'
                elif 'capex' in context.lower() or 'capital' in context.lower():
                    metric_type = 'ai_capex'
                else:
                    metric_type = 'ai_investment'
                
                metrics.append(ExtractedMetric(
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    year=year,
                    context=context[:300],
                    sector='Technology' if 'tech' in context.lower() else None
                ))
        
        return metrics
    
    def _extract_market_size_metrics(self, text: str) -> List[ExtractedMetric]:
        """Extract AI market size estimates."""
        metrics = []
        
        # Market size patterns
        market_patterns = [
            r'AI market[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'market for AI[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'AI.*?market size[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
            r'TAM[^.]*?AI[^.]*?\$(\d+(?:\.\d+)?)\s*(billion|bn|trillion|tn)',
        ]
        
        for pattern in market_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                unit = match.group(2).lower()
                
                # Convert to standard units
                if unit in ['billion', 'bn']:
                    value = value * 1000
                    unit = 'millions_usd'
                elif unit in ['trillion', 'tn']:
                    value = value * 1000000
                    unit = 'millions_usd'
                
                context = self._get_context(text, match.start(), match.end())
                year = self._extract_year_from_context(context)
                
                metrics.append(ExtractedMetric(
                    metric_type='ai_market_size',
                    value=value,
                    unit=unit,
                    year=year,
                    context=context[:300]
                ))
        
        return metrics
    
    def _extract_growth_projections(self, text: str) -> List[ExtractedMetric]:
        """Extract GDP and economic growth projections related to AI."""
        metrics = []
        
        # Growth rate patterns
        growth_patterns = [
            r'AI.*?boost.*?GDP.*?(\d+(?:\.\d+)?)\s*%',
            r'AI.*?contribute.*?(\d+(?:\.\d+)?)\s*%.*?growth',
            r'productivity.*?AI.*?(\d+(?:\.\d+)?)\s*%',
            r'AI.*?increase.*?productivity.*?(\d+(?:\.\d+)?)\s*%',
        ]
        
        for pattern in growth_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                context = self._get_context(text, match.start(), match.end())
                
                # Determine metric type from context
                if 'gdp' in context.lower():
                    metric_type = 'ai_gdp_impact'
                elif 'productivity' in context.lower():
                    metric_type = 'ai_productivity_impact'
                else:
                    metric_type = 'ai_growth_impact'
                
                year = self._extract_year_from_context(context)
                
                metrics.append(ExtractedMetric(
                    metric_type=metric_type,
                    value=value,
                    unit='percentage',
                    year=year,
                    context=context[:300]
                ))
        
        return metrics
    
    def _extract_productivity_metrics(self, text: str) -> List[ExtractedMetric]:
        """Extract productivity and efficiency metrics."""
        metrics = []
        
        # ROI and efficiency patterns
        roi_patterns = [
            r'ROI.*?AI.*?(\d+(?:\.\d+)?)\s*%',
            r'return on.*?AI.*?(\d+(?:\.\d+)?)\s*%',
            r'AI.*?efficiency.*?(\d+(?:\.\d+)?)\s*%',
            r'cost savings.*?AI.*?(\d+(?:\.\d+)?)\s*%',
        ]
        
        for pattern in roi_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = float(match.group(1))
                context = self._get_context(text, match.start(), match.end())
                
                if 'roi' in context.lower() or 'return' in context.lower():
                    metric_type = 'ai_roi'
                elif 'savings' in context.lower():
                    metric_type = 'ai_cost_savings'
                else:
                    metric_type = 'ai_efficiency_gain'
                
                year = self._extract_year_from_context(context)
                
                metrics.append(ExtractedMetric(
                    metric_type=metric_type,
                    value=value,
                    unit='percentage',
                    year=year,
                    context=context[:300]
                ))
        
        return metrics
    
    def _extract_sector_metrics(self, text: str) -> List[ExtractedMetric]:
        """Extract sector-specific AI metrics."""
        metrics = []
        
        # Sectors to look for
        sectors = {
            'financial': ['financial services', 'banking', 'fintech'],
            'healthcare': ['healthcare', 'pharma', 'medical'],
            'retail': ['retail', 'e-commerce', 'consumer'],
            'manufacturing': ['manufacturing', 'industrial'],
            'technology': ['technology', 'software', 'tech sector']
        }
        
        # Sector adoption patterns
        for sector_key, sector_terms in sectors.items():
            for term in sector_terms:
                # Adoption rates by sector
                pattern = f'{term}[^.]*?AI[^.]*?(\\d+(?:\\.\\d+)?)\\s*%'
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    value = float(match.group(1))
                    context = self._get_context(text, match.start(), match.end())
                    
                    # Determine if it's adoption, investment, or growth
                    if 'adopt' in context.lower():
                        metric_type = 'ai_adoption_rate'
                    elif 'invest' in context.lower():
                        metric_type = 'ai_investment_rate'
                    else:
                        metric_type = 'ai_penetration_rate'
                    
                    year = self._extract_year_from_context(context)
                    
                    metrics.append(ExtractedMetric(
                        metric_type=metric_type,
                        value=value,
                        unit='percentage',
                        year=year,
                        sector=sector_key.capitalize(),
                        context=context[:300]
                    ))
        
        return metrics
    
    def _get_context(self, text: str, start: int, end: int, window: int = 200) -> str:
        """Get surrounding context for a match."""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]
        # Clean up whitespace
        context = ' '.join(context.split())
        return context
    
    def _extract_year_from_context(self, context: str) -> int:
        """Extract year from context, default to 2025 if not found."""
        # Look for 4-digit years
        year_matches = re.findall(r'\b(20\d{2})\b', context)
        if year_matches:
            # Return the first valid year found
            for year_str in year_matches:
                year = int(year_str)
                if 2020 <= year <= 2030:
                    return year
        
        # Default to 2025 for forward-looking projections
        return 2025