"""
Test multi-stage pipeline on McKinsey PDF
McKinsey reports typically have more economic metrics
"""

from pathlib import Path
import logging
from multi_stage_pipeline import MultiStagePipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_mckinsey():
    """Run pipeline on McKinsey PDF"""
    
    # Initialize pipeline
    pipeline = MultiStagePipeline()
    
    # McKinsey PDF
    pdf_path = Path("../data/data/raw_pdfs/the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Testing Multi-Stage Pipeline on McKinsey Report")
    print(f"PDF: {pdf_path.name}")
    print(f"{'='*60}\n")
    
    # Run extraction
    candidates = pipeline.extract_from_pdf(pdf_path)
    
    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*60}")
    
    print(f"\nTotal candidates extracted: {len(candidates)}")
    
    # Analyze by extraction method
    by_method = {}
    for c in candidates:
        method = c.extraction_method
        by_method[method] = by_method.get(method, 0) + 1
    
    print("\nCandidates by extraction method:")
    for method, count in sorted(by_method.items()):
        print(f"  {method}: {count}")
    
    # Analyze by confidence
    high_conf = [c for c in candidates if c.confidence_score >= 0.8]
    med_conf = [c for c in candidates if 0.5 <= c.confidence_score < 0.8]
    low_conf = [c for c in candidates if c.confidence_score < 0.5]
    
    print(f"\nConfidence distribution:")
    print(f"  High (>=0.8): {len(high_conf)}")
    print(f"  Medium (0.5-0.8): {len(med_conf)}")
    print(f"  Low (<0.5): {len(low_conf)}")
    
    # Filter meaningful candidates (>10 or has unit)
    meaningful = [c for c in candidates if c.numeric_value > 10 or c.unit_hint]
    
    print(f"\nPotentially meaningful candidates: {len(meaningful)}")
    
    # Show top 15 meaningful candidates
    print(f"\nTop 15 Meaningful Candidates:")
    print("-" * 80)
    
    # Sort by confidence and value
    meaningful.sort(key=lambda x: (x.confidence_score, x.numeric_value), reverse=True)
    
    for i, candidate in enumerate(meaningful[:15], 1):
        print(f"\n{i}. {candidate.numeric_value} {candidate.unit_hint}")
        print(f"   Page: {candidate.page_number} | Method: {candidate.extraction_method}")
        print(f"   Category: {candidate.suggested_category}")
        print(f"   Context: {candidate.surrounding_text[:150]}...")
        print(f"   Confidence: {candidate.confidence_score:.2f}")
    
    # Category distribution
    print(f"\n{'='*60}")
    print("CATEGORY DISTRIBUTION")
    print(f"{'='*60}")
    
    by_category = {}
    for c in meaningful:
        cat = c.suggested_category
        by_category[cat] = by_category.get(cat, 0) + 1
    
    for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")
    
    # Output info
    output_dir = Path("extraction_output")
    candidate_file = output_dir / f"{pdf_path.name}_candidates.json"
    
    print(f"\n{'='*60}")
    print("NEXT STEPS")
    print(f"{'='*60}")
    print(f"\nCandidates saved to: {candidate_file.name}")
    print("\n1. Run 'python validation_ui.py' to validate")
    print("2. Open http://localhost:8050")
    print(f"3. Select '{candidate_file.name}'")
    print("4. This should have better economic metrics than OECD!")

if __name__ == "__main__":
    test_mckinsey()