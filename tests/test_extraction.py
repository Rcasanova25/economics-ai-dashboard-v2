"""
Test Stanford-aligned extraction on a section of ai-and-the-global-economy.pdf
"""

import sys
from pathlib import Path
import logging
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from stanford_aligned_extractor import StanfordAlignedExtractor
from economic_metrics_schema import EconomicMetric

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_extraction_on_section():
    """Test extraction on pages 6-10 which contain adoption and revenue metrics"""
    
    extractor = StanfordAlignedExtractor()
    
    # Extract specific pages for testing
    import fitz
    pdf_path = Path("../data/data/raw_pdfs/ai-and-the-global-economy.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}")
        return
    
    print(f"Testing extraction on {pdf_path.name}")
    print("=" * 60)
    
    # Extract from pages 6-10 (contain adoption rates, revenue impacts)
    doc = fitz.open(pdf_path)
    
    all_metrics = []
    
    for page_num in range(5, 10):  # Pages 6-10 (0-indexed)
        page = doc[page_num]
        text = page.get_text()
        
        print(f"\n--- Extracting from Page {page_num + 1} ---")
        
        # Use the extractor's internal method for testing
        from economic_metrics_schema import EXTRACTION_TARGETS
        
        page_metrics = []
        for target in EXTRACTION_TARGETS:
            metrics = extractor._extract_metrics_from_text(
                text, target, pdf_path.name, page_num + 1
            )
            page_metrics.extend(metrics)
        
        print(f"Found {len(page_metrics)} metrics on page {page_num + 1}")
        
        # Show details of each metric
        for metric in page_metrics:
            print(f"\n  Metric: {metric.value} {metric.unit.value}")
            print(f"  Category: {metric.category.value}")
            print(f"  Type: {metric.metric_type.value}")
            print(f"  Context: {metric.context[:100]}...")
            print(f"  Quality: {metric.data_quality.value}")
            print(f"  Confidence: {metric.confidence_score:.2f}")
            
        all_metrics.extend(page_metrics)
    
    doc.close()
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total metrics extracted: {len(all_metrics)}")
    
    # Group by category
    by_category = {}
    for metric in all_metrics:
        cat = metric.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nMetrics by category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")
    
    # Show value ranges
    print("\nValue ranges by unit:")
    by_unit = {}
    for metric in all_metrics:
        unit = metric.unit.value
        if unit not in by_unit:
            by_unit[unit] = []
        by_unit[unit].append(metric.value)
    
    for unit, values in sorted(by_unit.items()):
        if values:
            print(f"  {unit}: {min(values):.1f} - {max(values):.1f}")
    
    # Save results for analysis
    if all_metrics:
        results = []
        for m in all_metrics:
            results.append({
                'page': m.page_number,
                'category': m.category.value,
                'type': m.metric_type.value,
                'value': m.value,
                'unit': m.unit.value,
                'year': m.year,
                'geography': m.geographic_detail or m.geographic_scope.value,
                'sector': m.sector_detail or m.sector.value,
                'context': m.context[:200],
                'quality': m.data_quality.value,
                'confidence': m.confidence_score
            })
        
        df = pd.DataFrame(results)
        output_path = "test_extraction_results.csv"
        df.to_csv(output_path, index=False)
        print(f"\nResults saved to {output_path}")
        
        # Show top 5 high-confidence metrics
        print("\nTop 5 high-confidence metrics:")
        top_metrics = df.nlargest(5, 'confidence')
        for _, row in top_metrics.iterrows():
            print(f"\n  {row['value']} {row['unit']} - {row['type']}")
            print(f"  Context: {row['context'][:100]}...")

if __name__ == "__main__":
    test_extraction_on_section()