"""
Clean Extracted Data
Version: 1.0
Date: January 24, 2025

This script cleans the extracted metrics based on insights from:
1. Context window analysis
2. Compound term detection
3. Citation year patterns
4. Table/section reference patterns
5. Valid SME definitions

Preserves:
- ICT sector data
- Meaningful zeros from surveys
- Valid SME size definitions (e.g., "fewer than 500 employees")
- Legitimate small numbers with proper context
"""

import pandas as pd
import numpy as np
import re
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Tuple, Dict, List


class DataCleaner:
    """Clean extracted metrics with context-aware rules"""
    
    def __init__(self, input_csv: str, output_dir: str = None):
        self.input_csv = Path(input_csv)
        self.output_dir = Path(output_dir) if output_dir else self.input_csv.parent / "cleaned_data"
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up logging
        log_file = self.output_dir / f"cleaning_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load data
        self.logger.info(f"Loading data from {input_csv}")
        self.df = pd.read_csv(input_csv)
        self.original_count = len(self.df)
        
        # Tracking
        self.removal_reasons = {}
        self.preserved_reasons = {}
        
    def extract_context_window(self, full_context: str, value: float, window: int = 5) -> Tuple[str, str]:
        """Extract words before and after the value"""
        context = str(full_context)
        value_str = str(int(value)) if value == int(value) else str(value)
        
        # Find value in context
        pattern = r'\b' + re.escape(value_str) + r'\b'
        match = re.search(pattern, context)
        
        if not match:
            # Try without decimal
            if '.' in value_str:
                value_str = str(int(float(value_str)))
                pattern = r'\b' + re.escape(value_str) + r'\b'
                match = re.search(pattern, context)
        
        if not match:
            return "", ""
        
        start, end = match.span()
        
        # Extract surrounding words
        before_text = context[:start].strip()
        before_words = before_text.split()[-window:] if before_text else []
        
        after_text = context[end:].strip()
        after_words = after_text.split()[:window] if after_text else []
        
        return ' '.join(before_words), ' '.join(after_words)
    
    def is_compound_term_number(self, row: pd.Series) -> bool:
        """Check if number is part of a compound term"""
        value = row['value']
        context = str(row['context']).lower()
        
        # COVID-19
        if value == 19 and 'covid' in context:
            self.track_removal(row['metric_id'], "COVID-19 compound term")
            return True
        
        # Fortune 500
        if value == 500:
            before, after = self.extract_context_window(row['context'], value)
            context_phrase = f"{before} {value} {after}".lower()
            
            if 'fortune' in context_phrase or 's&p' in context_phrase:
                self.track_removal(row['metric_id'], "Fortune 500/S&P 500 reference")
                return True
        
        # 24/7
        if value in [24, 7]:
            if '24/7' in context or '24 7' in context or 'twenty-four seven' in context:
                self.track_removal(row['metric_id'], "24/7 compound term")
                return True
        
        # 401(k)
        if value == 401 and ('401k' in context or '401(k)' in context or '401 k' in context):
            self.track_removal(row['metric_id'], "401(k) reference")
            return True
        
        return False
    
    def is_citation_year(self, row: pd.Series) -> bool:
        """Enhanced citation year detection"""
        value = row['value']
        
        # Check if value is a year
        if not (2000 <= value <= 2030 and value == int(value)):
            return False
        
        context = str(row['context'])
        before, after = self.extract_context_window(context, value)
        context_phrase = f"{before} {value} {after}".lower()
        
        # Citation patterns
        citation_indicators = [
            'paper', 'study', 'article', 'publication', 'journal',
            'conference', 'proceedings', 'research', 'author',
            'et al', 'published', 'cited', 'reference', 'bibliography',
            '(', ')', 'pp.', 'vol.', 'doi:', 'isbn:', 'ssrn'
        ]
        
        # Count indicators
        indicator_count = sum(1 for ind in citation_indicators if ind in context_phrase)
        
        if indicator_count >= 2:  # Multiple indicators suggest citation
            self.track_removal(row['metric_id'], f"Citation year ({int(value)})")
            return True
        
        # Specific patterns
        if re.search(r'\(\s*' + str(int(value)) + r'\s*\)', context):  # (2023)
            self.track_removal(row['metric_id'], f"Citation year pattern ({int(value)})")
            return True
        
        return False
    
    def is_table_reference(self, row: pd.Series) -> bool:
        """Check if number is a table/figure/section reference"""
        value = row['value']
        context = str(row['context'])
        before, after = self.extract_context_window(context, value, window=3)
        
        # Reference indicators
        ref_patterns = [
            'table', 'figure', 'fig', 'section', 'chapter', 'appendix',
            'exhibit', 'chart', 'graph', 'page', 'pp', 'para', 'paragraph'
        ]
        
        before_lower = before.lower()
        
        for pattern in ref_patterns:
            if pattern in before_lower:
                self.track_removal(row['metric_id'], f"{pattern.capitalize()} reference ({value})")
                return True
        
        return False
    
    def is_valid_sme_definition(self, row: pd.Series) -> bool:
        """Check if this is a valid SME size definition"""
        value = row['value']
        
        # Common SME size thresholds
        if value not in [10, 50, 100, 250, 500, 1000, 5000]:
            return False
        
        context = str(row['context']).lower()
        before, after = self.extract_context_window(row['context'], value)
        context_phrase = f"{before} {value} {after}".lower()
        
        # SME patterns
        sme_patterns = [
            'fewer than', 'less than', 'under', 'below',
            'sme', 'small and medium', 'small business',
            'employee', 'worker', 'staff', 'personnel'
        ]
        
        matches = sum(1 for pattern in sme_patterns if pattern in context_phrase)
        
        if matches >= 2:  # Multiple indicators
            self.track_preservation(row['metric_id'], f"Valid SME definition ({value} employees)")
            return True
        
        return False
    
    def is_ict_data(self, row: pd.Series) -> bool:
        """Preserve ICT sector data"""
        context = str(row['context']).lower()
        sector = str(row.get('sector', '')).lower()
        
        # ICT patterns
        ict_patterns = [
            r'\bict\b',
            r'information.*communication.*technology',
            r'telecom',
            r'digital.*infrastructure',
            r'information.*technology',
            r'communication.*technology'
        ]
        
        # Check sector
        if 'information_communication_technology' in sector or 'ict' in sector:
            self.track_preservation(row['metric_id'], "ICT sector data")
            return True
        
        # Check context
        for pattern in ict_patterns:
            if re.search(pattern, context):
                self.track_preservation(row['metric_id'], "ICT context detected")
                return True
        
        return False
    
    def is_meaningful_zero(self, row: pd.Series) -> bool:
        """Check if zero value is meaningful"""
        if row['value'] != 0:
            return False
        
        context = str(row['context']).lower()
        
        # Survey/research patterns
        meaningful_patterns = [
            'survey', 'study', 'finding', 'result', 'observed',
            'measured', 'reported', 'found', 'showed', 'indicated',
            'no change', 'zero growth', 'unchanged', 'stable',
            'no increase', 'no decrease', 'remained flat'
        ]
        
        if any(pattern in context for pattern in meaningful_patterns):
            self.track_preservation(row['metric_id'], "Meaningful zero from survey/study")
            return True
        
        return False
    
    def is_legitimate_small_number(self, row: pd.Series) -> bool:
        """Check if small number has legitimate context"""
        value = row['value']
        
        if value >= 20 or value < 0:
            return False
        
        context = str(row['context']).lower()
        
        # Legitimate small number patterns
        legit_patterns = [
            'pilot', 'trial', 'test', 'initial', 'early',
            'few', 'several', 'handful', 'small group',
            'startup', 'beginning', 'first', 'selected'
        ]
        
        if any(pattern in context for pattern in legit_patterns):
            self.track_preservation(row['metric_id'], f"Legitimate small number ({value})")
            return True
        
        return False
    
    def should_remove(self, row: pd.Series) -> bool:
        """Main logic to determine if a metric should be removed"""
        
        # First check preservation rules (these override removal)
        if self.is_ict_data(row):
            return False
        
        if self.is_meaningful_zero(row):
            return False
        
        if self.is_valid_sme_definition(row):
            return False
        
        if self.is_legitimate_small_number(row):
            return False
        
        # Now check removal rules
        if self.is_compound_term_number(row):
            return True
        
        if self.is_citation_year(row):
            return True
        
        if self.is_table_reference(row):
            return True
        
        # Additional quality checks
        value = row['value']
        confidence = row.get('confidence', 1.0)
        
        # Very low confidence
        if confidence < 0.3:
            self.track_removal(row['metric_id'], f"Very low confidence ({confidence:.2f})")
            return True
        
        # Check for validation issues
        if pd.notna(row.get('validation_issues')):
            issues = eval(row['validation_issues']) if isinstance(row['validation_issues'], str) else row['validation_issues']
            if issues and len(issues) > 2:  # Multiple validation issues
                self.track_removal(row['metric_id'], f"Multiple validation issues ({len(issues)})")
                return True
        
        return False
    
    def track_removal(self, metric_id: int, reason: str):
        """Track removal reason"""
        self.removal_reasons[metric_id] = reason
    
    def track_preservation(self, metric_id: int, reason: str):
        """Track preservation reason"""
        self.preserved_reasons[metric_id] = reason
    
    def clean_data(self):
        """Main cleaning process"""
        self.logger.info("Starting data cleaning process...")
        
        # Create a copy for cleaning
        df_clean = self.df.copy()
        
        # Track metrics to remove
        to_remove = []
        
        # Process each row
        for idx, row in df_clean.iterrows():
            if self.should_remove(row):
                to_remove.append(idx)
        
        # Remove flagged metrics
        df_clean = df_clean.drop(to_remove)
        
        # Log results
        removed_count = len(to_remove)
        kept_count = len(df_clean)
        removal_rate = (removed_count / self.original_count) * 100
        
        self.logger.info(f"Original metrics: {self.original_count}")
        self.logger.info(f"Removed: {removed_count} ({removal_rate:.1f}%)")
        self.logger.info(f"Kept: {kept_count}")
        
        # Save cleaned data
        output_file = self.output_dir / "cleaned_metrics.csv"
        df_clean.to_csv(output_file, index=False)
        self.logger.info(f"Cleaned data saved to: {output_file}")
        
        # Save removal report
        self.save_cleaning_report(removed_count, kept_count)
        
        return df_clean
    
    def save_cleaning_report(self, removed_count: int, kept_count: int):
        """Save detailed cleaning report"""
        report = {
            "summary": {
                "original_count": self.original_count,
                "removed_count": removed_count,
                "kept_count": kept_count,
                "removal_rate": (removed_count / self.original_count) * 100,
                "timestamp": datetime.now().isoformat()
            },
            "removal_reasons": {},
            "preservation_reasons": {},
            "samples": {
                "removed": [],
                "preserved": []
            }
        }
        
        # Count removal reasons
        reason_counts = {}
        for reason in self.removal_reasons.values():
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        report["removal_reasons"] = dict(sorted(reason_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Count preservation reasons
        preserve_counts = {}
        for reason in self.preserved_reasons.values():
            preserve_counts[reason] = preserve_counts.get(reason, 0) + 1
        report["preservation_reasons"] = dict(sorted(preserve_counts.items(), key=lambda x: x[1], reverse=True))
        
        # Add samples
        for metric_id, reason in list(self.removal_reasons.items())[:10]:
            if metric_id in self.df['metric_id'].values:
                row = self.df[self.df['metric_id'] == metric_id].iloc[0]
                report["samples"]["removed"].append({
                    "metric_id": int(metric_id),
                    "value": float(row['value']),
                    "unit": row['unit'],
                    "metric_type": row['metric_type'],
                    "context": str(row['context'])[:200],
                    "reason": reason
                })
        
        # Save report
        report_file = self.output_dir / "cleaning_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        # Create markdown summary
        self.create_markdown_summary(report)
    
    def create_markdown_summary(self, report: dict):
        """Create human-readable summary"""
        md_lines = [
            "# Data Cleaning Report",
            f"**Date**: {report['summary']['timestamp'][:10]}",
            "",
            "## Summary",
            f"- **Original metrics**: {report['summary']['original_count']:,}",
            f"- **Removed**: {report['summary']['removed_count']:,} ({report['summary']['removal_rate']:.1f}%)",
            f"- **Kept**: {report['summary']['kept_count']:,}",
            "",
            "## Top Removal Reasons",
        ]
        
        for reason, count in list(report['removal_reasons'].items())[:10]:
            md_lines.append(f"- {reason}: {count:,}")
        
        if report['preservation_reasons']:
            md_lines.extend([
                "",
                "## Preservation Reasons",
            ])
            for reason, count in report['preservation_reasons'].items():
                md_lines.append(f"- {reason}: {count:,}")
        
        md_lines.extend([
            "",
            "## Quality Checks Applied",
            "- [x] Compound term detection (COVID-19, Fortune 500, etc.)",
            "- [x] Citation year filtering",
            "- [x] Table/figure reference removal",
            "- [x] ICT sector preservation",
            "- [x] Meaningful zero preservation",
            "- [x] Valid SME definitions preserved",
            "- [x] Context-aware small number validation",
            "",
            "## Recommendations",
            "1. Review high-confidence metrics first",
            "2. Check sector distribution for balance",
            "3. Validate against domain knowledge",
        ])
        
        summary_file = self.output_dir / "cleaning_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))


def main():
    """Main execution"""
    # Find latest extraction
    extraction_dirs = list(Path('.').glob('extraction_output_*'))
    if not extraction_dirs:
        print("No extraction output found!")
        return
    
    latest_dir = sorted(extraction_dirs)[-1]
    input_csv = latest_dir / 'all_metrics_extracted.csv'
    
    if not input_csv.exists():
        print(f"CSV not found: {input_csv}")
        return
    
    print(f"Cleaning data from: {input_csv}")
    
    # Run cleaning
    cleaner = DataCleaner(str(input_csv))
    cleaned_df = cleaner.clean_data()
    
    print(f"\nCleaning complete!")
    print(f"Check {cleaner.output_dir} for results")


if __name__ == "__main__":
    main()