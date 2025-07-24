"""
Test Script for New Extraction System
Version: 1.0
Date: January 24, 2025

This script tests the extraction system with a single PDF first
to ensure everything is working before batch processing.
"""

import sys
from pathlib import Path
import json
import logging

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_pdf_extractor import EnhancedPDFExtractor
from extraction_sector_metric_schema_final import SectorType, MetricCategory


def test_schema():
    """Test that schema is loaded correctly"""
    print("Testing Schema Loading...")
    print("-" * 50)
    
    # Test sector types
    print(f"Number of sectors defined: {len(SectorType)}")
    print(f"Sectors: {[s.value for s in SectorType][:5]}...")
    
    # Test metric categories
    print(f"\nNumber of metric categories: {len(MetricCategory)}")
    print(f"Categories: {[c.value for c in MetricCategory]}")
    
    print("\n[OK] Schema loaded successfully!")
    

def test_single_pdf(pdf_path: str):
    """Test extraction on a single PDF"""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found at {pdf_path}")
        return False
        
    print(f"\nTesting extraction on: {pdf_path.name}")
    print("-" * 50)
    
    try:
        # Create extractor
        extractor = EnhancedPDFExtractor(pdf_path, debug=True)
        
        # Extract metrics
        metrics = extractor.extract_all_metrics()
        
        # Get summary
        summary = extractor.get_summary_statistics()
        
        print(f"\n[OK] Extraction successful!")
        print(f"Metrics found: {len(metrics)}")
        print(f"Duplicates skipped: {summary['extraction_stats']['duplicates_skipped']}")
        print(f"Citations skipped: {summary['extraction_stats']['citations_skipped']}")
        print(f"Average confidence: {summary['confidence']['mean']:.2f}")
        
        # Show sample metrics
        if metrics:
            print("\nSample metrics extracted:")
            for i, metric in enumerate(metrics[:3]):
                print(f"\nMetric {i+1}:")
                print(f"  Value: {metric['value']} {metric['unit']}")
                print(f"  Type: {metric['metric_type']}")
                print(f"  Sector: {metric['sector']}")
                print(f"  Confidence: {metric['confidence']:.2f}")
                print(f"  Context: {metric['context'][:80]}...")
                
        return True
        
    except Exception as e:
        print(f"[ERROR] During extraction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing():
    """Test batch processing setup"""
    print("\n\nTesting Batch Processing Setup...")
    print("-" * 50)
    
    from batch_extract_pdfs import BatchPDFProcessor
    
    # Test with a small directory
    test_dir = Path("data/data/raw_pdfs")
    
    if not test_dir.exists():
        print(f"Creating test directory: {test_dir}")
        test_dir.mkdir(parents=True, exist_ok=True)
        
    # Count PDFs
    pdf_count = len(list(test_dir.glob("*.pdf")))
    print(f"PDFs found in {test_dir}: {pdf_count}")
    
    if pdf_count == 0:
        print("[WARNING] No PDFs found. Add PDFs to data/data/raw_pdfs/ directory")
    else:
        print("[OK] Ready for batch processing!")
        
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("EXTRACTION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Schema
    test_schema()
    
    # Test 2: Single PDF
    # First, find a PDF to test
    pdf_dir = Path("data/data/raw_pdfs")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        if pdfs:
            print(f"\nFound {len(pdfs)} PDFs. Testing with first one...")
            test_single_pdf(str(pdfs[0]))
        else:
            print("\n[WARNING] No PDFs found for testing")
            print("Add PDFs to data/data/raw_pdfs/ directory")
    else:
        print(f"\n[WARNING] PDF directory not found: {pdf_dir}")
        print("Create the directory and add PDFs")
        
    # Test 3: Batch setup
    test_batch_processing()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ensure PDFs are in data/data/raw_pdfs/ directory")
    print("2. Run: python batch_extract_pdfs.py")
    print("3. Check extraction_output_[timestamp]/ for results")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    main()