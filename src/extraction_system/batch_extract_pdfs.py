"""
Batch PDF Processing Script
Version: 1.0
Date: January 24, 2025

This script processes all PDFs using the enhanced extractor and
produces clean, deduplicated data ready for the dashboard.
"""

import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
from typing import List, Dict
import traceback

from enhanced_pdf_extractor import EnhancedPDFExtractor


class BatchPDFProcessor:
    """Handles batch processing of multiple PDFs"""
    
    def __init__(self, pdf_directory: str, output_directory: str = "extraction_output"):
        self.pdf_directory = Path(pdf_directory)
        self.output_directory = Path(output_directory)
        
        # Create output directory structure
        self.output_directory.mkdir(exist_ok=True)
        (self.output_directory / "individual_extractions").mkdir(exist_ok=True)
        (self.output_directory / "logs").mkdir(exist_ok=True)
        
        # Set up logging
        log_file = self.output_directory / "logs" / f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("BatchProcessor")
        
        # Storage for all metrics
        self.all_metrics = []
        self.processing_stats = {
            "total_pdfs": 0,
            "successful": 0,
            "failed": 0,
            "total_metrics": 0,
            "by_source": {}
        }
        
    def process_all_pdfs(self):
        """Process all PDFs in the directory"""
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        self.processing_stats["total_pdfs"] = len(pdf_files)
        
        self.logger.info(f"Found {len(pdf_files)} PDFs to process")
        
        for pdf_path in pdf_files:
            self.logger.info(f"\nProcessing: {pdf_path.name}")
            
            try:
                # Extract metrics
                extractor = EnhancedPDFExtractor(pdf_path)
                metrics = extractor.extract_all_metrics()
                
                # Add source information
                for metric in metrics:
                    metric["source_pdf"] = pdf_path.name
                    metric["extraction_date"] = datetime.now().isoformat()
                
                # Save individual extraction
                self._save_individual_extraction(pdf_path.name, metrics, extractor.get_summary_statistics())
                
                # Add to combined dataset
                self.all_metrics.extend(metrics)
                
                # Update stats
                self.processing_stats["successful"] += 1
                self.processing_stats["total_metrics"] += len(metrics)
                self.processing_stats["by_source"][pdf_path.name] = {
                    "metrics_count": len(metrics),
                    "status": "success"
                }
                
                self.logger.info(f"Successfully extracted {len(metrics)} metrics from {pdf_path.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
                self.logger.error(traceback.format_exc())
                
                self.processing_stats["failed"] += 1
                self.processing_stats["by_source"][pdf_path.name] = {
                    "metrics_count": 0,
                    "status": "failed",
                    "error": str(e)
                }
        
        # Save combined results
        self._save_combined_results()
        
        # Generate final report
        self._generate_final_report()
        
    def _save_individual_extraction(self, pdf_name: str, metrics: List[Dict], summary: Dict):
        """Save extraction results for individual PDF"""
        safe_name = pdf_name.replace(".pdf", "").replace(" ", "_")
        
        # Save metrics as CSV
        if metrics:
            df = pd.DataFrame(metrics)
            csv_path = self.output_directory / "individual_extractions" / f"{safe_name}_metrics.csv"
            df.to_csv(csv_path, index=False)
        
        # Save summary as JSON
        summary_path = self.output_directory / "individual_extractions" / f"{safe_name}_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def _save_combined_results(self):
        """Save all metrics in combined files"""
        if not self.all_metrics:
            self.logger.warning("No metrics extracted from any PDF")
            return
            
        # Convert to DataFrame
        df = pd.DataFrame(self.all_metrics)
        
        # Add unique ID for each metric
        df['metric_id'] = range(1, len(df) + 1)
        
        # Sort by confidence (highest first)
        df = df.sort_values('confidence', ascending=False)
        
        # Save as CSV
        csv_path = self.output_directory / "all_metrics_extracted.csv"
        df.to_csv(csv_path, index=False)
        self.logger.info(f"Saved {len(df)} metrics to {csv_path}")
        
        # Save high-confidence metrics separately
        high_conf_df = df[df['confidence'] >= 0.7]
        high_conf_path = self.output_directory / "high_confidence_metrics.csv"
        high_conf_df.to_csv(high_conf_path, index=False)
        self.logger.info(f"Saved {len(high_conf_df)} high-confidence metrics to {high_conf_path}")
        
        # Create sector-specific files
        sector_dir = self.output_directory / "by_sector"
        sector_dir.mkdir(exist_ok=True)
        
        for sector in df['sector'].unique():
            sector_df = df[df['sector'] == sector]
            if len(sector_df) > 0:
                sector_path = sector_dir / f"{sector}_metrics.csv"
                sector_df.to_csv(sector_path, index=False)
                
    def _generate_final_report(self):
        """Generate comprehensive extraction report"""
        report = {
            "extraction_summary": {
                "date": datetime.now().isoformat(),
                "total_pdfs_processed": self.processing_stats["total_pdfs"],
                "successful_extractions": self.processing_stats["successful"],
                "failed_extractions": self.processing_stats["failed"],
                "total_metrics_extracted": self.processing_stats["total_metrics"]
            },
            "quality_metrics": self._calculate_quality_metrics(),
            "sector_distribution": self._get_sector_distribution(),
            "metric_type_distribution": self._get_metric_type_distribution(),
            "source_details": self.processing_stats["by_source"],
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        report_path = self.output_directory / "extraction_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also create markdown report
        self._create_markdown_report(report)
        
    def _calculate_quality_metrics(self) -> Dict:
        """Calculate overall quality metrics"""
        if not self.all_metrics:
            return {"error": "No metrics to analyze"}
            
        df = pd.DataFrame(self.all_metrics)
        
        confidences = df['confidence'].values
        
        return {
            "average_confidence": float(confidences.mean()),
            "confidence_distribution": {
                "high_confidence": int((confidences >= 0.7).sum()),
                "medium_confidence": int(((confidences >= 0.5) & (confidences < 0.7)).sum()),
                "low_confidence": int((confidences < 0.5).sum())
            },
            "validation_issues": {
                "total_issues": sum(len(m.get('validation_issues', [])) for m in self.all_metrics),
                "metrics_with_issues": sum(1 for m in self.all_metrics if m.get('validation_issues', []))
            }
        }
    
    def _get_sector_distribution(self) -> Dict:
        """Get distribution of metrics by sector"""
        if not self.all_metrics:
            return {}
            
        df = pd.DataFrame(self.all_metrics)
        return df['sector'].value_counts().to_dict()
    
    def _get_metric_type_distribution(self) -> Dict:
        """Get distribution of metric types"""
        if not self.all_metrics:
            return {}
            
        df = pd.DataFrame(self.all_metrics)
        return df['metric_type'].value_counts().to_dict()
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on extraction results"""
        recommendations = []
        
        # Check success rate
        if self.processing_stats["failed"] > 0:
            recommendations.append(
                f"Review {self.processing_stats['failed']} failed PDFs for format issues"
            )
            
        # Check confidence levels
        if self.all_metrics:
            df = pd.DataFrame(self.all_metrics)
            low_conf_pct = (df['confidence'] < 0.5).mean() * 100
            
            if low_conf_pct > 20:
                recommendations.append(
                    f"{low_conf_pct:.1f}% of metrics have low confidence. Consider manual review."
                )
                
        # Check for missing sectors
        if self.all_metrics:
            df = pd.DataFrame(self.all_metrics)
            unknown_sector_count = (df['sector'] == 'unknown').sum()
            
            if unknown_sector_count > len(df) * 0.1:
                recommendations.append(
                    f"{unknown_sector_count} metrics have unknown sector. Improve sector classification."
                )
                
        return recommendations
    
    def _create_markdown_report(self, report: Dict):
        """Create a human-readable markdown report"""
        md_lines = [
            "# PDF Extraction Report",
            f"**Generated**: {report['extraction_summary']['date']}",
            "",
            "## Summary",
            f"- **Total PDFs**: {report['extraction_summary']['total_pdfs_processed']}",
            f"- **Successful**: {report['extraction_summary']['successful_extractions']}",
            f"- **Failed**: {report['extraction_summary']['failed_extractions']}",
            f"- **Total Metrics**: {report['extraction_summary']['total_metrics_extracted']}",
            "",
            "## Quality Metrics",
            f"- **Average Confidence**: {report['quality_metrics'].get('average_confidence', 0):.2f}",
            "",
            "### Confidence Distribution",
        ]
        
        if 'confidence_distribution' in report['quality_metrics']:
            conf_dist = report['quality_metrics']['confidence_distribution']
            md_lines.extend([
                f"- High (≥0.7): {conf_dist.get('high_confidence', 0)}",
                f"- Medium (0.5-0.7): {conf_dist.get('medium_confidence', 0)}",
                f"- Low (<0.5): {conf_dist.get('low_confidence', 0)}",
            ])
            
        md_lines.extend([
            "",
            "## Sector Distribution",
        ])
        
        for sector, count in report['sector_distribution'].items():
            md_lines.append(f"- {sector}: {count}")
            
        md_lines.extend([
            "",
            "## Recommendations",
        ])
        
        for rec in report['recommendations']:
            md_lines.append(f"- {rec}")
            
        # Save markdown
        md_path = self.output_directory / "extraction_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_lines))


def main():
    """Main execution function"""
    # Configuration
    PDF_DIRECTORY = "data/data/raw_pdfs"  # Updated to correct path
    OUTPUT_DIRECTORY = f"extraction_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Check if PDF directory exists
    if not Path(PDF_DIRECTORY).exists():
        print(f"Error: PDF directory '{PDF_DIRECTORY}' not found.")
        print("Please update the PDF_DIRECTORY variable with the correct path.")
        return
        
    # Create processor
    processor = BatchPDFProcessor(PDF_DIRECTORY, OUTPUT_DIRECTORY)
    
    # Process all PDFs
    processor.process_all_pdfs()
    
    print(f"\nExtraction complete! Results saved to: {OUTPUT_DIRECTORY}")
    print(f"Check {OUTPUT_DIRECTORY}/extraction_report.md for summary")


if __name__ == "__main__":
    main()