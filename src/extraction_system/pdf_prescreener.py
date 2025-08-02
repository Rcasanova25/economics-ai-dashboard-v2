"""
PDF Pre-screening Mechanism
Quickly assess if a PDF contains valuable economic metrics
"""

import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime


@dataclass
class PreScreenResult:
    """Results from pre-screening analysis"""
    pdf_path: str
    total_score: float
    
    # Component scores (0-100)
    metric_density_score: float
    table_quality_score: float
    economic_relevance_score: float
    data_recency_score: float
    
    # Raw counts
    percentage_count: int
    financial_count: int
    table_count: int
    economic_keyword_count: int
    
    # Insights
    sample_metrics: List[str]
    recommendation: str
    estimated_quality: str
    
    # Metadata
    pages_analyzed: int
    total_pages: int
    analysis_time: float


class PDFPreScreener:
    """Pre-screen PDFs to determine extraction worthiness"""
    
    def __init__(self, sample_pages: int = 10):
        self.sample_pages = sample_pages
        self.logger = logging.getLogger(__name__)
        
        # High-value patterns that indicate economic metrics
        self.metric_patterns = {
            'percentage': [
                # More flexible patterns
                r'(\d+(?:\.\d+)?)\s*%',  # Any percentage
                r'(\d+(?:\.\d+)?)\s*percent',  # Written out
                r'(\d+)\s*%\s*of\s+(?:companies|organizations|enterprises|firms|respondents)',
                r'adoption\s+rate[:\s]+(\d+(?:\.\d+)?)\s*%',
                r'ROI\s+of\s+(\d+(?:\.\d+)?)\s*%',
            ],
            'financial': [
                r'\$\s*(\d+(?:\.\d+)?)\s*(?:billion|million|B|M)',  # Any financial value
                r'(\d+(?:\.\d+)?)\s*(?:billion|million)\s+(?:USD|dollars|in\s+revenue)',
                r'market\s+(?:size|value)[:\s]+\$?\s*(\d+(?:\.\d+)?)',
            ],
            'productivity': [
                r'productivity\s+(?:gain|improvement|increase)[:\s]+(\d+(?:\.\d+)?)\s*%',
                r'efficiency\s+(?:gain|improvement)[:\s]+(\d+(?:\.\d+)?)\s*%',
                r'(\d+(?:\.\d+)?)\s*%\s+(?:time|cost)\s+savings',
                r'(\d+(?:\.\d+)?)\s*%\s+(?:increase|improvement|growth)',
            ]
        }
        
        # Economic keywords that indicate relevant content
        self.economic_keywords = [
            # Core economic terms
            'adoption rate', 'market share', 'revenue growth', 'cost reduction',
            'return on investment', 'roi', 'productivity', 'efficiency',
            
            # AI-specific economic terms  
            'ai investment', 'ai adoption', 'ai market', 'ai spending',
            'machine learning adoption', 'generative ai', 'genai', 'gen ai',
            
            # Business metrics
            'enterprise value', 'market size', 'growth rate', 'cagr',
            'total addressable market', 'tam', 'operational efficiency',
            
            # Sectoral terms
            'by industry', 'by sector', 'across industries', 'industry breakdown',
            'manufacturing', 'financial services', 'healthcare', 'retail'
        ]
        
        # Patterns that indicate low-quality content
        self.negative_patterns = [
            r'figure\s+\d+',  # Figure captions
            r'table\s+\d+',   # Table captions without data
            r'copyright\s+©',  # Copyright notices
            r'page\s+\d+\s+of\s+\d+',  # Page numbers
            r'\[\d+\]',  # Citation brackets
        ]
    
    def prescreen(self, pdf_path: Path) -> PreScreenResult:
        """Pre-screen a PDF for economic metric quality"""
        
        start_time = datetime.now()
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            pages_to_analyze = min(self.sample_pages, total_pages)
            
            # Analyze first N pages and some from middle
            pages_to_check = list(range(pages_to_analyze))
            if total_pages > self.sample_pages * 2:
                # Also sample from middle of document
                mid_start = total_pages // 2
                pages_to_check.extend(range(mid_start, mid_start + 3))
            
            # Collect metrics from sampled pages
            all_text = ""
            table_count = 0
            sample_metrics = []
            
            for page_num in pages_to_check:
                if page_num < total_pages:
                    page = doc[page_num]
                    text = page.get_text()
                    all_text += text + "\n"
                    
                    # Count tables (basic heuristic)
                    if self._has_table_structure(text):
                        table_count += 1
            
            doc.close()
            
            # Calculate component scores
            metric_density = self._calculate_metric_density(all_text, sample_metrics)
            table_quality = self._calculate_table_quality(table_count, len(pages_to_check))
            economic_relevance = self._calculate_economic_relevance(all_text)
            data_recency = self._calculate_data_recency(all_text)
            
            # Count specific patterns
            percentage_count = sum(len(re.findall(pattern, all_text, re.IGNORECASE)) 
                                 for pattern in self.metric_patterns['percentage'])
            financial_count = sum(len(re.findall(pattern, all_text, re.IGNORECASE)) 
                                for pattern in self.metric_patterns['financial'])
            keyword_count = sum(1 for keyword in self.economic_keywords 
                              if keyword.lower() in all_text.lower())
            
            # Calculate total score (weighted average)
            total_score = (
                metric_density * 0.35 +
                table_quality * 0.20 +
                economic_relevance * 0.30 +
                data_recency * 0.15
            )
            
            # Determine recommendation
            if total_score >= 70:
                recommendation = "HIGH PRIORITY - Extract immediately"
                estimated_quality = "High"
            elif total_score >= 40:
                recommendation = "MEDIUM PRIORITY - Extract if time permits"
                estimated_quality = "Medium"
            else:
                recommendation = "LOW PRIORITY - Skip unless specifically needed"
                estimated_quality = "Low"
            
            # Get sample metrics for preview
            sample_metrics = self._extract_sample_metrics(all_text)[:5]
            
            analysis_time = (datetime.now() - start_time).total_seconds()
            
            return PreScreenResult(
                pdf_path=str(pdf_path),
                total_score=round(total_score, 1),
                metric_density_score=round(metric_density, 1),
                table_quality_score=round(table_quality, 1),
                economic_relevance_score=round(economic_relevance, 1),
                data_recency_score=round(data_recency, 1),
                percentage_count=percentage_count,
                financial_count=financial_count,
                table_count=table_count,
                economic_keyword_count=keyword_count,
                sample_metrics=sample_metrics,
                recommendation=recommendation,
                estimated_quality=estimated_quality,
                pages_analyzed=len(pages_to_check),
                total_pages=total_pages,
                analysis_time=round(analysis_time, 2)
            )
            
        except Exception as e:
            self.logger.error(f"Pre-screening failed for {pdf_path}: {e}")
            return PreScreenResult(
                pdf_path=str(pdf_path),
                total_score=0,
                metric_density_score=0,
                table_quality_score=0,
                economic_relevance_score=0,
                data_recency_score=0,
                percentage_count=0,
                financial_count=0,
                table_count=0,
                economic_keyword_count=0,
                sample_metrics=[],
                recommendation="ERROR - Could not analyze",
                estimated_quality="Unknown",
                pages_analyzed=0,
                total_pages=0,
                analysis_time=0
            )
    
    def _calculate_metric_density(self, text: str, sample_metrics: List[str]) -> float:
        """Calculate density of economic metrics in text"""
        
        # Count all metric patterns
        total_metrics = 0
        
        for pattern_list in self.metric_patterns.values():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                total_metrics += len(matches)
                
                # Collect samples
                for match in matches[:2]:  # First 2 of each type
                    context_match = re.search(r'.{0,50}' + re.escape(str(match)) + r'.{0,50}', text)
                    if context_match:
                        sample_metrics.append(context_match.group(0).strip())
        
        # Calculate density per 1000 characters
        text_length = len(text)
        if text_length == 0:
            return 0
        
        density = (total_metrics / text_length) * 10000
        
        # Convert to 0-100 score (high density = 100)
        # Assume 5+ metrics per 10k chars is excellent
        score = min(100, (density / 5) * 100)
        
        return score
    
    def _calculate_table_quality(self, table_count: int, pages_analyzed: int) -> float:
        """Estimate table quality based on presence and structure"""
        
        if pages_analyzed == 0:
            return 0
        
        # Tables per page ratio
        table_ratio = table_count / pages_analyzed
        
        # Good PDFs have 0.3-1.0 tables per page
        if table_ratio >= 0.3:
            score = min(100, table_ratio * 100)
        else:
            score = table_ratio * 200  # Boost low ratios
        
        return score
    
    def _calculate_economic_relevance(self, text: str) -> float:
        """Calculate relevance based on economic keywords"""
        
        text_lower = text.lower()
        keyword_matches = 0
        unique_keywords = set()
        
        for keyword in self.economic_keywords:
            if keyword.lower() in text_lower:
                keyword_matches += text_lower.count(keyword.lower())
                unique_keywords.add(keyword)
        
        # Score based on unique keywords (diversity) and total matches (depth)
        diversity_score = min(100, len(unique_keywords) * 5)  # 20 unique = 100
        depth_score = min(100, keyword_matches * 2)  # 50 matches = 100
        
        return (diversity_score + depth_score) / 2
    
    def _calculate_data_recency(self, text: str) -> float:
        """Check if data is recent (2023-2025)"""
        
        current_year = datetime.now().year
        recent_years = [str(year) for year in range(current_year - 2, current_year + 1)]
        
        recent_count = 0
        for year in recent_years:
            # Look for year in data context, not just citations
            pattern = rf'{year}\s*(?:survey|data|report|study|adoption|growth)'
            recent_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Old data check
        old_years = [str(year) for year in range(2010, current_year - 3)]
        old_count = sum(text.count(year) for year in old_years)
        
        if recent_count > old_count:
            score = min(100, recent_count * 10)
        else:
            score = max(0, 50 - old_count * 5)
        
        return score
    
    def _has_table_structure(self, text: str) -> bool:
        """Simple heuristic to detect table-like structures"""
        
        # Look for patterns that suggest tabular data
        lines = text.split('\n')
        
        # Count lines with multiple numbers separated by spaces/tabs
        numeric_lines = 0
        for line in lines:
            numbers = re.findall(r'\d+(?:\.\d+)?', line)
            if len(numbers) >= 2:
                numeric_lines += 1
        
        # Multiple numeric lines suggest a table
        return numeric_lines >= 3
    
    def _extract_sample_metrics(self, text: str) -> List[str]:
        """Extract sample metrics for preview"""
        
        samples = []
        
        # Get one example of each type
        for metric_type, patterns in self.metric_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Get context around match
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    context = ' '.join(context.split())  # Clean whitespace
                    samples.append(f"[{metric_type}] {context}")
                    break
        
        return samples
    
    def batch_prescreen(self, pdf_dir: Path) -> Dict[str, PreScreenResult]:
        """Pre-screen all PDFs in a directory"""
        
        results = {}
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        print(f"Pre-screening {len(pdf_files)} PDFs...")
        print("-" * 60)
        
        for pdf_path in pdf_files:
            print(f"\nAnalyzing: {pdf_path.name}")
            result = self.prescreen(pdf_path)
            results[pdf_path.name] = result
            
            # Print summary
            print(f"Score: {result.total_score}/100 - {result.estimated_quality}")
            print(f"Metrics found: {result.percentage_count} percentages, {result.financial_count} financial")
            print(f"Recommendation: {result.recommendation}")
        
        return results


