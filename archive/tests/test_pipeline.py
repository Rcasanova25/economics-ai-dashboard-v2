"""
Test the full multi-stage pipeline on OECD AI Review PDF
"""

from pathlib import Path
import logging
from multi_stage_pipeline import MultiStagePipeline

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_pipeline():
    """Run full pipeline test on OECD PDF"""
    
    # Initialize pipeline
    pipeline = MultiStagePipeline()
    
    # Select OECD PDF
    pdf_path = Path("../data/data/raw_pdfs/oecd-artificial-intelligence-review-2025.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found at {pdf_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Testing Multi-Stage Pipeline on: {pdf_path.name}")
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
    for method, count in by_method.items():
        print(f"  {method}: {count}")
    
    # Analyze by confidence
    high_conf = [c for c in candidates if c.confidence_score >= 0.8]
    med_conf = [c for c in candidates if 0.5 <= c.confidence_score < 0.8]
    low_conf = [c for c in candidates if c.confidence_score < 0.5]
    
    print(f"\nConfidence distribution:")
    print(f"  High (≥0.8): {len(high_conf)}")
    print(f"  Medium (0.5-0.8): {len(med_conf)}")
    print(f"  Low (<0.5): {len(low_conf)}")
    
    # Show top 10 high-confidence candidates
    print(f"\nTop 10 High-Confidence Candidates:")
    print("-" * 60)
    
    for i, candidate in enumerate(high_conf[:10], 1):
        print(f"\n{i}. {candidate.numeric_value} {candidate.unit_hint}")
        print(f"   Page: {candidate.page_number} | Method: {candidate.extraction_method}")
        print(f"   Category: {candidate.suggested_category}")
        print(f"   Context: {candidate.surrounding_text[:100]}...")
        print(f"   Confidence: {candidate.confidence_score:.2f}")
    
    # Check output files
    output_dir = Path("extraction_output")
    candidate_file = output_dir / f"{pdf_path.name}_candidates.json"
    summary_file = output_dir / f"{pdf_path.name}_summary.json"
    
    print(f"\n{'='*60}")
    print("OUTPUT FILES")
    print(f"{'='*60}")
    print(f"\nCandidates saved to: {candidate_file}")
    print(f"Summary saved to: {summary_file}")
    
    print("\nNext steps:")
    print("1. Run 'python validation_ui.py' to start the validation interface")
    print("2. Open http://localhost:8050 in your browser")
    print(f"3. Select '{candidate_file.name}' from the dropdown")
    print("4. Review and validate candidates")
    print("5. Click 'Save Progress' to export validated metrics")
    
    return candidates

if __name__ == "__main__":
    candidates = test_pipeline()