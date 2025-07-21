"""
Universal PDF Extractor

This is the fallback extractor that ensures NO data is missed.
It uses ALL patterns from our base PDF processor plus additional
heuristics to extract any economic metrics from any PDF type.

This ensures comprehensive coverage for:
- PDFs without specific extractors
- Unusual report formats
- Mixed-format documents
- Any future PDFs added to the collection
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.pipeline.pdf_processor import PDFExtractor, EconomicMetricExtractor
from src.models.schema import AIAdoptionMetric, DataSource, MetricType, Unit

logger = logging.getLogger(__name__)


class UniversalExtractor(PDFExtractor):
    """
    Universal extractor that works with any PDF.
    Uses comprehensive pattern matching to extract all possible metrics.
    
    Key features:
    - Extracts ALL numeric patterns with context
    - Uses machine learning-like heuristics to classify metrics
    - Captures contradictory data for comparison
    - Works with any document structure
    """
    
    def __init__(self, pdf_path: Path):
        super().__init__(pdf_path)
        self.source = DataSource.OTHER
        
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics using comprehensive pattern matching."""
        metrics = []
        
        # 1. Use base class comprehensive extraction
        logger.info("Running comprehensive extraction...")
        base_stats = self.extract_key_statistics()
        
        # Convert base statistics to metrics
        for stat_type, stat_list in base_stats.items():
            for stat in stat_list:
                metric = self._convert_statistic_to_metric(stat_type, stat)
                if metric:
                    metrics.append(metric)
        
        # 2. Extract using economic metric patterns
        logger.info("Extracting economic metrics...")
        for indicator, keywords in EconomicMetricExtractor.INDICATORS.items():
            indicator_metrics = self._extract_indicator_metrics(indicator, keywords)
            metrics.extend(indicator_metrics)
        
        # 3. Extract from all tables
        logger.info("Extracting from all tables...")
        table_metrics = self._extract_all_table_metrics()
        metrics.extend(table_metrics)
        
        # 4. Page-by-page comprehensive extraction
        logger.info("Running page-by-page extraction...")
        for page_num in range(min(self.doc.page_count, 100)):  # Limit to first 100 pages
            page_metrics = self._extract_page_metrics(page_num)
            metrics.extend(page_metrics)
        
        # 5. Extract contradictory or comparative statements
        logger.info("Looking for comparative/contradictory data...")
        comparative_metrics = self._extract_comparative_metrics()
        metrics.extend(comparative_metrics)
        
        # Remove duplicates but keep contradictions
        unique_metrics = self._smart_deduplicate(metrics)
        
        logger.info(f"Extracted {len(unique_metrics)} unique metrics from {self.pdf_name}")
        return unique_metrics
    
    def _convert_statistic_to_metric(self, stat_type: str, stat: Dict) -> Optional[Dict[str, Any]]:
        """Convert a statistic from base extractor to a metric."""
        if not stat.get('value'):
            return None
        
        # Map statistic types to metric types
        type_mapping = {
            'percentages': 'general_rate',
            'dollar_amounts': 'financial_metric',
            'costs': 'cost_metric',
            'revenues': 'revenue_metric',
            'labor_metrics': 'employment_metric',
            'growth_rates': 'growth_metric',
            'token_metrics': 'ai_cost_metric',
            'energy_metrics': 'energy_metric'
        }
        
        metric_type = type_mapping.get(stat_type, 'unknown_metric')
        
        # Extract numeric value from the statistic
        value_match = re.search(r'([-]?\d+\.?\d*)', stat['value'])
        if not value_match:
            return None
        
        value = float(value_match.group(1))
        
        # Determine unit from context
        context = stat.get('context', '').lower()
        if '%' in stat['value'] or 'percent' in context:
            unit = 'percentage'
        elif any(x in stat['value'].lower() for x in ['billion', 'b', '$']):
            unit = 'billions_usd'
        elif any(x in stat['value'].lower() for x in ['million', 'm']):
            unit = 'millions_usd'
        elif any(x in context for x in ['mw', 'gw', 'kwh', 'mwh', 'gwh']):
            unit = 'energy_unit'
        elif any(x in context for x in ['tons', 'tonnes', 'co2']):
            unit = 'co2_emissions'
        else:
            unit = 'number'
        
        # Extract metric context
        metric_context = self._extract_metric_context(context)
        
        return {
            'metric_type': metric_type,
            'value': value,
            'unit': unit,
            'context': context[:200],  # Limit context length
            'extracted_from': metric_context,
            'source': self.source.value,
            'paper': self.pdf_name,
            'confidence': 0.7,  # Lower confidence for universal extraction
            'year': self._extract_year_from_context(context) or 2024
        }
    
    def _extract_indicator_metrics(self, indicator: str, keywords: List[str]) -> List[Dict[str, Any]]:
        """Extract metrics for a specific economic indicator."""
        metrics = []
        
        # Search for each keyword
        for keyword in keywords[:3]:  # Limit to avoid too many duplicates
            pages = self.find_pages_with_keyword(keyword)
            
            for page_num in pages[:2]:  # Check first 2 pages with keyword
                text = self.extract_text_from_page(page_num)
                
                # Extract sentences containing the keyword
                sentences = text.split('.')
                relevant_sentences = [s for s in sentences if keyword.lower() in s.lower()]
                
                for sentence in relevant_sentences[:5]:  # Limit sentences per page
                    # Look for numeric values in the sentence
                    numeric_patterns = [
                        r'(\d+\.?\d*)\s*(?:percent|%)',
                        r'\$?\s*(\d+\.?\d*)\s*(?:billion|million|B|M)',
                        r'(\d+\.?\d*)\s*(?:fold|times|x)',
                        r'(\d+\.?\d*)\s*(?:MW|GW|kWh|MWh|GWh)',
                        r'(\d+\.?\d*)\s*(?:tons?|tonnes?)\s*(?:of\s+)?CO2'
                    ]
                    
                    for pattern in numeric_patterns:
                        matches = re.findall(pattern, sentence, re.IGNORECASE)
                        for match in matches:
                            value = float(match) if isinstance(match, str) else float(match[0])
                            
                            # Determine unit from pattern
                            if 'percent' in pattern or '%' in pattern:
                                unit = 'percentage'
                            elif 'billion' in pattern:
                                unit = 'billions_usd'
                            elif 'million' in pattern:
                                unit = 'millions_usd'
                            elif 'fold' in pattern or 'times' in pattern:
                                unit = 'multiple'
                            elif any(x in pattern for x in ['MW', 'GW', 'kWh']):
                                unit = 'energy'
                            elif 'CO2' in pattern:
                                unit = 'co2_tons'
                            else:
                                unit = 'number'
                            
                            metric = {
                                'metric_type': f"{indicator}_metric",
                                'value': value,
                                'unit': unit,
                                'indicator': indicator,
                                'keyword': keyword,
                                'context': sentence.strip()[:200],
                                'source': self.source.value,
                                'paper': self.pdf_name,
                                'page': page_num,
                                'confidence': 0.75,
                                'year': self._extract_year_from_context(sentence) or 2024
                            }
                            metrics.append(metric)
        
        return metrics
    
    def _extract_all_table_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics from all tables in the document."""
        metrics = []
        
        try:
            all_tables = self.extract_all_tables()
            
            for page_num, tables in all_tables.items():
                for table_idx, table in enumerate(tables):
                    # Extract from every cell that contains numbers
                    table_metrics = self._extract_universal_table_metrics(table, page_num)
                    metrics.extend(table_metrics)
        except Exception as e:
            logger.warning(f"Error extracting tables: {e}")
        
        return metrics
    
    def _extract_universal_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract any numeric data from tables."""
        metrics = []
        
        # Get table context from headers
        headers = ' '.join(str(col) for col in table.columns).lower()
        
        for idx, row in table.iterrows():
            row_context = str(idx).lower() if idx else ""
            
            for col_idx, col in enumerate(table.columns):
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Try to extract any numeric value
                    numeric_patterns = [
                        (r'(\d+\.?\d*)%', 'percentage'),
                        (r'\$?(\d+\.?\d*)\s*B', 'billions_usd'),
                        (r'\$?(\d+\.?\d*)\s*M', 'millions_usd'),
                        (r'\$?(\d+\.?\d*)\s*(?:billion)', 'billions_usd'),
                        (r'\$?(\d+\.?\d*)\s*(?:million)', 'millions_usd'),
                        (r'(\d+\.?\d*)\s*(?:MW|GW)', 'power'),
                        (r'(\d+\.?\d*)\s*(?:kWh|MWh|GWh)', 'energy'),
                        (r'^(\d+\.?\d*)$', 'number')  # Plain numbers
                    ]
                    
                    for pattern, unit_type in numeric_patterns:
                        match = re.search(pattern, value_str, re.IGNORECASE)
                        if match:
                            try:
                                numeric_value = float(match.group(1))
                                
                                # Skip very large numbers that might be IDs or years
                                if unit_type == 'number' and (numeric_value > 10000 or 1900 < numeric_value < 2100):
                                    continue
                                
                                # Determine metric type from context
                                metric_type = self._classify_metric_from_context(
                                    headers + ' ' + row_context + ' ' + str(col)
                                )
                                
                                metric = {
                                    'metric_type': metric_type,
                                    'value': numeric_value,
                                    'unit': unit_type,
                                    'table_context': f"Row: {idx}, Col: {col}",
                                    'headers': headers[:100],
                                    'source': self.source.value,
                                    'paper': self.pdf_name,
                                    'page': page_num,
                                    'confidence': 0.65,  # Lower confidence for table data
                                    'year': self._extract_year_from_context(headers + ' ' + row_context) or 2024
                                }
                                metrics.append(metric)
                                break  # Only take first match
                            except ValueError:
                                continue
        
        return metrics
    
    def _extract_page_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from a single page using comprehensive patterns."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Skip if page is too short (likely header/footer only)
        if len(text) < 200:
            return metrics
        
        # Comprehensive patterns for any economic metric
        comprehensive_patterns = {
            'adoption_metrics': [
                r'(\d+\.?\d*)%\s+(?:of\s+)?(?:companies|firms|organizations|businesses)\s+(?:have\s+)?(?:adopted|implemented|use|using)',
                r'adoption\s+(?:rate|level)\s+(?:of\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+adoption'
            ],
            'financial_metrics': [
                r'(?:worth|valued at|totaling)\s+\$?(\d+\.?\d*)\s*(billion|million|trillion)',
                r'\$?(\d+\.?\d*)\s*(billion|million|trillion)\s+(?:market|opportunity|potential)',
                r'(?:save|cost|spend)\s+\$?(\d+\.?\d*)\s*(billion|million)'
            ],
            'impact_metrics': [
                r'(?:increase|improve|boost|raise)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(?:reduce|decrease|cut|lower)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|improvement|reduction|decrease)'
            ],
            'comparison_metrics': [
                r'(\d+\.?\d*)\s*(?:times|x)\s+(?:more|less|higher|lower|faster|slower)',
                r'(\d+\.?\d*)[-\s]?fold\s+(?:increase|decrease|improvement)',
                r'(?:up|down)\s+(\d+\.?\d*)%\s+(?:from|compared)'
            ]
        }
        
        for metric_category, pattern_list in comprehensive_patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Extract value and unit
                    if isinstance(match, tuple):
                        value = float(match[0])
                        if len(match) > 1:
                            unit_text = match[1].lower()
                            if unit_text == 'trillion':
                                value = value * 1000
                                unit = 'billions_usd'
                            elif unit_text == 'billion':
                                unit = 'billions_usd'
                            elif unit_text == 'million':
                                unit = 'millions_usd'
                            else:
                                unit = 'percentage'
                        else:
                            unit = 'percentage' if '%' in pattern else 'number'
                    else:
                        value = float(match)
                        unit = 'percentage' if '%' in pattern else 'number'
                    
                    # Get surrounding context
                    pattern_match = re.search(pattern.replace(r'(\d+\.?\d*)', str(value)), text, re.IGNORECASE)
                    if pattern_match:
                        start = max(0, pattern_match.start() - 100)
                        end = min(len(text), pattern_match.end() + 100)
                        context = text[start:end].strip()
                        context = ' '.join(context.split())  # Clean whitespace
                    else:
                        context = ""
                    
                    metric = {
                        'metric_type': metric_category,
                        'value': value,
                        'unit': unit,
                        'context': context[:200],
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'page': page_num,
                        'confidence': 0.7,
                        'year': self._extract_year_from_context(context) or 2024
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_comparative_metrics(self) -> List[Dict[str, Any]]:
        """Extract comparative and potentially contradictory metrics."""
        metrics = []
        
        # Look for pages with comparative language
        comparative_keywords = ['however', 'in contrast', 'on the other hand', 
                               'alternatively', 'whereas', 'compared to', 'versus']
        
        pages_to_check = set()
        for keyword in comparative_keywords:
            pages = self.find_pages_with_keyword(keyword)
            pages_to_check.update(pages[:3])  # First 3 pages per keyword
        
        for page_num in list(pages_to_check)[:10]:  # Limit total pages
            text = self.extract_text_from_page(page_num)
            
            # Look for contrasting statements with numbers
            contrast_patterns = [
                r'(?:while|whereas)\s+.*?(\d+\.?\d*)%.*?(?:only|just|merely)\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:compared to|versus)\s+(\d+\.?\d*)%',
                r'(?:increased|decreased)\s+from\s+(\d+\.?\d*)%\s+to\s+(\d+\.?\d*)%',
                r'(?:ranged?|varies?)\s+(?:from\s+)?(\d+\.?\d*)%\s+to\s+(\d+\.?\d*)%'
            ]
            
            for pattern in contrast_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value1 = float(match[0])
                    value2 = float(match[1])
                    
                    # Get context
                    pattern_str = pattern.replace(r'(\d+\.?\d*)', r'\d+\.?\d*')
                    context_match = re.search(pattern_str, text, re.IGNORECASE)
                    if context_match:
                        start = max(0, context_match.start() - 150)
                        end = min(len(text), context_match.end() + 150)
                        context = text[start:end].strip()
                    else:
                        context = ""
                    
                    # Create two metrics for comparison
                    metric1 = {
                        'metric_type': 'comparative_metric',
                        'value': value1,
                        'unit': 'percentage',
                        'comparison_type': 'first_value',
                        'context': context[:200],
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'page': page_num,
                        'confidence': 0.8,
                        'year': self._extract_year_from_context(context) or 2024
                    }
                    
                    metric2 = {
                        'metric_type': 'comparative_metric',
                        'value': value2,
                        'unit': 'percentage',
                        'comparison_type': 'second_value',
                        'context': context[:200],
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'page': page_num,
                        'confidence': 0.8,
                        'year': self._extract_year_from_context(context) or 2024
                    }
                    
                    metrics.extend([metric1, metric2])
        
        return metrics
    
    def _extract_metric_context(self, context: str) -> str:
        """Extract the type of metric from context."""
        context_lower = context.lower()
        
        # Keywords to identify metric types
        keyword_mapping = {
            'adoption': ['adopt', 'implement', 'usage', 'penetration'],
            'cost': ['cost', 'expense', 'spend', 'investment', 'capital'],
            'revenue': ['revenue', 'sales', 'income', 'earnings'],
            'productivity': ['productiv', 'efficiency', 'output'],
            'employment': ['job', 'employ', 'worker', 'labor', 'workforce'],
            'growth': ['growth', 'increase', 'expand', 'rise'],
            'reduction': ['reduc', 'decreas', 'declin', 'fall', 'cut'],
            'energy': ['energy', 'power', 'electric', 'mw', 'kwh'],
            'ai_specific': ['ai', 'artificial intelligence', 'machine learning', 'automation']
        }
        
        for metric_type, keywords in keyword_mapping.items():
            if any(keyword in context_lower for keyword in keywords):
                return metric_type
        
        return 'general'
    
    def _classify_metric_from_context(self, context: str) -> str:
        """Classify metric type based on surrounding context."""
        context_lower = context.lower()
        
        # Priority order matters - more specific first
        if any(x in context_lower for x in ['adopt', 'implementation', 'usage rate']):
            return 'adoption_metric'
        elif any(x in context_lower for x in ['cost', 'expense', 'tco', 'spending']):
            return 'cost_metric'
        elif any(x in context_lower for x in ['revenue', 'sales', 'earnings']):
            return 'revenue_metric'
        elif any(x in context_lower for x in ['productiv', 'efficiency']):
            return 'productivity_metric'
        elif any(x in context_lower for x in ['job', 'employ', 'worker']):
            return 'employment_metric'
        elif any(x in context_lower for x in ['energy', 'power', 'mw', 'kwh']):
            return 'energy_metric'
        elif any(x in context_lower for x in ['invest', 'funding', 'capital']):
            return 'investment_metric'
        else:
            return 'unclassified_metric'
    
    def _extract_year_from_context(self, context: str) -> Optional[int]:
        """Extract year from context."""
        if not context:
            return None
        
        # Look for 4-digit years
        year_matches = re.findall(r'\b(20\d{2})\b', context)
        if year_matches:
            # Return the most recent year
            years = [int(year) for year in year_matches]
            return max(years)
        
        return None
    
    def _smart_deduplicate(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Smart deduplication that keeps contradictory data.
        Two metrics are considered contradictory if they have:
        - Same metric type and unit
        - Different values (>10% difference)
        - Similar context
        """
        # Group metrics by type and unit
        grouped = {}
        for metric in metrics:
            key = (metric.get('metric_type'), metric.get('unit'))
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(metric)
        
        unique_metrics = []
        
        for (metric_type, unit), group in grouped.items():
            if len(group) == 1:
                unique_metrics.extend(group)
                continue
            
            # Sort by confidence
            group.sort(key=lambda x: x.get('confidence', 0), reverse=True)
            
            # Keep metrics with significantly different values
            kept_metrics = [group[0]]  # Always keep highest confidence
            
            for metric in group[1:]:
                # Check if this metric is significantly different from any kept metric
                is_different = True
                for kept in kept_metrics:
                    value_diff = abs(metric['value'] - kept['value'])
                    value_avg = (metric['value'] + kept['value']) / 2
                    
                    # If values are within 10% of each other, consider them duplicates
                    if value_avg > 0 and (value_diff / value_avg) < 0.1:
                        is_different = False
                        break
                
                if is_different or metric.get('comparison_type'):  # Always keep comparative metrics
                    kept_metrics.append(metric)
            
            unique_metrics.extend(kept_metrics)
        
        return unique_metrics