def create_prescreening_report(results: Dict[str, PreScreenResult]) -> str:
    """Create a summary report of pre-screening results"""
    
    report = []
    report.append("PDF PRE-SCREENING REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total PDFs analyzed: {len(results)}")
    report.append("")
    
    # Sort by score
    sorted_results = sorted(results.items(), key=lambda x: x[1].total_score, reverse=True)
    
    # High priority PDFs
    high_priority = [r for r in sorted_results if r[1].total_score >= 70]
    if high_priority:
        report.append("HIGH PRIORITY PDFs:")
        report.append("-" * 40)
        for name, result in high_priority:
            report.append(f"\n{name}")
            report.append(f"  Score: {result.total_score}/100")
            report.append(f"  Economic keywords: {result.economic_keyword_count}")
            report.append(f"  Sample metric: {result.sample_metrics[0] if result.sample_metrics else 'None'}")
    
    # Medium priority
    medium_priority = [r for r in sorted_results if 40 <= r[1].total_score < 70]
    if medium_priority:
        report.append("\n\nMEDIUM PRIORITY PDFs:")
        report.append("-" * 40)
        for name, result in medium_priority:
            report.append(f"\n{name}")
            report.append(f"  Score: {result.total_score}/100")
            report.append(f"  Metrics found: {result.percentage_count + result.financial_count}")
    
    # Low priority
    low_priority = [r for r in sorted_results if r[1].total_score < 40]
    if low_priority:
        report.append("\n\nLOW PRIORITY PDFs (Skip):")
        report.append("-" * 40)
        for name, result in low_priority:
            report.append(f"\n{name}: Score {result.total_score}/100")
    
    # Summary statistics
    report.append("\n\nSUMMARY:")
    report.append("-" * 40)
    report.append(f"High priority: {len(high_priority)} PDFs")
    report.append(f"Medium priority: {len(medium_priority)} PDFs")
    report.append(f"Low priority: {len(low_priority)} PDFs")
    
    avg_score = sum(r.total_score for _, r in results.items()) / len(results) if results else 0
    report.append(f"\nAverage quality score: {avg_score:.1f}/100")
    
    total_time = sum(r.analysis_time for _, r in results.items())
    report.append(f"Total analysis time: {total_time:.1f} seconds")
    
    return "\n".join(report)


