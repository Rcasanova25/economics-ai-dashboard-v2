"""
Main PDF Extraction Script

This script orchestrates the extraction of economic metrics from all PDFs.
It automatically selects the right extractor for each PDF and ensures
comprehensive data capture, including contradictory information.

As a senior developer, I recommend running this script:
1. Initially to populate your database
2. When new PDFs are added
3. Periodically to update with new extraction patterns

Usage:
    python extract_all_pdfs.py
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline.pdf_processor import PDFProcessingPipeline
from src.pipeline.extractors import (
    EXTRACTOR_MAPPING, 
    DEFAULT_EXTRACTOR,
    StanfordHAIExtractor,
    OECDExtractor,
    McKinseyExtractor,
    AcademicPaperExtractor,
    UniversalExtractor
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def select_extractor_for_pdf(pdf_path: Path) -> type:
    """
    Select the appropriate extractor based on PDF filename.
    
    This function implements our hybrid strategy:
    1. Check for specific extractor matches
    2. Fall back to universal extractor
    """
    pdf_name_lower = pdf_path.name.lower()
    
    # Check each pattern in our mapping
    for pattern, extractor_class in EXTRACTOR_MAPPING.items():
        if pattern.lower() in pdf_name_lower:
            logger.info(f"Selected {extractor_class.__name__} for {pdf_path.name}")
            return extractor_class
    
    # Default to universal extractor
    logger.info(f"Using UniversalExtractor (default) for {pdf_path.name}")
    return DEFAULT_EXTRACTOR


def create_extraction_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a summary of extraction results for analysis."""
    summary = {
        'total_pdfs': len(results),
        'successful': 0,
        'failed': 0,
        'total_metrics': 0,
        'metrics_by_type': {},
        'metrics_by_source': {},
        'potential_contradictions': []
    }
    
    # Analyze results
    for result in results:
        if 'error' in result:
            summary['failed'] += 1
        else:
            summary['successful'] += 1
            metrics = result.get('metrics', [])
            summary['total_metrics'] += len(metrics)
            
            # Count metrics by type
            for metric in metrics:
                metric_type = metric.get('metric_type', 'unknown')
                summary['metrics_by_type'][metric_type] = summary['metrics_by_type'].get(metric_type, 0) + 1
            
            # Count by source PDF
            pdf_name = result.get('pdf_name', 'unknown')
            summary['metrics_by_source'][pdf_name] = len(metrics)
    
    # Look for potential contradictions (simplified version)
    # In practice, you'd do more sophisticated analysis
    all_metrics = []
    for result in results:
        if 'metrics' in result:
            all_metrics.extend(result['metrics'])
    
    # Group similar metrics and find outliers
    adoption_rates = [m for m in all_metrics if 'adoption' in m.get('metric_type', '').lower()]
    if len(adoption_rates) > 1:
        values = [m['value'] for m in adoption_rates if m.get('unit') == 'percentage']
        if values:
            min_val, max_val = min(values), max(values)
            if max_val - min_val > 20:  # More than 20% difference
                summary['potential_contradictions'].append({
                    'type': 'adoption_rate_variance',
                    'min': min_val,
                    'max': max_val,
                    'sources': list(set(m.get('source', 'unknown') for m in adoption_rates))
                })
    
    return summary


def main():
    """Main extraction function."""
    logger.info("=== Starting PDF Extraction Process ===")
    
    # Setup paths
    pdf_dir = project_root / "data" / "data" / "raw_pdfs"
    output_dir = project_root / "data" / "processed" / "extractions"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if PDF directory exists
    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return
    
    # Create extraction pipeline
    pipeline = PDFProcessingPipeline(output_dir)
    
    # Get all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Create dynamic extractor mapping
    dynamic_mapping = {}
    for pdf_path in pdf_files:
        extractor_class = select_extractor_for_pdf(pdf_path)
        # Use the PDF stem (filename without extension) as key
        dynamic_mapping[pdf_path.stem] = extractor_class
    
    # Process all PDFs
    results = []
    for pdf_path in pdf_files:
        logger.info(f"\nProcessing: {pdf_path.name}")
        logger.info("-" * 50)
        
        try:
            # Get the appropriate extractor
            extractor_class = dynamic_mapping.get(pdf_path.stem, DEFAULT_EXTRACTOR)
            
            # Process the PDF
            result = pipeline.process_pdf(pdf_path, extractor_class)
            results.append(result)
            
            # Log metrics summary
            if 'metrics' in result:
                logger.info(f"✓ Extracted {len(result['metrics'])} metrics")
                
                # Show sample metrics
                for i, metric in enumerate(result['metrics'][:3]):
                    logger.info(f"  Sample {i+1}: {metric.get('metric_type')} = "
                              f"{metric.get('value')} {metric.get('unit')}")
                if len(result['metrics']) > 3:
                    logger.info(f"  ... and {len(result['metrics']) - 3} more metrics")
            
        except Exception as e:
            logger.error(f"✗ Failed to process {pdf_path.name}: {str(e)}")
            results.append({
                'pdf_name': pdf_path.name,
                'error': str(e),
                'extraction_date': datetime.now().isoformat()
            })
    
    # Create and save summary
    logger.info("\n=== Extraction Summary ===")
    summary = create_extraction_summary(results)
    
    logger.info(f"Total PDFs processed: {summary['total_pdfs']}")
    logger.info(f"Successful: {summary['successful']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Total metrics extracted: {summary['total_metrics']}")
    
    # Show metrics by type
    logger.info("\nMetrics by type:")
    for metric_type, count in sorted(summary['metrics_by_type'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"  {metric_type}: {count}")
    
    # Show potential contradictions
    if summary['potential_contradictions']:
        logger.info("\n⚠️  Potential contradictions found:")
        for contradiction in summary['potential_contradictions']:
            logger.info(f"  - {contradiction['type']}: "
                       f"values range from {contradiction['min']} to {contradiction['max']}")
            logger.info(f"    Sources: {', '.join(contradiction['sources'])}")
    
    # Save summary
    summary_file = output_dir / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"\n✅ Extraction complete! Summary saved to: {summary_file}")
    
    # Save consolidated metrics for database import
    all_metrics = []
    for result in results:
        if 'metrics' in result:
            for metric in result['metrics']:
                metric['pdf_source'] = result.get('pdf_name', 'unknown')
                all_metrics.append(metric)
    
    metrics_file = output_dir / f"all_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(all_metrics, f, indent=2)
    
    logger.info(f"📊 All metrics saved to: {metrics_file}")
    logger.info(f"   Ready for database import!")
    
    return results, all_metrics


if __name__ == "__main__":
    results, metrics = main()
    
    # Print final message
    print("\n" + "="*60)
    print("🎉 PDF EXTRACTION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review extraction logs for any issues")
    print("2. Check extracted metrics for quality")
    print("3. Import metrics into SQLite database")
    print("4. Run the dashboard to visualize results")
    print("\nTo view extracted data:")
    print(f"  - Check: {Path('data/processed/extractions')}")
    print("  - Look for JSON files with metrics and summaries")