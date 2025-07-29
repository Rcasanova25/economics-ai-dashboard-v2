"""Test pre-screening specifically on academic papers"""

from pathlib import Path
from pdf_prescreener import PDFPreScreener, create_prescreening_report

def test_academic_papers():
    """Test pre-screener on academic papers vs industry reports"""
    
    prescreener = PDFPreScreener(sample_pages=10)
    pdf_dir = Path("../data/data/raw_pdfs")
    
    # Focus on the academic papers
    academic_pdfs = [
        "Acemoglu_Macroeconomics-of-AI_May-2024 - Copy.pdf",
        "Economic_Impacts_Paper.pdf",
        "oecd-artificial-intelligence-review-2025.pdf"  # Also academic-style
    ]
    
    industry_pdfs = [
        "ai-and-the-global-economy.pdf",
        "the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf",
        "Mapping-AI-readiness-final.pdf"
    ]
    
    print("ACADEMIC vs INDUSTRY REPORT COMPARISON")
    print("="*60)
    
    # Test academic papers
    print("\nACADEMIC PAPERS:")
    print("-"*40)
    academic_results = {}
    
    for pdf_name in academic_pdfs:
        pdf_path = pdf_dir / pdf_name
        if pdf_path.exists():
            print(f"\nAnalyzing: {pdf_name[:50]}...")
            result = prescreener.prescreen(pdf_path)
            academic_results[pdf_name] = result
            
            print(f"Score: {result.total_score}/100 - {result.estimated_quality}")
            print(f"  Percentages: {result.percentage_count}")
            print(f"  Financial: {result.financial_count}")
            print(f"  Economic keywords: {result.economic_keyword_count}")
            print(f"  Recommendation: {result.recommendation}")
            
            if result.sample_metrics:
                try:
                    print(f"  Sample: {result.sample_metrics[0][:80]}...")
                except:
                    print("  Sample: [encoding error - contains special characters]")
    
    # Test industry reports for comparison
    print("\n\nINDUSTRY REPORTS:")
    print("-"*40)
    industry_results = {}
    
    for pdf_name in industry_pdfs:
        pdf_path = pdf_dir / pdf_name
        if pdf_path.exists():
            print(f"\nAnalyzing: {pdf_name[:50]}...")
            result = prescreener.prescreen(pdf_path)
            industry_results[pdf_name] = result
            
            print(f"Score: {result.total_score}/100 - {result.estimated_quality}")
            print(f"  Percentages: {result.percentage_count}")
            print(f"  Financial: {result.financial_count}")
            print(f"  Economic keywords: {result.economic_keyword_count}")
    
    # Summary comparison
    print("\n\nSUMMARY COMPARISON:")
    print("="*60)
    
    avg_academic = sum(r.total_score for r in academic_results.values()) / len(academic_results) if academic_results else 0
    avg_industry = sum(r.total_score for r in industry_results.values()) / len(industry_results) if industry_results else 0
    
    print(f"Average Academic Paper Score: {avg_academic:.1f}/100")
    print(f"Average Industry Report Score: {avg_industry:.1f}/100")
    print(f"Difference: {avg_industry - avg_academic:.1f} points")
    
    # Detailed comparison
    print("\n\nDETAILED METRICS:")
    print("-"*40)
    print("Academic papers average metrics:")
    if academic_results:
        avg_pct = sum(r.percentage_count for r in academic_results.values()) / len(academic_results)
        avg_fin = sum(r.financial_count for r in academic_results.values()) / len(academic_results)
        avg_kw = sum(r.economic_keyword_count for r in academic_results.values()) / len(academic_results)
        print(f"  Percentages: {avg_pct:.1f}")
        print(f"  Financial: {avg_fin:.1f}")
        print(f"  Keywords: {avg_kw:.1f}")
    
    print("\nIndustry reports average metrics:")
    if industry_results:
        avg_pct = sum(r.percentage_count for r in industry_results.values()) / len(industry_results)
        avg_fin = sum(r.financial_count for r in industry_results.values()) / len(industry_results)
        avg_kw = sum(r.economic_keyword_count for r in industry_results.values()) / len(industry_results)
        print(f"  Percentages: {avg_pct:.1f}")
        print(f"  Financial: {avg_fin:.1f}")
        print(f"  Keywords: {avg_kw:.1f}")
    
    # Test conclusion
    print("\n\nPRE-SCREENER EFFECTIVENESS:")
    print("-"*40)
    
    # How many were correctly classified?
    correct_academic = sum(1 for r in academic_results.values() if r.total_score < 40)
    correct_industry = sum(1 for r in industry_results.values() if r.total_score >= 40)
    
    total_correct = correct_academic + correct_industry
    total_pdfs = len(academic_results) + len(industry_results)
    
    accuracy = (total_correct / total_pdfs * 100) if total_pdfs > 0 else 0
    
    print(f"Correctly classified: {total_correct}/{total_pdfs} ({accuracy:.0f}%)")
    print(f"  Academic as low priority: {correct_academic}/{len(academic_results)}")
    print(f"  Industry as medium/high priority: {correct_industry}/{len(industry_results)}")
    
    if accuracy >= 80:
        print("\n✓ Pre-screener is working effectively!")
    else:
        print("\n⚠ Pre-screener may need adjustment")

if __name__ == "__main__":
    test_academic_papers()