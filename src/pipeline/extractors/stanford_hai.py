"""
Stanford HAI AI Index Report Extractor

The Stanford HAI AI Index is one of the most comprehensive reports on AI adoption.
It contains rich data on:
- AI adoption rates by country and industry
- Investment trends
- Research output metrics
- Labor market impacts
- Cost trends
- Energy consumption (increasingly important)
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.pipeline.pdf_processor import PDFExtractor, EconomicMetricExtractor
from src.models.schema import AIAdoptionMetric, DataSource, MetricType, Unit

logger = logging.getLogger(__name__)


class StanfordHAIExtractor(PDFExtractor):
    """
    Specialized extractor for Stanford HAI AI Index reports.
    
    These reports typically have:
    - Executive summary with key statistics
    - Chapter-based organization
    - Extensive data tables
    - Consistent formatting across years
    """
    
    def __init__(self, pdf_path: Path):
        super().__init__(pdf_path)
        self.source = DataSource.STANFORD_HAI
        
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """
        Extract metrics specific to Stanford HAI report structure.
        """
        metrics = []
        
        # 1. Extract from Executive Summary (usually in first 10 pages)
        logger.info("Extracting from Executive Summary...")
        exec_summary_metrics = self._extract_executive_summary()
        metrics.extend(exec_summary_metrics)
        
        # 2. Extract from specific chapters
        logger.info("Extracting from chapters...")
        
        # Chapter on Industry Adoption (look for "Industry" or "Corporate")
        industry_pages = self.find_pages_with_keyword("industry adoption")
        if not industry_pages:
            industry_pages = self.find_pages_with_keyword("corporate AI")
        
        for page in industry_pages[:5]:  # Check first 5 matching pages
            chapter_metrics = self._extract_industry_metrics(page)
            metrics.extend(chapter_metrics)
        
        # Chapter on Investment (look for "Investment" or "Funding")
        investment_pages = self.find_pages_with_keyword("investment")
        for page in investment_pages[:5]:
            investment_metrics = self._extract_investment_metrics(page)
            metrics.extend(investment_metrics)
        
        # Chapter on Labor/Jobs
        labor_pages = self.find_pages_with_keyword("labor market")
        if not labor_pages:
            labor_pages = self.find_pages_with_keyword("employment")
        
        for page in labor_pages[:5]:
            labor_metrics = self._extract_labor_metrics(page)
            metrics.extend(labor_metrics)
        
        # 3. Extract from data tables
        logger.info("Extracting from tables...")
        table_metrics = self._extract_table_metrics()
        metrics.extend(table_metrics)
        
        # 4. Extract cost/pricing data (particularly important for AI)
        cost_pages = self.find_pages_with_keyword("cost")
        for page in cost_pages[:3]:
            cost_metrics = self._extract_cost_metrics(page)
            metrics.extend(cost_metrics)
        
        # 5. Extract energy consumption data (NEW)
        logger.info("Extracting energy consumption data...")
        energy_pages = self.find_pages_with_keyword("energy")
        if not energy_pages:
            energy_pages = self.find_pages_with_keyword("power consumption")
        if not energy_pages:
            energy_pages = self.find_pages_with_keyword("carbon")
        
        for page in energy_pages[:5]:
            energy_metrics = self._extract_energy_metrics(page)
            metrics.extend(energy_metrics)
        
        # Remove duplicates
        unique_metrics = self._deduplicate_metrics(metrics)
        
        logger.info(f"Extracted {len(unique_metrics)} unique metrics from Stanford HAI report")
        return unique_metrics
    
    def _extract_executive_summary(self) -> List[Dict[str, Any]]:
        """Extract key metrics from executive summary."""
        metrics = []
        
        # Executive summary is usually in first 10 pages
        for page_num in range(min(10, self.doc.page_count)):
            text = self.extract_text_from_page(page_num)
            
            # Look for key patterns in executive summary
            patterns = {
                'adoption_rate': [
                    r'(\d+\.?\d*)%\s+of\s+(?:companies|firms|organizations)\s+(?:have\s+)?adopted',
                    r'adoption\s+rate\s+(?:reached|is|was)\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+(?:are\s+)?using\s+AI'
                ],
                'investment': [
                    r'(?:global\s+)?AI\s+investment\s+(?:reached|totaled|was)\s+\$?(\d+\.?\d*)\s*(billion|B)',
                    r'\$?(\d+\.?\d*)\s*(billion|B)\s+(?:in\s+)?AI\s+investment',
                    r'invested\s+\$?(\d+\.?\d*)\s*(billion|B)\s+in\s+AI'
                ],
                'productivity': [
                    r'productivity\s+(?:gains?|increases?)\s+of\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+productivity\s+(?:gain|increase|improvement)'
                ],
                'cost_reduction': [
                    r'cost\s+(?:reduction|savings?)\s+of\s+(\d+\.?\d*)%',
                    r'reduced\s+costs?\s+by\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+(?:lower\s+)?costs?'
                ]
            }
            
            for metric_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        value = float(match[0]) if isinstance(match, tuple) else float(match)
                        
                        # Extract year context
                        year = self._extract_year_context(text, pattern)
                        
                        metric = {
                            'metric_type': metric_type,
                            'value': value,
                            'unit': 'percentage' if '%' in pattern else 'billions_usd',
                            'source': self.source.value,
                            'page': page_num,
                            'year': year or 2025,  # Default to 2025 for latest report
                            'confidence': 0.9  # High confidence for executive summary
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_industry_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract industry-specific adoption metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Industry-specific patterns
        industries = ['technology', 'finance', 'healthcare', 'manufacturing', 'retail', 'education']
        
        for industry in industries:
            # Look for adoption rates by industry
            patterns = [
                rf'{industry}\s+(?:sector\s+)?(?:adoption\s+)?(?:rate\s+)?(?:is\s+)?(\d+\.?\d*)%',
                rf'(\d+\.?\d*)%\s+of\s+{industry}\s+(?:companies|firms)',
                rf'{industry}.*?adoption.*?(\d+\.?\d*)%'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if isinstance(match, str) else float(match[0])
                    
                    metric = {
                        'metric_type': 'adoption_rate',
                        'value': value,
                        'unit': 'percentage',
                        'sector': industry.capitalize(),
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_investment_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract investment-related metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Investment patterns
        patterns = {
            'global_investment': [
                r'global\s+AI\s+investment.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)',
                r'worldwide\s+AI\s+funding.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)'
            ],
            'venture_capital': [
                r'VC\s+investment.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)',
                r'venture\s+capital.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)'
            ],
            'corporate_investment': [
                r'corporate\s+(?:AI\s+)?investment.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)',
                r'enterprise\s+spending.*?\$?(\d+\.?\d*)\s*(billion|B|million|M)'
            ]
        }
        
        for investment_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match[0])
                    unit = 'billions_usd' if match[1].lower() in ['billion', 'b'] else 'millions_usd'
                    
                    # Convert millions to billions for consistency
                    if unit == 'millions_usd':
                        value = value / 1000
                        unit = 'billions_usd'
                    
                    metric = {
                        'metric_type': 'investment',
                        'value': value,
                        'unit': unit,
                        'category': investment_type,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.9
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_labor_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract labor market and employment metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Labor market patterns
        patterns = {
            'job_postings': [
                r'AI[- ]related\s+job\s+postings?.*?(\d+\.?\d*)%\s+increase',
                r'(\d+\.?\d*)%\s+(?:increase|growth)\s+in\s+AI\s+jobs?'
            ],
            'skill_demand': [
                r'demand\s+for\s+AI\s+skills?.*?(?:increased|grew)\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|growth)\s+in\s+AI\s+skill\s+demand'
            ],
            'wage_premium': [
                r'AI\s+(?:professionals?|workers?)\s+earn\s+(\d+\.?\d*)%\s+more',
                r'(\d+\.?\d*)%\s+wage\s+premium\s+for\s+AI'
            ],
            'automation_risk': [
                r'(\d+\.?\d*)%\s+of\s+jobs?\s+at\s+risk\s+of\s+automation',
                r'automation\s+(?:could\s+)?(?:affect|impact)\s+(\d+\.?\d*)%\s+of\s+jobs?'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if isinstance(match, str) else float(match[0])
                    
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
    
    def _extract_cost_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract AI cost-related metrics (training costs, inference costs, etc.)."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Cost patterns specific to AI
        patterns = {
            'training_cost': [
                r'training\s+cost.*?\$?(\d+\.?\d*)\s*(million|thousand|M|K)',
                r'cost\s+to\s+train.*?\$?(\d+\.?\d*)\s*(million|thousand|M|K)',
                r'GPT[- ]?\d*\s+training\s+cost.*?\$?(\d+\.?\d*)\s*(million|M)'
            ],
            'inference_cost': [
                r'inference\s+cost.*?\$?(\d+\.?\d*)\s*per\s+(thousand|million)\s+tokens?',
                r'cost\s+per\s+(\d+\.?\d*[KM]?)\s+tokens?.*?\$?(\d+\.?\d*)',
                r'\$?(\d+\.?\d*)\s*per\s+(\d+\.?\d*[KM]?)\s+tokens?'
            ],
            'cost_reduction': [
                r'(?:cost|price)\s+(?:decreased|fell|dropped)\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:decrease|reduction)\s+in\s+(?:AI\s+)?costs?',
                r'costs?\s+(?:have\s+)?fallen\s+(\d+\.?\d*)[-\s]?fold'
            ]
        }
        
        for cost_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    if cost_type == 'training_cost':
                        value = float(match[0])
                        unit = 'millions_usd' if match[1].lower() in ['million', 'm'] else 'thousands_usd'
                    elif cost_type == 'inference_cost':
                        # Handle different match formats
                        if len(match) == 2:
                            value = float(match[0])
                            unit = 'usd_per_thousand_tokens'
                    else:  # cost_reduction
                        value = float(match) if isinstance(match, str) else float(match[0])
                        unit = 'percentage' if '%' in text[text.find(str(value)):text.find(str(value))+10] else 'factor'
                    
                    metric = {
                        'metric_type': cost_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'page': page_num,
                        'year': self._extract_year_context(text, pattern) or 2025,
                        'confidence': 0.8
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_energy_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract energy consumption and sustainability metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Energy consumption patterns
        patterns = {
            'power_consumption': [
                r'(?:AI\s+)?(?:model\s+)?(?:training\s+)?power\s+consumption.*?(\d+\.?\d*)\s*(MW|megawatts?|GW|gigawatts?)',
                r'(\d+\.?\d*)\s*(MW|megawatts?|GW|gigawatts?)\s+(?:of\s+)?(?:power|electricity)',
                r'data\s+center.*?(\d+\.?\d*)\s*(MW|megawatts?|GW|gigawatts?)'
            ],
            'energy_usage': [
                r'energy\s+(?:usage|consumption).*?(\d+\.?\d*)\s*(kWh|MWh|GWh)',
                r'(\d+\.?\d*)\s*(kWh|MWh|GWh)\s+(?:of\s+)?(?:energy|electricity)',
                r'annual\s+energy.*?(\d+\.?\d*)\s*(kWh|MWh|GWh)'
            ],
            'carbon_emissions': [
                r'carbon\s+emissions?.*?(\d+\.?\d*)\s*(?:metric\s+)?(?:tons?|tonnes?)',
                r'(\d+\.?\d*)\s*(?:metric\s+)?(?:tons?|tonnes?)\s+(?:of\s+)?CO2',
                r'CO2\s+emissions?.*?(\d+\.?\d*)\s*(?:metric\s+)?(?:tons?|tonnes?)'
            ],
            'energy_efficiency': [
                r'energy\s+efficiency.*?(?:improved|increased)\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:more\s+)?energy\s+efficient',
                r'reduced\s+energy\s+consumption\s+by\s+(\d+\.?\d*)%'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value = float(match[0])
                        unit = match[1].lower() if len(match) > 1 else 'unknown'
                    else:
                        value = float(match)
                        unit = 'percentage' if metric_type == 'energy_efficiency' else 'unknown'
                    
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
        """Extract metrics from tables throughout the document."""
        metrics = []
        
        # Extract all tables
        all_tables = self.extract_all_tables()
        
        for page_num, tables in all_tables.items():
            for table_idx, table in enumerate(tables):
                # Try to identify what kind of table this is
                table_metrics = self._analyze_table(table, page_num)
                metrics.extend(table_metrics)
        
        return metrics
    
    def _analyze_table(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Analyze a table and extract metrics based on its structure."""
        metrics = []
        
        # Convert table to string for pattern matching
        table_text = table.to_string()
        
        # Check if it's an adoption rate table
        if any(word in table_text.lower() for word in ['adoption', 'usage', 'penetration']):
            metrics.extend(self._extract_adoption_table_metrics(table, page_num))
        
        # Check if it's an investment table
        elif any(word in table_text.lower() for word in ['investment', 'funding', 'capital']):
            metrics.extend(self._extract_investment_table_metrics(table, page_num))
        
        # Check if it's a cost table
        elif any(word in table_text.lower() for word in ['cost', 'price', 'expense']):
            metrics.extend(self._extract_cost_table_metrics(table, page_num))
        
        # Check if it's an energy table
        elif any(word in table_text.lower() for word in ['energy', 'power', 'mw', 'kwh', 'carbon']):
            metrics.extend(self._extract_energy_table_metrics(table, page_num))
        
        # Check if it's a time series table (has year columns)
        elif any(str(year) in table_text for year in range(2015, 2030)):
            metrics.extend(self._extract_timeseries_table_metrics(table, page_num))
        
        return metrics
    
    def _extract_adoption_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from adoption rate tables."""
        metrics = []
        
        # Look for percentage values in the table
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    # Check if it's a percentage
                    percent_match = re.search(r'(\d+\.?\d*)%', str(value))
                    if percent_match:
                        # Try to identify what this percentage represents
                        # Look at row index and column name for context
                        context = f"{idx} {col}" if idx else str(col)
                        
                        metric = {
                            'metric_type': 'adoption_rate',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.7  # Lower confidence for table data without clear labels
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_investment_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from investment tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    # Look for dollar amounts
                    dollar_match = re.search(r'\$?(\d+\.?\d*)\s*(B|billion|M|million)?', str(value))
                    if dollar_match:
                        amount = float(dollar_match.group(1))
                        unit_text = dollar_match.group(2) or ''
                        
                        if unit_text.lower() in ['b', 'billion']:
                            unit = 'billions_usd'
                        elif unit_text.lower() in ['m', 'million']:
                            amount = amount / 1000  # Convert to billions
                            unit = 'billions_usd'
                        else:
                            unit = 'millions_usd'  # Default assumption
                        
                        context = f"{idx} {col}" if idx else str(col)
                        
                        metric = {
                            'metric_type': 'investment',
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
    
    def _extract_cost_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from cost tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    # Look for cost patterns
                    cost_match = re.search(r'\$?(\d+\.?\d*)\s*(?:per\s+)?([KM]?\s*tokens?)?', str(value))
                    if cost_match:
                        amount = float(cost_match.group(1))
                        token_unit = cost_match.group(2) or ''
                        
                        if 'token' in token_unit.lower():
                            unit = 'usd_per_thousand_tokens' if 'K' in token_unit else 'usd_per_million_tokens'
                        else:
                            unit = 'usd'
                        
                        context = f"{idx} {col}" if idx else str(col)
                        
                        metric = {
                            'metric_type': 'cost',
                            'value': amount,
                            'unit': unit,
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.7
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_energy_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from energy consumption tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Look for energy units
                    energy_patterns = [
                        (r'(\d+\.?\d*)\s*(MW|megawatts?)', 'megawatts'),
                        (r'(\d+\.?\d*)\s*(GW|gigawatts?)', 'gigawatts'),
                        (r'(\d+\.?\d*)\s*(kWh)', 'kilowatt_hours'),
                        (r'(\d+\.?\d*)\s*(MWh)', 'megawatt_hours'),
                        (r'(\d+\.?\d*)\s*(GWh)', 'gigawatt_hours'),
                        (r'(\d+\.?\d*)\s*(?:metric\s+)?(?:tons?|tonnes?)\s*(?:CO2)?', 'co2_tons')
                    ]
                    
                    for pattern, unit_name in energy_patterns:
                        match = re.search(pattern, value_str, re.IGNORECASE)
                        if match:
                            amount = float(match.group(1))
                            context = f"{idx} {col}" if idx else str(col)
                            
                            metric = {
                                'metric_type': 'energy_consumption' if 'co2' not in unit_name else 'carbon_emissions',
                                'value': amount,
                                'unit': unit_name,
                                'context': context,
                                'source': self.source.value,
                                'page': page_num,
                                'year': self._extract_year_from_context(context) or 2025,
                                'confidence': 0.75
                            }
                            metrics.append(metric)
                            break
        
        return metrics
    
    def _extract_timeseries_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract time series data from tables with year columns."""
        metrics = []
        
        # Identify year columns
        year_cols = []
        for col in table.columns:
            if re.match(r'^20\d{2}$', str(col)):
                year_cols.append(col)
        
        if year_cols:
            # Each row might be a different metric
            for idx, row in table.iterrows():
                metric_name = str(idx)
                
                for year_col in year_cols:
                    value = row[year_col]
                    if pd.notna(value):
                        # Determine the type and unit of the metric
                        metric_type, unit, clean_value = self._parse_table_value(value)
                        
                        if clean_value is not None:
                            metric = {
                                'metric_type': metric_type,
                                'value': clean_value,
                                'unit': unit,
                                'metric_name': metric_name,
                                'source': self.source.value,
                                'page': page_num,
                                'year': int(year_col),
                                'confidence': 0.8
                            }
                            metrics.append(metric)
        
        return metrics
    
    def _parse_table_value(self, value: Any) -> tuple[str, str, Optional[float]]:
        """Parse a table value to determine metric type, unit, and numeric value."""
        value_str = str(value)
        
        # Check for percentage
        percent_match = re.search(r'(\d+\.?\d*)%', value_str)
        if percent_match:
            return 'rate', 'percentage', float(percent_match.group(1))
        
        # Check for dollar amount
        dollar_match = re.search(r'\$?(\d+\.?\d*)\s*(B|billion|M|million)?', value_str)
        if dollar_match:
            amount = float(dollar_match.group(1))
            unit_text = dollar_match.group(2) or ''
            
            if unit_text.lower() in ['b', 'billion']:
                return 'financial', 'billions_usd', amount
            elif unit_text.lower() in ['m', 'million']:
                return 'financial', 'millions_usd', amount
            else:
                return 'financial', 'usd', amount
        
        # Check for energy units
        energy_match = re.search(r'(\d+\.?\d*)\s*(MW|GW|kWh|MWh|GWh)', value_str, re.IGNORECASE)
        if energy_match:
            return 'energy', energy_match.group(2).lower(), float(energy_match.group(1))
        
        # Check for plain number
        number_match = re.search(r'^(\d+\.?\d*)$', value_str.strip())
        if number_match:
            return 'count', 'number', float(number_match.group(1))
        
        return 'unknown', 'unknown', None
    
    def _extract_year_context(self, text: str, pattern: str) -> Optional[int]:
        """Extract year from surrounding context of a pattern match."""
        # Look for years near the pattern
        year_pattern = r'(20\d{2})'
        years = re.findall(year_pattern, text)
        
        if years:
            # Return the most recent year found
            return max(int(year) for year in years)
        return None
    
    def _extract_year_from_context(self, context: str) -> Optional[int]:
        """Extract year from a context string."""
        year_match = re.search(r'(20\d{2})', context)
        if year_match:
            return int(year_match.group(1))
        return None
    
    def _deduplicate_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate metrics, keeping the highest confidence ones."""
        # Create a key for each metric
        metric_dict = {}
        
        for metric in metrics:
            # Create a unique key based on metric properties
            key = (
                metric.get('metric_type'),
                metric.get('value'),
                metric.get('unit'),
                metric.get('year'),
                metric.get('sector', 'global'),
                metric.get('category', 'general')
            )
            
            # Keep the metric with highest confidence
            if key not in metric_dict or metric.get('confidence', 0) > metric_dict[key].get('confidence', 0):
                metric_dict[key] = metric
        
        return list(metric_dict.values())