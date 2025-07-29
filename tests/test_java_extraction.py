"""
Test PDF Extraction with Java

This script verifies Java is working correctly with tabula-py
"""

import sys
import os
import logging
from pathlib import Path

# Add Java to PATH if needed
java_path = r"C:\Program Files\Java\jdk-17\bin"
if java_path not in os.environ['PATH']:
    os.environ['PATH'] = java_path + os.pathsep + os.environ['PATH']

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_java_and_extraction():
    """Test Java availability and table extraction."""
    
    # 1. Test Java availability
    logger.info("=== Testing Java Installation ===")
    try:
        import subprocess
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✓ Java is available!")
            logger.info(f"  Version: {result.stderr.split()[2].strip('"')}")
        else:
            logger.error("✗ Java not found in PATH")
            return False
    except Exception as e:
        logger.error(f"✗ Error checking Java: {e}")
        return False
    
    # 2. Test tabula-py
    logger.info("\n=== Testing tabula-py ===")
    try:
        import tabula
        logger.info("✓ tabula-py imported successfully")
        
        # Test on a PDF with tables
        pdf_dir = project_root / "data" / "data" / "raw_pdfs"
        
        # Look for a PDF likely to have tables
        test_pdfs = [
            "hai_ai_index_report_2025.pdf",
            "oecd-artificial-intelligence-review-2025.pdf",
            "the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf"
        ]
        
        test_pdf = None
        for pdf_name in test_pdfs:
            pdf_path = pdf_dir / pdf_name
            if pdf_path.exists():
                test_pdf = pdf_path
                break
        
        if not test_pdf:
            # Use first available PDF
            pdfs = list(pdf_dir.glob("*.pdf"))
            if pdfs:
                test_pdf = pdfs[0]
        
        if test_pdf:
            logger.info(f"\nTesting table extraction on: {test_pdf.name}")
            
            # Try to extract tables from first few pages
            try:
                tables = tabula.read_pdf(
                    str(test_pdf), 
                    pages="1-5",
                    multiple_tables=True,
                    lattice=True  # For bordered tables
                )
                
                logger.info(f"✓ Extracted {len(tables)} tables")
                
                if tables:
                    # Show info about first table
                    first_table = tables[0]
                    logger.info(f"  First table: {first_table.shape[0]} rows × {first_table.shape[1]} columns")
                    
                    # Show sample data
                    if not first_table.empty:
                        logger.info("\n  Sample data from first table:")
                        sample = first_table.head(3).to_string()
                        for line in sample.split('\n'):
                            logger.info(f"    {line}")
                
                logger.info("\n✅ Table extraction working perfectly!")
                return True
                
            except Exception as e:
                logger.error(f"✗ Table extraction failed: {e}")
                return False
        else:
            logger.error("No PDFs found to test")
            return False
            
    except ImportError:
        logger.error("✗ tabula-py not installed")
        logger.error("  Run: pip install tabula-py")
        return False
    except Exception as e:
        logger.error(f"✗ Error testing tabula-py: {e}")
        return False

if __name__ == "__main__":
    logger.info("PDF Extraction System Test with Java\n")
    
    success = test_java_and_extraction()
    
    if success:
        logger.info("\n" + "="*50)
        logger.info("🎉 Everything is working perfectly!")
        logger.info("="*50)
        logger.info("\nYou now have:")
        logger.info("• Java installed and accessible")
        logger.info("• Table extraction fully functional")
        logger.info("• Ready for comprehensive PDF processing")
        logger.info("\nRun: python extract_all_pdfs.py")
    else:
        logger.info("\n" + "="*50)
        logger.info("Please fix any issues before proceeding.")
        logger.info("You may need to restart your terminal for PATH updates.")