# Example usage
if __name__ == "__main__":
    prescreener = PDFPreScreener(sample_pages=10)
    
    # Test on a single PDF
    pdf_path = Path("../data/data/raw_pdfs/the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf")
    
    if pdf_path.exists():
        print("Testing pre-screener on McKinsey PDF...")
        result = prescreener.prescreen(pdf_path)
        
        print(f"\nResults for {pdf_path.name}:")
        print(f"Overall Score: {result.total_score}/100")
        print(f"Quality: {result.estimated_quality}")
        print(f"Recommendation: {result.recommendation}")
        print(f"\nComponent Scores:")
        print(f"  Metric Density: {result.metric_density_score}/100")
        print(f"  Table Quality: {result.table_quality_score}/100")
        print(f"  Economic Relevance: {result.economic_relevance_score}/100")
        print(f"  Data Recency: {result.data_recency_score}/100")
        print(f"\nMetrics Found:")
        print(f"  Percentages: {result.percentage_count}")
        print(f"  Financial: {result.financial_count}")
        print(f"  Tables: {result.table_count}")
        print(f"\nSample Metrics:")
        for sample in result.sample_metrics:
            print(f"  - {sample}")
    
    # Batch pre-screen all PDFs
    print("\n" + "="*60)
    print("BATCH PRE-SCREENING ALL PDFs")
    print("="*60)
    
    pdf_dir = Path("../data/data/raw_pdfs")
    if pdf_dir.exists():
        results = prescreener.batch_prescreen(pdf_dir)
        
        # Generate report
        report = create_prescreening_report(results)
        print("\n" + report)
        
        # Save report
        with open("prescreening_report.txt", "w") as f:
            f.write(report)