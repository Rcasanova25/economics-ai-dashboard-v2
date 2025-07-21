"""
OECD AI Policy Observatory Report Extractor

The OECD reports focus on:
- Policy frameworks and governance
- International comparisons
- Economic impacts by country
- Labor market effects
- Investment trends by region
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.pipeline.pdf_processor import PDFExtractor, EconomicMetricExtractor
from src.models.schema import AIAdoptionMetric, DataSource, MetricType, Unit

logger = logging.getLogger(__name__)


class OECDExtractor(PDFExtractor):
    """
    Specialized extractor for OECD AI reports.
    
    OECD reports typically have:
    - Country-by-country analysis
    - Policy recommendations
    - Comparative statistics
    - Extensive footnotes and methodology sections
    """
    
    def __init__(self, pdf_path: Path):
        super().__init__(pdf_path)
        self.source = DataSource.OECD
        
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics specific to OECD report structure."""
        metrics = []
        
        # 1. Extract from Executive Summary
        logger.info("Extracting from Executive Summary...")
        exec_summary_metrics = self._extract_executive_summary()
        metrics.extend(exec_summary_metrics)
        
        # 2. Extract country-specific data
        logger.info("Extracting country-specific metrics...")
        country_metrics = self._extract_country_metrics()
        metrics.extend(country_metrics)
        
        # 3. Extract policy impact metrics
        logger.info("Extracting policy impact metrics...")
        policy_pages = self.find_pages_with_keyword("policy")
        for page in policy_pages[:5]:
            policy_metrics = self._extract_policy_metrics(page)
            metrics.extend(policy_metrics)
        
        # 4. Extract labor market analysis
        labor_pages = self.find_pages_with_keyword("employment")
        if not labor_pages:
            labor_pages = self.find_pages_with_keyword("labour market")  # OECD uses British spelling
        
        for page in labor_pages[:5]:
            labor_metrics = self._extract_labor_metrics(page)
            metrics.extend(labor_metrics)
        
        # 5. Extract investment and R&D metrics
        investment_pages = self.find_pages_with_keyword("investment")
        rd_pages = self.find_pages_with_keyword("R&D")
        
        for page in (investment_pages + rd_pages)[:5]:
            investment_metrics = self._extract_investment_rd_metrics(page)
            metrics.extend(investment_metrics)
        
        # 6. Extract from data tables
        logger.info("Extracting from tables...")
        table_metrics = self._extract_table_metrics()
        metrics.extend(table_metrics)
        
        # 7. Extract energy and sustainability metrics (if present)
        sustainability_pages = self.find_pages_with_keyword("sustainab")
        energy_pages = self.find_pages_with_keyword("energy")
        
        for page in (sustainability_pages + energy_pages)[:3]:
            sustainability_metrics = self._extract_sustainability_metrics(page)
            metrics.extend(sustainability_metrics)
        
        # Remove duplicates
        unique_metrics = self._deduplicate_metrics(metrics)
        
        logger.info(f"Extracted {len(unique_metrics)} unique metrics from OECD report")
        return unique_metrics
    
    def _extract_executive_summary(self) -> List[Dict[str, Any]]:
        """Extract key metrics from executive summary."""
        metrics = []
        
        # OECD executive summaries are usually in first 5-8 pages
        for page_num in range(min(8, self.doc.page_count)):
            text = self.extract_text_from_page(page_num)
            
            # OECD-specific patterns
            patterns = {
                'ai_investment': [
                    r'AI\s+investment\s+(?:reached|totaled|was)\s+(?:USD\s+)?\$?(\d+\.?\d*)\s*(billion|million)',
                    r'(?:USD\s+)?\$?(\d+\.?\d*)\s*(billion|million)\s+in\s+AI\s+investment'
                ],
                'gdp_impact': [
                    r'AI\s+(?:could\s+)?(?:contribute|add)\s+(\d+\.?\d*)%\s+to\s+GDP',
                    r'GDP\s+(?:growth|increase)\s+of\s+(\d+\.?\d*)%\s+(?:from|due to)\s+AI'
                ],
                'productivity_impact': [
                    r'productivity\s+(?:gains?|increases?)\s+of\s+(\d+\.?\d*)%',
                    r'(\d+\.?\d*)%\s+productivity\s+(?:improvement|increase)'
                ],
                'adoption_rate': [
                    r'(\d+\.?\d*)%\s+of\s+(?:firms|companies|enterprises)\s+(?:have\s+)?adopted\s+AI',
                    r'AI\s+adoption\s+rate\s+(?:of\s+)?(\d+\.?\d*)%'
                ],
                'employment_impact': [
                    r'(\d+\.?\d*)%\s+of\s+(?:jobs|workers)\s+(?:could be\s+)?affected',
                    r'affect\s+(\d+\.?\d*)%\s+of\s+(?:the\s+)?(?:workforce|employment)'
                ]
            }
            
            for metric_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            value = float(match[0])
                            unit = 'billions_usd' if 'billion' in match[1].lower() else 'millions_usd'
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
    
    def _extract_country_metrics(self) -> List[Dict[str, Any]]:
        """Extract country-specific metrics."""
        metrics = []
        
        # Major OECD countries to look for
        countries = [
            'United States', 'USA', 'US',
            'China', 'Japan', 'Germany',
            'United Kingdom', 'UK', 'France',
            'Canada', 'South Korea', 'Korea',
            'Australia', 'Italy', 'Spain',
            'Netherlands', 'Sweden', 'Switzerland'
        ]
        
        for country in countries:
            country_pages = self.find_pages_with_keyword(country)
            
            for page_num in country_pages[:3]:  # Check first 3 pages mentioning the country
                text = self.extract_text_from_page(page_num)
                
                # Country-specific patterns
                patterns = [
                    rf'{country}.*?AI\s+investment.*?\$?(\d+\.?\d*)\s*(billion|million)',
                    rf'{country}.*?(\d+\.?\d*)%\s+(?:of\s+)?(?:firms|companies)\s+(?:using|adopted)\s+AI',
                    rf'{country}.*?R&D\s+(?:spending|expenditure).*?\$?(\d+\.?\d*)\s*(billion|million)',
                    rf'{country}.*?(\d+\.?\d*)%\s+GDP\s+(?:growth|impact)',
                    rf'{country}.*?(\d+\.?\d*)\s*(?:thousand|million)?\s+AI\s+(?:researchers|professionals)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        # Determine metric type based on pattern content
                        if 'investment' in pattern or 'R&D' in pattern:
                            metric_type = 'investment'
                            if isinstance(match, tuple):
                                value = float(match[0])
                                unit = 'billions_usd' if 'billion' in match[1].lower() else 'millions_usd'
                            else:
                                value = float(match)
                                unit = 'millions_usd'
                        elif 'firms' in pattern or 'companies' in pattern:
                            metric_type = 'adoption_rate'
                            value = float(match) if not isinstance(match, tuple) else float(match[0])
                            unit = 'percentage'
                        elif 'GDP' in pattern:
                            metric_type = 'gdp_impact'
                            value = float(match) if not isinstance(match, tuple) else float(match[0])
                            unit = 'percentage'
                        else:
                            metric_type = 'workforce'
                            value = float(match[0]) if isinstance(match, tuple) else float(match)
                            unit = 'count'
                        
                        metric = {
                            'metric_type': metric_type,
                            'value': value,
                            'unit': unit,
                            'region': country,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_context(text, pattern) or 2025,
                            'confidence': 0.85
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_policy_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract policy-related metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Policy impact patterns
        patterns = {
            'regulatory_impact': [
                r'regulation.*?(?:increased|decreased)\s+(?:AI\s+)?adoption\s+by\s+(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:increase|decrease)\s+(?:in\s+)?adoption\s+(?:due to|following)\s+(?:new\s+)?regulation'
            ],
            'policy_effectiveness': [
                r'policy\s+(?:intervention|measure).*?(\d+\.?\d*)%\s+(?:more\s+)?effective',
                r'(\d+\.?\d*)%\s+(?:improvement|increase)\s+(?:in\s+)?(?:AI\s+)?(?:adoption|implementation)'
            ],
            'compliance_cost': [
                r'compliance\s+cost.*?\$?(\d+\.?\d*)\s*(billion|million)',
                r'regulatory\s+burden.*?\$?(\d+\.?\d*)\s*(billion|million)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if 'cost' in metric_type:
                        value = float(match[0])
                        unit = 'billions_usd' if 'billion' in match[1].lower() else 'millions_usd'
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
                        'confidence': 0.8
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_labor_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract labor market metrics with OECD's specific focus."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # OECD labor market patterns
        patterns = {
            'job_displacement': [
                r'(\d+\.?\d*)%\s+of\s+jobs\s+(?:at\s+)?(?:high\s+)?risk\s+of\s+automation',
                r'(?:could\s+)?displace\s+(\d+\.?\d*)%\s+of\s+(?:current\s+)?jobs'
            ],
            'job_creation': [
                r'create\s+(\d+\.?\d*)\s*million\s+(?:new\s+)?jobs',
                r'(\d+\.?\d*)\s*million\s+(?:new\s+)?jobs\s+(?:could be\s+)?created'
            ],
            'skill_gap': [
                r'(\d+\.?\d*)%\s+(?:of\s+)?(?:workers|employees)\s+(?:lack|need)\s+(?:AI\s+)?skills',
                r'skill\s+gap\s+(?:affecting|of)\s+(\d+\.?\d*)%'
            ],
            'wage_inequality': [
                r'wage\s+(?:gap|inequality)\s+(?:increased|widened)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+wage\s+(?:differential|premium)\s+(?:for\s+)?AI\s+skills'
            ],
            'training_investment': [
                r'(?:re)?training\s+(?:investment|cost).*?\$?(\d+\.?\d*)\s*(billion|million)',
                r'\$?(\d+\.?\d*)\s*(billion|million)\s+(?:for\s+)?(?:worker\s+)?(?:re)?training'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if 'million' in pattern and 'jobs' in pattern:
                        value = float(match) if not isinstance(match, tuple) else float(match[0])
                        unit = 'millions_jobs'
                    elif 'investment' in metric_type or 'cost' in pattern:
                        value = float(match[0])
                        unit = 'billions_usd' if 'billion' in match[1].lower() else 'millions_usd'
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
    
    def _extract_investment_rd_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract investment and R&D metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Investment patterns
        patterns = {
            'private_investment': [
                r'private\s+(?:sector\s+)?investment.*?\$?(\d+\.?\d*)\s*(billion|million)',
                r'corporate\s+AI\s+(?:R&D|investment).*?\$?(\d+\.?\d*)\s*(billion|million)'
            ],
            'public_investment': [
                r'(?:public|government)\s+(?:AI\s+)?investment.*?\$?(\d+\.?\d*)\s*(billion|million)',
                r'(?:public|government)\s+(?:AI\s+)?(?:R&D|funding).*?\$?(\d+\.?\d*)\s*(billion|million)'
            ],
            'rd_intensity': [
                r'R&D\s+intensity.*?(\d+\.?\d*)%\s+of\s+GDP',
                r'(\d+\.?\d*)%\s+of\s+GDP\s+(?:spent\s+)?on\s+AI\s+R&D'
            ],
            'venture_capital': [
                r'(?:VC|venture\s+capital).*?\$?(\d+\.?\d*)\s*(billion|million)',
                r'startup\s+funding.*?\$?(\d+\.?\d*)\s*(billion|million)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and len(match) > 1:
                        value = float(match[0])
                        if 'billion' in match[1].lower():
                            unit = 'billions_usd'
                        else:
                            unit = 'millions_usd'
                    else:
                        value = float(match) if not isinstance(match, tuple) else float(match[0])
                        unit = 'percentage' if 'intensity' in metric_type else 'millions_usd'
                    
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
    
    def _extract_sustainability_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract sustainability and energy-related metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Sustainability patterns
        patterns = {
            'energy_consumption': [
                r'AI\s+(?:systems?\s+)?energy\s+consumption.*?(\d+\.?\d*)\s*(TWh|GWh|MWh)',
                r'data\s+centers?\s+(?:energy\s+)?consumption.*?(\d+\.?\d*)\s*(TWh|GWh|MWh)'
            ],
            'carbon_footprint': [
                r'carbon\s+(?:footprint|emissions).*?(\d+\.?\d*)\s*(?:million\s+)?(?:metric\s+)?tons',
                r'(\d+\.?\d*)\s*(?:Mt|million\s+tons)\s+CO2(?:\s+equivalent)?'
            ],
            'renewable_energy': [
                r'(\d+\.?\d*)%\s+(?:of\s+)?AI\s+(?:systems?\s+)?(?:powered\s+by\s+)?renewable',
                r'renewable\s+energy\s+(?:usage|share).*?(\d+\.?\d*)%'
            ],
            'efficiency_improvement': [
                r'energy\s+efficiency\s+(?:improved|increased)\s+(?:by\s+)?(\d+\.?\d*)%',
                r'(\d+\.?\d*)%\s+(?:reduction|decrease)\s+in\s+energy\s+(?:consumption|use)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        value = float(match[0])
                        if len(match) > 1 and match[1]:
                            unit = match[1].lower()
                        else:
                            unit = 'percentage' if '%' in pattern else 'unknown'
                    else:
                        value = float(match)
                        unit = 'percentage' if '%' in pattern else 'unknown'
                    
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
    
    def _extract_table_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics from OECD's data tables."""
        metrics = []
        
        # Extract all tables
        all_tables = self.extract_all_tables()
        
        for page_num, tables in all_tables.items():
            for table_idx, table in enumerate(tables):
                # OECD tables often have country comparisons
                if self._is_country_comparison_table(table):
                    country_metrics = self._extract_country_comparison_metrics(table, page_num)
                    metrics.extend(country_metrics)
                else:
                    # Use general table analysis
                    table_metrics = self._analyze_table(table, page_num)
                    metrics.extend(table_metrics)
        
        return metrics
    
    def _is_country_comparison_table(self, table: pd.DataFrame) -> bool:
        """Check if table contains country comparisons."""
        table_text = table.to_string().lower()
        countries = ['united states', 'china', 'japan', 'germany', 'france', 'korea']
        
        country_count = sum(1 for country in countries if country.lower() in table_text)
        return country_count >= 3  # At least 3 countries mentioned
    
    def _extract_country_comparison_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from country comparison tables."""
        metrics = []
        
        # Try to identify country column
        country_col = None
        for col in table.columns:
            col_text = str(col).lower()
            if 'country' in col_text or 'nation' in col_text:
                country_col = col
                break
        
        if country_col is None:
            # Check if first column contains country names
            first_col = table.columns[0]
            sample_values = table[first_col].astype(str).str.lower()
            if any('united states' in val or 'china' in val for val in sample_values):
                country_col = first_col
        
        if country_col:
            # Extract metrics for each country
            for idx, row in table.iterrows():
                country = str(row[country_col])
                
                for col in table.columns:
                    if col != country_col:
                        value = row[col]
                        if pd.notna(value):
                            # Parse the value
                            metric_type, unit, clean_value = self._parse_table_value(value)
                            
                            if clean_value is not None:
                                metric = {
                                    'metric_type': metric_type,
                                    'value': clean_value,
                                    'unit': unit,
                                    'region': country,
                                    'metric_name': str(col),
                                    'source': self.source.value,
                                    'page': page_num,
                                    'year': self._extract_year_from_context(str(col)) or 2025,
                                    'confidence': 0.8
                                }
                                metrics.append(metric)
        
        return metrics
    
    def _analyze_table(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """General table analysis for OECD tables."""
        metrics = []
        
        # Similar to Stanford HAI but with OECD-specific considerations
        table_text = table.to_string()
        
        # Check table type based on content
        if any(word in table_text.lower() for word in ['adoption', 'implementation', 'usage']):
            metrics.extend(self._extract_adoption_table_metrics(table, page_num))
        elif any(word in table_text.lower() for word in ['investment', 'funding', 'expenditure']):
            metrics.extend(self._extract_investment_table_metrics(table, page_num))
        elif any(word in table_text.lower() for word in ['employment', 'jobs', 'workforce']):
            metrics.extend(self._extract_employment_table_metrics(table, page_num))
        elif any(word in table_text.lower() for word in ['energy', 'carbon', 'emissions']):
            metrics.extend(self._extract_energy_table_metrics(table, page_num))
        
        return metrics
    
    def _extract_adoption_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract adoption metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    # Check if it's a percentage
                    percent_match = re.search(r'(\d+\.?\d*)%', str(value))
                    if percent_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'adoption_rate',
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
    
    def _extract_investment_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract investment metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    # Look for monetary values
                    money_match = re.search(r'(?:USD\s+)?\$?(\d+\.?\d*)\s*(billion|million|B|M)?', str(value))
                    if money_match:
                        amount = float(money_match.group(1))
                        unit_text = money_match.group(2) or ''
                        
                        if unit_text.lower() in ['billion', 'b']:
                            unit = 'billions_usd'
                        elif unit_text.lower() in ['million', 'm']:
                            amount = amount / 1000
                            unit = 'billions_usd'
                        else:
                            unit = 'millions_usd'
                        
                        context = f"{idx} {col}"
                        
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
    
    def _extract_employment_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract employment metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Look for job numbers
                    job_match = re.search(r'(\d+\.?\d*)\s*(thousand|million)?\s*(?:jobs|workers|employees)', value_str, re.IGNORECASE)
                    if job_match:
                        amount = float(job_match.group(1))
                        scale = job_match.group(2) or ''
                        
                        if scale.lower() == 'million':
                            unit = 'millions_jobs'
                        elif scale.lower() == 'thousand':
                            amount = amount / 1000
                            unit = 'millions_jobs'
                        else:
                            unit = 'jobs'
                        
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'employment',
                            'value': amount,
                            'unit': unit,
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.75
                        }
                        metrics.append(metric)
                    
                    # Look for percentages (unemployment, etc.)
                    percent_match = re.search(r'(\d+\.?\d*)%', value_str)
                    if percent_match and not job_match:
                        context = f"{idx} {col}"
                        
                        metric = {
                            'metric_type': 'employment_rate',
                            'value': float(percent_match.group(1)),
                            'unit': 'percentage',
                            'context': context,
                            'source': self.source.value,
                            'page': page_num,
                            'year': self._extract_year_from_context(context) or 2025,
                            'confidence': 0.7
                        }
                        metrics.append(metric)
        
        return metrics
    
    def _extract_energy_table_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract energy and sustainability metrics from tables."""
        metrics = []
        
        for idx, row in table.iterrows():
            for col in table.columns:
                value = row[col]
                if pd.notna(value):
                    value_str = str(value)
                    
                    # Energy consumption patterns
                    energy_patterns = [
                        (r'(\d+\.?\d*)\s*(TWh|terawatt)', 'terawatt_hours'),
                        (r'(\d+\.?\d*)\s*(GWh|gigawatt)', 'gigawatt_hours'),
                        (r'(\d+\.?\d*)\s*(MWh|megawatt)', 'megawatt_hours'),
                        (r'(\d+\.?\d*)\s*(Mt|megatons?)\s*CO2', 'megatons_co2'),
                        (r'(\d+\.?\d*)\s*(?:million\s+)?tons?\s*CO2', 'million_tons_co2')
                    ]
                    
                    for pattern, unit_name in energy_patterns:
                        match = re.search(pattern, value_str, re.IGNORECASE)
                        if match:
                            amount = float(match.group(1))
                            context = f"{idx} {col}"
                            
                            metric = {
                                'metric_type': 'energy_consumption' if 'wh' in unit_name else 'carbon_emissions',
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
    
    def _parse_table_value(self, value: Any) -> tuple[str, str, Optional[float]]:
        """Parse a table value to determine metric type, unit, and numeric value."""
        value_str = str(value)
        
        # Check for percentage
        percent_match = re.search(r'(\d+\.?\d*)%', value_str)
        if percent_match:
            return 'rate', 'percentage', float(percent_match.group(1))
        
        # Check for monetary amount
        money_match = re.search(r'(?:USD\s+)?\$?(\d+\.?\d*)\s*(billion|million|B|M)?', value_str, re.IGNORECASE)
        if money_match:
            amount = float(money_match.group(1))
            unit_text = money_match.group(2) or ''
            
            if unit_text.lower() in ['billion', 'b']:
                return 'financial', 'billions_usd', amount
            elif unit_text.lower() in ['million', 'm']:
                return 'financial', 'millions_usd', amount
            else:
                return 'financial', 'usd', amount
        
        # Check for job numbers
        job_match = re.search(r'(\d+\.?\d*)\s*(thousand|million)?\s*(?:jobs|workers)', value_str, re.IGNORECASE)
        if job_match:
            amount = float(job_match.group(1))
            scale = job_match.group(2) or ''
            
            if scale.lower() == 'million':
                return 'employment', 'millions_jobs', amount
            elif scale.lower() == 'thousand':
                return 'employment', 'thousands_jobs', amount
            else:
                return 'employment', 'jobs', amount
        
        # Check for plain number
        number_match = re.search(r'^(\d+\.?\d*)$', value_str.strip())
        if number_match:
            return 'count', 'number', float(number_match.group(1))
        
        return 'unknown', 'unknown', None
    
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
                metric.get('region', 'global'),
                metric.get('context', '')[:50]  # First 50 chars of context
            )
            
            # Keep highest confidence
            if key not in metric_dict or metric.get('confidence', 0) > metric_dict[key].get('confidence', 0):
                metric_dict[key] = metric
        
        return list(metric_dict.values())