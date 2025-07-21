"""
Test PDF Extraction - Single PDF

This script tests the extraction on a single PDF to ensure everything works
before processing all PDFs.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_single_pdf():
    """Test extraction on a single PDF."""
    # Get first PDF
    pdf_dir = project_root / "data" / "data" / "raw_pdfs"
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.error("No PDF files found!")
        return
    
    # Test with first PDF
    test_pdf = pdf_files[0]
    logger.info(f"Testing with: {test_pdf.name}")
    
    try:
        # Import after path setup
        from src.pipeline.extractors import UniversalExtractor
        
        # Test basic extraction
        with UniversalExtractor(test_pdf) as extractor:
            # Just test text extraction first
            logger.info("\n1. Testing text extraction...")
            text = extractor.extract_text_from_page(0)
            logger.info(f"   ✓ Extracted {len(text)} characters from page 1")
            
            # Test finding pages with keywords
            logger.info("\n2. Testing keyword search...")
            ai_pages = extractor.find_pages_with_keyword("AI")
            logger.info(f"   ✓ Found 'AI' on {len(ai_pages)} pages")
            
            # Test key statistics extraction
            logger.info("\n3. Testing statistics extraction...")
            stats = extractor.extract_key_statistics()
            total_stats = sum(len(v) for v in stats.values())
            logger.info(f"   ✓ Found {total_stats} statistics")
            
            for stat_type, stat_list in stats.items():
                if stat_list:
                    logger.info(f"   - {stat_type}: {len(stat_list)} items")
            
            # Test metric extraction
            logger.info("\n4. Testing full metric extraction...")
            metrics = extractor.extract_metrics()
            logger.info(f"   ✓ Extracted {len(metrics)} metrics")
            
            # Show sample metrics
            if metrics:
                logger.info("\n   Sample metrics:")
                for i, metric in enumerate(metrics[:5]):
                    logger.info(f"   {i+1}. {metric.get('metric_type', 'Unknown')}: "
                              f"{metric.get('value', 'N/A')} {metric.get('unit', '')}")
        
        logger.info("\n✅ Test successful! Ready to process all PDFs.")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {str(e)}")
        logger.error("\nThis might be because:")
        logger.error("1. Missing dependencies (try: pip install tabula-py)")
        logger.error("2. Java not installed (required for tabula-py)")
        logger.error("3. Import errors in the code")
        return False

if __name__ == "__main__":
    logger.info("=== PDF Extraction Test ===\n")
    success = test_single_pdf()
    
    if success:
        logger.info("\n" + "="*40)
        logger.info("Ready to run full extraction!")
        logger.info("Run: python extract_all_pdfs.py")
    else:
        logger.info("\n" + "="*40)
        logger.info("Please fix the errors before running full extraction.")