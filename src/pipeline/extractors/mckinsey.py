"""
McKinsey Global Institute Report Extractor

McKinsey reports focus on:
- Business value and ROI
- Industry-specific use cases
- Implementation challenges
- Cost-benefit analysis
- Productivity impacts
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.pipeline.pdf_processor import PDFExtractor, EconomicMetricExtractor
from src.models.schema import AIAdoptionMetric, DataSource, MetricType, Unit

logger = logging.getLogger(__name__)


class McKinseyExtractor(PDFExtractor):
    """
    Specialized extractor for McKinsey reports.
    
    McKinsey reports typically have:
    - Executive summary with key insights
    - Industry deep-dives
    - Case studies with specific metrics
    - Extensive charts and exhibits
    - ROI and value calculations
    """
    
    def __init__(self, pdf_path: Path):
        super().__init__(pdf_path)
        self.source = DataSource.MCKINSEY
        
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics specific to McKinsey report structure."""
        metrics = []
        
        # 1. Extract from Executive Summary
        logger.info("Extracting from Executive Summary...")
        exec_summary_metrics = self._extract_executive_summary()
        metrics.extend(exec_summary_metrics)
        
        # 2. Extract value creation metrics
        logger.info("Extracting value creation metrics...")
        value_pages = self.find_pages_with_keyword("value")
        for page in value_pages[:5]:
            value_metrics = self._extract_value_metrics(page)
            metrics.extend(value_metrics)
        
        # 3. Extract industry-specific metrics
        logger.info("Extracting industry metrics...")
        industry_metrics = self._extract_industry_metrics()
        metrics.extend(industry_metrics)
        
        # 4. Extract ROI and cost-benefit analysis
        roi_pages = self.find_pages_with_keyword("ROI")
        if not roi_pages:
            roi_pages = self.find_pages_with_keyword("return on investment")
        
        for page in roi_pages[:3]:
            roi_metrics = self._extract_roi_metrics(page)
            metrics.extend(roi_metrics)
        
        # 5. Extract productivity metrics
        productivity_pages = self.find_pages_with_keyword("productivity")
        for page in productivity_pages[:5]:
            productivity_metrics = self._extract_productivity_metrics(page)
            metrics.extend(productivity_metrics)
        
        # 6. Extract implementation metrics
        implementation_pages = self.find_pages_with_keyword("implementation")
        for page in implementation_pages[:3]:
            implementation_metrics = self._extract_implementation_metrics(page)
            metrics.extend(implementation_metrics)
        
        # 7. Extract from exhibits and tables
        logger.info("Extracting from exhibits and tables...")
        table_metrics = self._extract_table_metrics()
        metrics.extend(table_metrics)
        
        # 8. Extract workforce and talent metrics
        talent_pages = self.find_pages_with_keyword("talent")
        workforce_pages = self.find_pages_with_keyword("workforce")
        
        for page in (talent_pages + workforce_pages)[:3]:
            workforce_metrics = self._extract_workforce_metrics(page)
            metrics.extend(workforce_metrics)
        
        # Remove duplicates
        unique_metrics = self._deduplicate_metrics(metrics)
        
        logger.info(f"Extracted {len(unique_metrics)} unique metrics from McKinsey report")
        return unique_metrics
    
    def _extract_executive_summary(self) -> List[Dict[str, Any]]:
        """Extract key metrics from executive summary."""
        metrics = []
        
        # McKinsey executive summaries are usually in first 5-7 pages
        for page_num in range(min(7, self.doc.page_count)):
            text = self.extract_text_from_page(page_num)
            
            # McKinsey-specific patterns focusing on value and impact
            patterns = {
                'value_potential': [
                    r'(?:value\s+)?potential\s+of\s+\$?(\d+\.?\d*)\s*(trillion|billion)',
                    r'\$?(\d+\.?\d*)\s*(trillion|billion)\s+(?:in\s+)?(?:annual\s+)?value',
                    r'economic\s+value.*?\$?(\d+\.?\d*)\s*(trillion|billion)'
                ],
                'productivity_gain': [
                    r'productivity\s+(?:boost|gain|increase)\s+of\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+productivity\s+improvement',
                    r'increase\s+productivity\s+by\s+(\d+\.?\d*)%'
                ],
                'cost_reduction': [
                    r'(?:reduce|cut)\s+costs?\s+by\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+cost\s+(?:reduction|savings)',
                    r'save\s+(\d+\.?\d*)%\s+(?:in\s+)?(?:operational\s+)?costs?'
                ],
                'revenue_increase': [
                    r'revenue\s+(?:growth|increase)\s+of\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+revenue\s+(?:uplift|boost)',
                    r'increase\s+revenue\s+by\s+(\d+\.?\d*)%'
                ],
                'adoption_rate': [
                    r'(\d+\.?\d*)%\s+of\s+(?:companies|organizations)\s+(?:have\s+)?(?:adopted|implemented)',
                    r'adoption\s+rate\s+of\s+(\d+\.?\d*)%'
                ],
                'time_savings': [
                    r'save\s+(\d+\.?\d*)%\s+of\s+time',
                    r'(\d+\.?\d*)%\s+time\s+(?:reduction|savings)',
                    r'reduce\s+time\s+by\s+(\d+\.?\d*)%'
                ]
            }
            
            for metric_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            value = float(match[0])
                            if len(match) > 1 and match[1]:
                                if match[1].lower() == 'trillion':
                                    value = value * 1000  # Convert to billions
                                unit = 'billions_usd'
                            else:
                                unit = 'percentage'
                        else:
                            value = float(match)
                            unit = 'percentage'
                        
                        metric = {
                            'metric_type': metric_type,
                            'value': value,
                            'unit': unit,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_context(text, pattern) or 2025,
                            'confidence': 0.9
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_value_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract value creation and business impact metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Value creation patterns
        patterns = {
            'ebitda_impact': [
                r'EBITDA\s+(?:improvement|increase)\s+of\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+EBITDA\s+(?:margin\s+)?improvement',
                r'improve\s+EBITDA\s+by\s+(\d+\.?\d*)%'
            ],
            'margin_improvement': [
                r'margin\s+(?:improvement|expansion)\s+of\s+(\d+\.?\d*)\s+(?:percentage\s+)?points?',
                r'(\d+\.?\d*)\s+(?:basis\s+)?points?\s+margin\s+improvement'
            ],
            'market_value': [
                r'market\s+value.*?\$?(\d+\.?\d*)\s*(trillion|billion)',
                r'\$?(\d+\.?\d*)\s*(trillion|billion)\s+market\s+(?:opportunity|value)'
            ],
            'customer_satisfaction': [
                r'customer\s+satisfaction\s+(?:improved|increased)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:improvement|increase)\s+in\s+customer\s+satisfaction'
            ],
            'operational_efficiency': [
                r'operational\s+efficiency\s+(?:gain|improvement)\s+of\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:more\s+)?efficient\s+operations'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value = float(match[0])
                        if len(match) > 1 and match[1]:
                            if match[1].lower() == 'trillion':
                                value = value * 1000
                            unit = 'billions_usd'
                        else:
                            unit = 'percentage_points' if 'points' in pattern else 'percentage'
                    else:
                        value = float(match)
                        unit = 'percentage_points' if 'points' in pattern else 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_industry_metrics(self) -> List[Dict[str, Any]]:
        """Extract industry-specific metrics."""
        metrics = []
        
        # McKinsey focuses on these key industries
        industries = {
            'banking': ['banking', 'financial services', 'banks'],
            'retail': ['retail', 'e-commerce', 'consumer'],
            'healthcare': ['healthcare', 'pharma', 'medical'],
            'manufacturing': ['manufacturing', 'industrial', 'automotive'],
            'technology': ['technology', 'tech', 'software'],
            'energy': ['energy', 'oil', 'utilities']
        }
        
        for industry_key, keywords in industries.items():
            # Find pages mentioning this industry
            industry_pages = []
            for keyword in keywords:
                pages = self.find_pages_with_keyword(keyword)
                industry_pages.extend(pages)
            
            # Remove duplicates and limit to first 3 pages
            industry_pages = list(set(industry_pages))[:3]
            
            for page_num in industry_pages:
                text = self.extract_text_from_page(page_num)
                
                # Industry-specific patterns
                patterns = [
                    rf'{"|".join(keywords)}.*?value.*?\$?(\d+\.?\d*)\s*(billion|million)',
                    rf'{"|".join(keywords)}.*?(\d+\.?\d*)%\s+(?:productivity|efficiency)\s+gain',
                    rf'{"|".join(keywords)}.*?save.*?\$?(\d+\.?\d*)\s*(billion|million)',
                    rf'{"|".join(keywords)}.*?(\d+\.?\d*)%\s+cost\s+reduction',
                    rf'{"|".join(keywords)}.*?(\d+\.?\d*)%\s+(?:of\s+)?companies\s+(?:using|adopted)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Determine metric type from pattern
                        if 'value' in pattern:
                            metric_type = 'industry_value'
                            value = float(match[0])
                            unit = 'billions_usd' if match[1].lower() == 'billion' else 'millions_usd'
                        elif 'productivity' in pattern or 'efficiency' in pattern:
                            metric_type = 'productivity_gain'
                            value = float(match)
                            unit = 'percentage'
                        elif 'save' in pattern:
                            metric_type = 'cost_savings'
                            value = float(match[0])
                            unit = 'billions_usd' if match[1].lower() == 'billion' else 'millions_usd'
                        elif 'cost' in pattern:
                            metric_type = 'cost_reduction'
                            value = float(match)
                            unit = 'percentage'
                        else:
                            metric_type = 'adoption_rate'
                            value = float(match)
                            unit = 'percentage'
                        
                        metric = {
                            'metric_type': metric_type,
                            'value': value,
                            'unit': unit,
                            'sector': industry_key.capitalize(),
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_context(text, pattern) or 2025,
                            'confidence': 0.8
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_roi_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract ROI and payback period metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # ROI patterns
        patterns = {
            'roi': [
                r'ROI\s+of\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:return\s+on\s+investment|ROI)',
                r'return\s+on\s+investment.*?(\d+\.?\d*)%'
            ],
            'payback_period': [
                r'payback\s+(?:period|time)\s+of\s+(\d+\.?\d*)\s+(?:months?|years?)',
                r'(\d+\.?\d*)\s+(?:month|year)\s+payback',
                r'recoup\s+investment\s+in\s+(\d+\.?\d*)\s+(?:months?|years?)'
            ],
            'irr': [
                r'IRR\s+of\s+(\d+\.?\d*)%',
                r'internal\s+rate\s+of\s+return.*?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+IRR'
            ],
            'npv': [
                r'NPV\s+of\s+\$?(\d+\.?\d*)\s*(million|billion)',
                r'net\s+present\s+value.*?\$?(\d+\.?\d*)\s*(million|billion)'
            ],
            'break_even': [
                r'break[- ]?even\s+in\s+(\d+\.?\d*)\s+(?:months?|years?)',
                r'(\d+\.?\d*)\s+(?:months?|years?)\s+to\s+break[- ]?even'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if metric_type == 'payback_period' or metric_type == 'break_even':
                        value = float(match[0]) if isinstance(match, tuple) else float(match)
                        # Determine if months or years
                        if 'month' in text[text.find(str(value)):text.find(str(value))+20].lower():
                            unit = 'months'
                        else:
                            unit = 'years'
                    elif metric_type == 'npv':
                        value = float(match[0])
                        unit = 'billions_usd' if match[1].lower() == 'billion' else 'millions_usd'
                    else:
                        value = float(match) if not isinstance(match, tuple) else float(match[0])
                        unit = 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_productivity_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract detailed productivity metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Productivity patterns
        patterns = {
            'labor_productivity': [
                r'labor\s+productivity\s+(?:increase|gain)\s+of\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|improvement)\s+in\s+labor\s+productivity'
            ],
            'output_per_hour': [
                r'output\s+per\s+hour\s+(?:increased|improved)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|gain)\s+in\s+output\s+per\s+hour'
            ],
            'automation_impact': [
                r'automation\s+(?:increased|improved)\s+productivity\s+by\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+productivity\s+(?:gain|increase)\s+from\s+automation'
            ],
            'error_reduction': [
                r'(?:reduce|decrease)\s+errors?\s+by\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:fewer|reduction\s+in)\s+errors?'
            ],
            'quality_improvement': [
                r'quality\s+(?:improved|increased)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+quality\s+improvement'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if not isinstance(match, tuple) else float(match[0])
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': 'percentage',
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_implementation_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract implementation and adoption timeline metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Implementation patterns
        patterns = {
            'implementation_time': [
                r'implementation\s+(?:time|period)\s+of\s+(\d+\.?\d*)\s+(?:months?|weeks?)',
                r'implement\s+in\s+(\d+\.?\d*)\s+(?:months?|weeks?)',
                r'(\d+\.?\d*)\s+(?:months?|weeks?)\s+(?:to\s+)?implement'
            ],
            'pilot_success': [
                r'(\d+\.?\d*)%\s+of\s+pilots?\s+(?:were\s+)?successful',
                r'pilot\s+success\s+rate\s+of\s+(\d+\.?\d*)%'
            ],
            'scaling_rate': [
                r'scale\s+to\s+(\d+\.?\d*)%\s+of\s+(?:operations|organization)',
                r'(\d+\.?\d*)%\s+(?:of\s+)?(?:company|organization)\s+(?:using|adopted)'
            ],
            'training_time': [
                r'training\s+(?:time|period)\s+of\s+(\d+\.?\d*)\s+(?:days?|weeks?)',
                r'(\d+\.?\d*)\s+(?:days?|weeks?)\s+of\s+training'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if not isinstance(match, tuple) else float(match[0])
                    
                    if 'time' in metric_type:
                        # Determine time unit
                        context = text[max(0, text.find(str(value))-50):text.find(str(value))+50]
                        if 'week' in context.lower():
                            unit = 'weeks'
                        elif 'day' in context.lower():
                            unit = 'days'
                        else:
                            unit = 'months'
                    else:
                        unit = 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.8
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_workforce_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract workforce and talent-related metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Workforce patterns
        patterns = {
            'reskilling_need': [
                r'(\d+\.?\d*)%\s+of\s+(?:workforce|employees)\s+(?:need|require)\s+reskilling',
                r'reskill\s+(\d+\.?\d*)%\s+of\s+(?:workforce|employees)'
            ],
            'talent_gap': [
                r'talent\s+gap\s+of\s+(\d+\.?\d*)\s*(?:million)?\s+(?:workers|professionals)',
                r'(\d+\.?\d*)\s*(?:million)?\s+(?:AI\s+)?talent\s+(?:gap|shortage)'
            ],
            'hiring_increase': [
                r'(?:hire|hiring)\s+(?:increased|up)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|growth)\s+in\s+(?:AI\s+)?hiring'
            ],
            'skill_premium': [
                r'(\d+\.?\d*)%\s+(?:wage|salary)\s+premium\s+for\s+AI\s+skills',
                r'AI\s+(?:professionals|workers)\s+earn\s+(\d+\.?\d*)%\s+more'
            ],
            'training_investment': [
                r'invest\s+\$?(\d+\.?\d*)\s*(billion|million)\s+in\s+(?:employee\s+)?training',
                r'\$?(\d+\.?\d*)\s*(billion|million)\s+(?:for\s+)?training\s+(?:programs|initiatives)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if 'investment' in metric_type:
                        value = float(match[0])
                        unit = 'billions_usd' if match[1].lower() == 'billion' else 'millions_usd'
                    elif 'gap' in metric_type:
                        value = float(match[0]) if isinstance(match, tuple) else float(match)
                        unit = 'millions_workers' if 'million' in text[text.find(str(value)):text.find(str(value))+20] else 'workers'
                    else:
                        value = float(match) if not isinstance(match, tuple) else float(match[0])
                        unit = 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_table_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics from McKinsey's exhibits and tables."""
        metrics = []
        
        # Extract all tables
        all_tables = self.extract_all_tables()
        
        for page_num, tables in all_tables.items():
            for table_idx, table in enumerate(tables):
                # McKinsey tables often have specific structures
                if self._is_value_impact_table(table):
                    value_metrics = self._extract_value_impact_metrics(table, page_num)
                    metrics.extend(value_metrics)
                elif self._is_use_case_table(table):
                    use_case_metrics = self._extract_use_case_metrics(table, page_num)
                    metrics.extend(use_case_metrics)
                else:
                    # General table analysis
                    table_metrics = self._analyze_table(table, page_num)
                    metrics.extend(table_metrics)
        
        return metrics
    
    def _is_value_impact_table(self, table: pd.DataFrame) -> bool:
        """Check if table contains value/impact analysis."""
        table_text = table.to_string().lower()
        value_keywords = ['value', 'impact', 'benefit', 'savings', 'roi', 'npv']
        
        return sum(1 for keyword in value_keywords if keyword in table_text) >= 2
    
    def _is_use_case_table(self, table: pd.DataFrame) -> bool:
        """Check if table contains use cases."""
        table_text = table.to_string().lower()
        use_case_keywords = ['use case', 'application', 'example', 'scenario']
        
        return any(keyword in table_text for keyword in use_case_keywords)
    
    def _extract_value_impact_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from value/impact tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Look for monetary values
                    money_match = re.search(r'\$?(\d+\.?\d*)\s*(billion|million|B|M)?', value_str)
                    if money_match:
                        amount = float(money_match.group(1))
                        unit_text = money_match.group(2) or ''
                        
                        if unit_text.lower() in ['billion', 'b']:
                            unit = 'billions_usd'
                        elif unit_text.lower() in ['million', 'm']:
                            unit = 'millions_usd'
                        else:
                            unit = 'usd'
                        
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'value_impact',
                            'value': amount,
                            'unit': unit,
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.8
                        }
                        metrics.append(metric)
                    
                    # Look for percentages
                    percent_match = re.search(r'(\d+\.?\d*)%', value_str)
                    if percent_match and not money_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'improvement_rate',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_use_case_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from use case tables."""
        metrics = []
        
        # Use case tables often have impact/value columns
        for idx, row in table.iterrows():
            use_case_name = str(idx) if idx else "Unknown"
            
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Extract any numeric values with context
                    # Percentages
                    percent_matches = re.findall(r'(\d+\.?\d*)%', value_str)
                    for percent in percent_matches:
                        metric = {
                            'metric_type': 'use_case_impact',
                            'value': float(percent),
                            'unit': 'percentage',
                            'use_case': use_case_name,
                            'metric_name': str(col),
                            'source': self.source.value,
                            'page': page_num,
                            'year': 2025,
                            'confidence': 0.7
                        }
                        metrics.append(metric)
                    
                    # Monetary values
                    money_matches = re.findall(r'\$?(\d+\.?\d*)\s*(million|billion|M|B)?', value_str)
                    for match in money_matches:
                        if match[0] and not any(match[0] in p for p in percent_matches):
                            amount = float(match[0])
                            unit_text = match[1] or ''
                            
                            if unit_text.lower() in ['billion', 'b']:
                                unit = 'billions_usd'
                            elif unit_text.lower() in ['million', 'm']:
                                unit = 'millions_usd'
                            else:
                                continue  # Skip if no clear unit
                            
                            metric = {
                                'metric_type': 'use_case_value',
                                'value': amount,
                                'unit': unit,
                                'use_case': use_case_name,
                                'metric_name': str(col),
                                'source': self.source.value,
                                'page': page_num,
                                'year': 2025,
                                'confidence': 0.7
                            }
                            metrics.append(metric)
        
        return metrics
    
    def _analyze_table(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """General table analysis for McKinsey tables."""
        metrics = []
        
        # Convert table to string for pattern matching
        table_text = table.to_string()
        
        # Check content type
        if any(word in table_text.lower() for word in ['cost', 'savings', 'reduction']):
            metrics.extend(self._extract_cost_table_metrics(table, page_num))
        elif any(word in table_text.lower() for word in ['revenue', 'growth', 'increase']):
            metrics.extend(self._extract_revenue_table_metrics(table, page_num))
        elif any(word in table_text.lower() for word in ['productivity', 'efficiency']):
            metrics.extend(self._extract_productivity_table_metrics(table, page_num))
        
        return metrics
    
    def _extract_cost_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract cost-related metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Cost reduction percentages
                    percent_match = re.search(r'(\d+\.?\d*)%', value_str)
                    if percent_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'cost_reduction',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
                    
                    # Absolute cost savings
                    money_match = re.search(r'\$?(\d+\.?\d*)\s*(million|billion|M|B)?', value_str)
                    if money_match and not percent_match:
                        amount = float(money_match.group(1))
                        unit_text = money_match.group(2) or ''
                        
                        if unit_text.lower() in ['billion', 'b']:
                            unit = 'billions_usd'
                        elif unit_text.lower() in ['million', 'm']:
                            unit = 'millions_usd'
                        else:
                            continue
                        
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'cost_savings',
                            'value': amount,
                            'unit': unit,
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_revenue_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract revenue-related metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Revenue growth percentages
                    percent_match = re.search(r'(\d+\.?\d*)%', value_str)
                    if percent_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'revenue_growth',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_productivity_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract productivity metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Productivity improvements
                    percent_match = re.search(r'(\d+\.?\d*)%', value_str)
                    if percent_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'productivity_improvement',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
                    
                    # Time savings (hours, days)
                    time_match = re.search(r'(\d+\.?\d*)\s*(hours?|days?|weeks?)', value_str)
                    if time_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'time_savings',
                            'value': float(time_match.group(1)),
                            'unit': time_match.group(2).lower(),
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.7
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_year_context(self, text: str, pattern: str) -> Optional[int]:
        """Extract year from surrounding context."""
        year_pattern = r'(20\d{2})'
        years = re.findall(year_pattern, text)
        
        if years:
            return max(int(year) for year in years)
        return None
    
    def _extract_year_from_context(self, context: str) -> Optional[int]:
        """Extract year from a context string."""
        year_match = re.search(r'(20\d{2})', context)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def _deduplicate_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate metrics, keeping highest confidence ones."""
        metric_dict = {}
        
        for metric in metrics:
            # Create unique key
            key = (
                metric.get('metric_type'),
                metric.get('value'),
                metric.get('unit'),
                metric.get('year'),
                metric.get('sector', 'global'),
                metric.get('use_case', ''),
                metric.get('context', '')[:30]
            )
            
            # Keep highest confidence
            if key not in metric_dict or metric.get('confidence', 0) > metric_dict[key].get('confidence', 0):
                metric_dict[key] = metric
        
        return list(metric_dict.values())