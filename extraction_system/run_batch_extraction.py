"""
Batch extraction for priority PDFs
Run multi-stage extraction on pre-screened high-value PDFs
"""

from pathlib import Path
import logging
from datetime import datetime
from multi_stage_pipeline import MultiStagePipeline

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_batch_extraction():
    """Extract from priority PDFs based on pre-screening results"""
    
    # Priority PDFs from pre-screening
    priority_pdfs = [
        ("ai-and-the-global-economy.pdf", 70.3, "HIGH"),
        ("the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf", 64.5, "MEDIUM"),
        ("hai_ai_index_report_2025.pdf", 59.8, "MEDIUM"),
        ("Mapping-AI-readiness-final.pdf", 60.5, "MEDIUM")
    ]
    
    print("BATCH EXTRACTION PLAN")
    print("="*60)
    print(f"Starting: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Processing {len(priority_pdfs)} priority PDFs\n")
    
    # Show plan
    for pdf_name, score, priority in priority_pdfs:
        print(f"- {pdf_name[:50]:50} Score: {score} ({priority})")
    
    print("\nSkipping: OECD and academic papers (low scores)")
    print("-"*60)
    
    # Initialize pipeline
    pipeline = MultiStagePipeline()
    pdf_dir = Path("../data/data/raw_pdfs")
    
    # Track statistics
    total_candidates = 0
    extraction_times = []
    
    # Process each PDF
    for i, (pdf_name, score, priority) in enumerate(priority_pdfs, 1):
        pdf_path = pdf_dir / pdf_name
        
        if not pdf_path.exists():
            print(f"\nERROR: {pdf_name} not found!")
            continue
        
        print(f"\n[{i}/{len(priority_pdfs)}] Extracting: {pdf_name}")
        print("-"*40)
        
        start_time = datetime.now()
        
        try:
            # Run extraction
            candidates = pipeline.extract_from_pdf(pdf_path)
            
            # Calculate time
            extraction_time = (datetime.now() - start_time).total_seconds()
            extraction_times.append(extraction_time)
            
            # Report results
            print(f"SUCCESS: Extracted {len(candidates)} candidates in {extraction_time:.1f} seconds")
            
            # Quick quality check
            high_conf = len([c for c in candidates if c.confidence_score >= 0.8])
            print(f"  High confidence: {high_conf} ({high_conf/len(candidates)*100:.0f}%)")
            
            total_candidates += len(candidates)
            
        except Exception as e:
            print(f"FAILED: Extraction failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    
    print(f"\nTotal candidates extracted: {total_candidates}")
    print(f"Total time: {sum(extraction_times):.1f} seconds")
    print(f"Average time per PDF: {sum(extraction_times)/len(extraction_times):.1f} seconds")
    
    print("\nSUCCESS: Candidate files saved to: extraction_output/")
    print("\nNEXT STEPS:")
    print("1. Run validation UI: python validation_ui.py")
    print("2. Review and validate candidates")
    print("3. Export validated metrics")
    print("4. Build dashboard with clean data")
    
    # Create summary report
    summary_path = Path("extraction_output/batch_extraction_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Batch Extraction Summary\n")
        f.write(f"========================\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"PDFs processed: {len(priority_pdfs)}\n")
        f.write(f"Total candidates: {total_candidates}\n")
        f.write(f"Total time: {sum(extraction_times):.1f} seconds\n\n")
        
        f.write("Files processed:\n")
        for pdf_name, score, priority in priority_pdfs:
            f.write(f"- {pdf_name} (Score: {score})\n")
    
    print(f"\nSUCCESS: Summary saved to: {summary_path}")

if __name__ == "__main__":
    run_batch_extraction()