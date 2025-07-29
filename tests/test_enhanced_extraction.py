"""
Test Enhanced Stanford-aligned extraction on ai-and-the-global-economy.pdf
"""

import sys
from pathlib import Path
import logging
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_stanford_extractor import EnhancedStanfordExtractor
from economic_metrics_schema import EconomicMetric

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_enhanced_extraction():
    """Test enhanced extraction on pages 6-10"""
    
    extractor = EnhancedStanfordExtractor()
    
    pdf_path = Path("../data/data/raw_pdfs/ai-and-the-global-economy.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}")
        return
    
    print(f"Testing ENHANCED extraction on {pdf_path.name}")
    print("=" * 60)
    
    # Extract all metrics
    all_metrics = extractor.extract_from_pdf(pdf_path)
    
    # Filter to pages 6-10 for comparison with previous test
    test_metrics = [m for m in all_metrics if 6 <= m.page_number <= 10]
    
    print(f"\nExtracted {len(test_metrics)} metrics from pages 6-10")
    print(f"(Total {len(all_metrics)} metrics from entire PDF)")
    
    # Show structured metrics by country
    country_metrics = [m for m in test_metrics if m.geographic_scope.value == "country"]
    if country_metrics:
        print("\n--- Country-Specific Adoption Rates ---")
        for metric in sorted(country_metrics, key=lambda x: x.value, reverse=True):
            print(f"{metric.geographic_detail}: {metric.value}% - {metric.description}")
            print(f"  Context: {metric.context[:100]}...")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    
    # Group by category
    by_category = {}
    for metric in test_metrics:
        cat = metric.category.value
        by_category[cat] = by_category.get(cat, 0) + 1
    
    print("\nMetrics by category:")
    for cat, count in sorted(by_category.items()):
        print(f"  {cat}: {count}")
    
    # Show value ranges
    print("\nValue ranges by unit:")
    by_unit = {}
    for metric in test_metrics:
        unit = metric.unit.value
        if unit not in by_unit:
            by_unit[unit] = []
        by_unit[unit].append(metric.value)
    
    for unit, values in sorted(by_unit.items()):
        if values:
            # Filter out obvious chart artifacts
            filtered_values = [v for v in values if v not in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]]
            if filtered_values:
                print(f"  {unit}: {min(filtered_values):.1f} - {max(filtered_values):.1f} (n={len(filtered_values)})")
    
    # Quality distribution
    print("\nData quality distribution:")
    quality_dist = {}
    for metric in test_metrics:
        q = metric.data_quality.value
        quality_dist[q] = quality_dist.get(q, 0) + 1
    
    for quality, count in sorted(quality_dist.items()):
        print(f"  {quality}: {count}")
    
    # Save detailed results
    if test_metrics:
        results = []
        for m in test_metrics:
            results.append({
                'page': m.page_number,
                'category': m.category.value,
                'type': m.metric_type.value,
                'value': m.value,
                'unit': m.unit.value,
                'year': m.year,
                'geography': m.geographic_detail or m.geographic_scope.value,
                'sector': m.sector_detail or m.sector.value,
                'company_size': m.company_size.value if m.company_size else None,
                'description': m.description,
                'context': m.context[:200],
                'quality': m.data_quality.value,
                'confidence': m.confidence_score
            })
        
        df = pd.DataFrame(results)
        output_path = "enhanced_extraction_results.csv"
        df.to_csv(output_path, index=False)
        print(f"\nDetailed results saved to {output_path}")
        
        # Compare with original extraction
        print("\n--- Comparison with Original Extraction ---")
        print("Original: 41 metrics (many duplicates and chart artifacts)")
        print(f"Enhanced: {len(test_metrics)} metrics (deduplicated and filtered)")
        
        # Show unique values to demonstrate deduplication
        unique_values = df['value'].unique()
        print(f"\nUnique values extracted: {len(unique_values)}")
        print("Sample values:", sorted(unique_values)[:10])

if __name__ == "__main__":
    test_enhanced_extraction()