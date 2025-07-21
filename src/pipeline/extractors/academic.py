"""
Academic Paper Extractor

Handles academic papers with their unique structure:
- Abstract with key findings
- Literature review
- Methodology
- Empirical results
- Tables with regression results
- Conclusions

This extractor works for papers like:
- Acemoglu's Macroeconomics of AI
- Productivity impact studies
- Labor market analyses
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from src.pipeline.pdf_processor import PDFExtractor, EconomicMetricExtractor
from src.models.schema import AIAdoptionMetric, DataSource, MetricType, Unit

logger = logging.getLogger(__name__)


class AcademicPaperExtractor(PDFExtractor):
    """
    Specialized extractor for academic papers.
    
    Academic papers typically have:
    - Abstract with key quantitative findings
    - Structured sections (Introduction, Literature, Methods, Results)
    - Regression tables and statistical results
    - Robustness checks
    - Policy implications
    """
    
    def __init__(self, pdf_path: Path):
        super().__init__(pdf_path)
        self.source = DataSource.ACADEMIC_PAPER
        
    def extract_metrics(self) -> List[Dict[str, Any]]:
        """Extract metrics from academic paper structure."""
        metrics = []
        
        # 1. Extract from Abstract (usually page 1)
        logger.info("Extracting from Abstract...")
        abstract_metrics = self._extract_abstract_metrics()
        metrics.extend(abstract_metrics)
        
        # 2. Extract from Introduction/Executive Summary
        intro_pages = self.find_pages_with_keyword("Introduction")
        if not intro_pages:
            intro_pages = self.find_pages_with_keyword("Executive Summary")
        
        for page in intro_pages[:3]:
            intro_metrics = self._extract_introduction_metrics(page)
            metrics.extend(intro_metrics)
        
        # 3. Extract from Results/Findings sections
        results_pages = self.find_pages_with_keyword("Results")
        if not results_pages:
            results_pages = self.find_pages_with_keyword("Findings")
        if not results_pages:
            results_pages = self.find_pages_with_keyword("Empirical")
        
        for page in results_pages[:5]:
            results_metrics = self._extract_results_metrics(page)
            metrics.extend(results_metrics)
        
        # 4. Extract from regression tables and statistical results
        logger.info("Extracting from tables...")
        table_metrics = self._extract_regression_tables()
        metrics.extend(table_metrics)
        
        # 5. Extract from Conclusion/Policy Implications
        conclusion_pages = self.find_pages_with_keyword("Conclusion")
        policy_pages = self.find_pages_with_keyword("Policy")
        
        for page in (conclusion_pages + policy_pages)[:3]:
            conclusion_metrics = self._extract_conclusion_metrics(page)
            metrics.extend(conclusion_metrics)
        
        # 6. Extract any cost-benefit analysis
        cba_pages = self.find_pages_with_keyword("cost-benefit")
        if not cba_pages:
            cba_pages = self.find_pages_with_keyword("cost benefit")
        
        for page in cba_pages[:3]:
            cba_metrics = self._extract_cost_benefit_metrics(page)
            metrics.extend(cba_metrics)
        
        # Remove duplicates
        unique_metrics = self._deduplicate_metrics(metrics)
        
        logger.info(f"Extracted {len(unique_metrics)} unique metrics from academic paper")
        return unique_metrics
    
    def _extract_abstract_metrics(self) -> List[Dict[str, Any]]:
        """Extract key findings from abstract."""
        metrics = []
        
        # Abstract is usually on first page
        text = self.extract_text_from_page(0)
        
        # Look for abstract section
        abstract_start = text.lower().find("abstract")
        if abstract_start == -1:
            abstract_start = 0
        
        # Get text after "Abstract" up to Introduction or end of page
        abstract_end = text.lower().find("introduction", abstract_start)
        if abstract_end == -1:
            abstract_end = min(len(text), abstract_start + 3000)  # Limit to ~3000 chars
        
        abstract_text = text[abstract_start:abstract_end]
        
        # Academic paper patterns - focus on causal effects and estimates
        patterns = {
            'effect_size': [
                r'(?:increase|decrease|effect|impact)\s+of\s+(\d+\.?\d*)\s*(?:percent|percentage|%)',
                r'(\d+\.?\d*)\s*(?:percent|percentage|%)\s+(?:increase|decrease|effect)',
                r'(?:raises|lowers|reduces|improves)\s+(?:by\s+)?(\d+\.?\d*)\s*(?:percent|percentage|%)'
            ],
            'elasticity': [
                r'elasticity\s+of\s+(\d+\.?\d*)',
                r'(\d+\.?\d*)\s+percent\s+(?:increase|decrease)\s+(?:in|for)\s+(?:every|each)',
                r'1\s*(?:percent|%)\s+increase.*?(\d+\.?\d*)\s*(?:percent|%)'
            ],
            'productivity_impact': [
                r'productivity\s+(?:gains?|increase)\s+of\s+(\d+\.?\d*)\s*(?:percent|%)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+productivity\s+(?:gain|increase|improvement)'
            ],
            'cost_impact': [
                r'(?:cost|costs)\s+(?:reduction|savings?)\s+of\s+(\d+\.?\d*)\s*(?:percent|%)',
                r'(?:reduce|save)\s+(\d+\.?\d*)\s*(?:percent|%)\s+(?:in\s+)?costs?'
            ],
            'employment_impact': [
                r'(?:employment|jobs?)\s+(?:increase|decrease)\s+(?:of\s+)?(\d+\.?\d*)\s*(?:percent|%)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+(?:of\s+)?(?:jobs|workers)\s+(?:affected|displaced)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, abstract_text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if isinstance(match, str) else float(match[0])
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': 'percentage',
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'section': 'abstract',
                        'page': 0,
                        'year': self._extract_year_from_text(text) or 2024,
                        'confidence': 0.95  # High confidence for abstract findings
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_introduction_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from introduction section."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Introduction often contains motivation and key statistics
        patterns = {
            'market_size': [
                r'market\s+(?:size|value)\s+of\s+\$?(\d+\.?\d*)\s*(trillion|billion|million)',
                r'\$?(\d+\.?\d*)\s*(trillion|billion|million)\s+(?:AI\s+)?market'
            ],
            'growth_rate': [
                r'(?:growing|growth)\s+(?:at\s+)?(\d+\.?\d*)\s*(?:percent|%)\s+(?:per\s+)?(?:year|annually)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+(?:annual\s+)?growth'
            ],
            'adoption_stat': [
                r'(\d+\.?\d*)\s*(?:percent|%)\s+of\s+(?:firms|companies)\s+(?:have\s+)?adopted',
                r'adoption\s+rate\s+of\s+(\d+\.?\d*)\s*(?:percent|%)'
            ],
            'investment_stat': [
                r'investment\s+of\s+\$?(\d+\.?\d*)\s*(trillion|billion|million)',
                r'\$?(\d+\.?\d*)\s*(trillion|billion|million)\s+(?:in\s+)?investment'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple) and len(match) > 1:
                        value = float(match[0])
                        if match[1].lower() == 'trillion':
                            value = value * 1000  # Convert to billions
                        unit = 'billions_usd' if match[1] else 'percentage'
                    else:
                        value = float(match) if isinstance(match, str) else float(match[0])
                        unit = 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'section': 'introduction',
                        'page': page_num,
                        'year': self._extract_year_from_text(text) or 2024,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_results_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from results/findings section."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Results sections contain empirical findings
        patterns = {
            'coefficient': [
                r'coefficient\s+of\s+(\d+\.?\d*)',
                r'(?:beta|β)\s*=\s*(\d+\.?\d*)',
                r'estimate\s+of\s+(\d+\.?\d*)'
            ],
            'significance': [
                r'significant\s+at\s+(?:the\s+)?(\d+)\s*(?:percent|%)\s+level',
                r'p\s*[<>]\s*(\d+\.?\d*)'
            ],
            'r_squared': [
                r'R\^?2\s*=\s*(\d+\.?\d*)',
                r'R-squared\s*(?:of\s+)?(\d+\.?\d*)'
            ],
            'treatment_effect': [
                r'treatment\s+effect\s+of\s+(\d+\.?\d*)\s*(?:percent|%)?',
                r'(?:ATE|average\s+treatment\s+effect)\s*=\s*(\d+\.?\d*)'
            ],
            'marginal_effect': [
                r'marginal\s+effect\s+of\s+(\d+\.?\d*)',
                r'(\d+\.?\d*)\s+percentage\s+point\s+(?:increase|decrease)'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    value = float(match) if isinstance(match, str) else float(match[0])
                    
                    # Determine unit based on metric type
                    if metric_type in ['significance']:
                        unit = 'p_value'
                    elif metric_type in ['r_squared']:
                        unit = 'r_squared'
                    elif 'percent' in text[max(0, text.find(str(value))-20):text.find(str(value))+20]:
                        unit = 'percentage'
                    else:
                        unit = 'coefficient'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'section': 'results',
                        'page': page_num,
                        'year': self._extract_year_from_text(text) or 2024,
                        'confidence': 0.9
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_regression_tables(self) -> List[Dict[str, Any]]:
        """Extract metrics from regression tables."""
        metrics = []
        
        # Extract all tables
        all_tables = self.extract_all_tables()
        
        for page_num, tables in all_tables.items():
            for table_idx, table in enumerate(tables):
                # Check if it's a regression table
                if self._is_regression_table(table):
                    regression_metrics = self._extract_regression_metrics(table, page_num)
                    metrics.extend(regression_metrics)
                elif self._is_summary_statistics_table(table):
                    summary_metrics = self._extract_summary_statistics(table, page_num)
                    metrics.extend(summary_metrics)
        
        return metrics
    
    def _is_regression_table(self, table: pd.DataFrame) -> bool:
        """Check if table contains regression results."""
        table_text = table.to_string().lower()
        regression_keywords = ['coefficient', 'std. error', 'standard error', 't-stat', 
                               'p-value', 'r-squared', 'observations', '***', '**', '*']
        
        matches = sum(1 for keyword in regression_keywords if keyword in table_text)
        return matches >= 3
    
    def _is_summary_statistics_table(self, table: pd.DataFrame) -> bool:
        """Check if table contains summary statistics."""
        table_text = table.to_string().lower()
        stats_keywords = ['mean', 'std. dev', 'min', 'max', 'observations', 'n =']
        
        matches = sum(1 for keyword in stats_keywords if keyword in table_text)
        return matches >= 3
    
    def _extract_regression_metrics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from regression tables."""
        metrics = []
        
        # Look for key variables and their coefficients
        for idx, row in table.iterrows():
            row_str = str(idx) + ' ' + ' '.join(str(v) for v in row.values)
            
            # Extract coefficients with significance stars
            coef_pattern = r'([-]?\d+\.?\d*)\s*\*{0,3}'
            matches = re.findall(coef_pattern, row_str)
            
            if matches and any(keyword in row_str.lower() for keyword in 
                             ['ai', 'artificial intelligence', 'automation', 'technology',
                              'productivity', 'employment', 'wage', 'cost']):
                
                for match in matches:
                    try:
                        value = float(match)
                        # Skip if it looks like a year or observation count
                        if 1900 < value < 2100 or value > 10000:
                            continue
                        
                        # Determine what this coefficient represents
                        variable_name = str(idx).lower()
                        if 'ai' in variable_name or 'technology' in variable_name:
                            metric_type = 'ai_effect'
                        elif 'productivity' in variable_name:
                            metric_type = 'productivity_effect'
                        elif 'employment' in variable_name or 'job' in variable_name:
                            metric_type = 'employment_effect'
                        elif 'wage' in variable_name:
                            metric_type = 'wage_effect'
                        else:
                            metric_type = 'regression_coefficient'
                        
                        metric = {
                            'metric_type': metric_type,
                            'value': value,
                            'unit': 'coefficient',
                            'variable': str(idx),
                            'source': self.source.value,
                            'paper': self.pdf_name,
                            'section': 'regression_table',
                            'page': page_num,
                            'year': self._extract_year_from_text(str(table)) or 2024,
                            'confidence': 0.85
                        }
                        metrics.append(metric)
                        break  # Only take first coefficient per row
                    except ValueError:
                        continue
        
        return metrics
    
    def _extract_summary_statistics(self, table: pd.DataFrame, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from summary statistics tables."""
        metrics = []
        
        # Look for AI-related variables in summary stats
        for idx, row in table.iterrows():
            variable_name = str(idx).lower()
            
            if any(keyword in variable_name for keyword in 
                   ['ai', 'adoption', 'investment', 'productivity', 'cost', 'revenue']):
                
                # Try to extract mean value
                for col in table.columns:
                    col_lower = str(col).lower()
                    if 'mean' in col_lower or 'average' in col_lower:
                        value = row[col]
                        if pd.notna(value):
                            try:
                                numeric_value = float(str(value).replace(',', '').replace('$', ''))
                                
                                # Determine unit based on variable name
                                if '$' in str(value) or 'revenue' in variable_name or 'cost' in variable_name:
                                    unit = 'usd'
                                elif '%' in str(value) or 'rate' in variable_name:
                                    unit = 'percentage'
                                else:
                                    unit = 'index'
                                
                                metric = {
                                    'metric_type': 'summary_statistic',
                                    'value': numeric_value,
                                    'unit': unit,
                                    'variable': variable_name,
                                    'statistic': 'mean',
                                    'source': self.source.value,
                                    'paper': self.pdf_name,
                                    'page': page_num,
                                    'year': self._extract_year_from_text(str(table)) or 2024,
                                    'confidence': 0.8
                                }
                                metrics.append(metric)
                            except ValueError:
                                continue
        
        return metrics
    
    def _extract_conclusion_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract metrics from conclusion/policy section."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Conclusions often summarize key quantitative findings
        patterns = {
            'policy_impact': [
                r'policy\s+(?:could\s+)?(?:increase|improve|reduce)\s+(?:by\s+)?(\d+\.?\d*)\s*(?:percent|%)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+(?:improvement|reduction)\s+(?:from|through)\s+policy'
            ],
            'welfare_impact': [
                r'welfare\s+(?:gain|improvement)\s+of\s+(\d+\.?\d*)\s*(?:percent|%)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+welfare\s+(?:gain|improvement)'
            ],
            'long_term_effect': [
                r'long[- ]term\s+(?:effect|impact)\s+of\s+(\d+\.?\d*)\s*(?:percent|%)',
                r'(\d+\.?\d*)\s*(?:percent|%)\s+(?:in\s+the\s+)?long[- ]term'
            ],
            'recommendation': [
                r'recommend\s+(?:investing|spending)\s+\$?(\d+\.?\d*)\s*(billion|million)',
                r'optimal\s+(?:investment|spending)\s+of\s+\$?(\d+\.?\d*)\s*(billion|million)'
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
                        elif 'million' in match[1].lower():
                            unit = 'millions_usd'
                        else:
                            unit = 'percentage'
                    else:
                        value = float(match) if isinstance(match, str) else float(match[0])
                        unit = 'percentage'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'section': 'conclusion',
                        'page': page_num,
                        'year': self._extract_year_from_text(text) or 2024,
                        'confidence': 0.85
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_cost_benefit_metrics(self, page_num: int) -> List[Dict[str, Any]]:
        """Extract cost-benefit analysis metrics."""
        metrics = []
        text = self.extract_text_from_page(page_num)
        
        # Cost-benefit patterns
        patterns = {
            'benefit_cost_ratio': [
                r'benefit[- ]cost\s+ratio\s+of\s+(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*:\s*1\s+benefit[- ]cost',
                r'benefits?\s+(?:exceed|outweigh)\s+costs?\s+by\s+(\d+\.?\d*)\s*(?:times|x)'
            ],
            'net_benefit': [
                r'net\s+benefit\s+of\s+\$?(\d+\.?\d*)\s*(billion|million)',
                r'\$?(\d+\.?\d*)\s*(billion|million)\s+net\s+benefit'
            ],
            'total_cost': [
                r'total\s+cost\s+of\s+\$?(\d+\.?\d*)\s*(billion|million)',
                r'\$?(\d+\.?\d*)\s*(billion|million)\s+(?:in\s+)?(?:total\s+)?costs?'
            ],
            'total_benefit': [
                r'total\s+benefit\s+of\s+\$?(\d+\.?\d*)\s*(billion|million)',
                r'\$?(\d+\.?\d*)\s*(billion|million)\s+(?:in\s+)?(?:total\s+)?benefits?'
            ],
            'break_even_time': [
                r'break[- ]even\s+(?:in\s+)?(\d+\.?\d*)\s+years?',
                r'(\d+\.?\d*)\s+years?\s+to\s+break[- ]even'
            ]
        }
        
        for metric_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if metric_type == 'benefit_cost_ratio':
                        value = float(match) if isinstance(match, str) else float(match[0])
                        unit = 'ratio'
                    elif metric_type == 'break_even_time':
                        value = float(match) if isinstance(match, str) else float(match[0])
                        unit = 'years'
                    else:
                        value = float(match[0])
                        unit = 'billions_usd' if match[1].lower() == 'billion' else 'millions_usd'
                    
                    metric = {
                        'metric_type': metric_type,
                        'value': value,
                        'unit': unit,
                        'source': self.source.value,
                        'paper': self.pdf_name,
                        'section': 'cost_benefit_analysis',
                        'page': page_num,
                        'year': self._extract_year_from_text(text) or 2024,
                        'confidence': 0.9
                    }
                    metrics.append(metric)
        
        return metrics
    
    def _extract_year_from_text(self, text: str) -> Optional[int]:
        """Extract publication year from text."""
        # Look for patterns like "2024)" or "(2024)" or "Working Paper 2024"
        year_patterns = [
            r'\(?(20\d{2})\)?',
            r'Working\s+Paper\s+(20\d{2})',
            r'Draft.*?(20\d{2})',
            r'Version.*?(20\d{2})'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text[:1000])  # Check first 1000 chars
            if matches:
                # Return the most recent year
                years = [int(match) for match in matches]
                return max(years)
        
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
                metric.get('section'),
                metric.get('variable', ''),
                metric.get('paper')
            )
            
            # Keep highest confidence
            if key not in metric_dict or metric.get('confidence', 0) > metric_dict[key].get('confidence', 0):
                metric_dict[key] = metric
        
        return list(metric_dict.values())