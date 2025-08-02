"""
Multi-Stage Extraction Pipeline
Combines multiple extraction methods with human validation
Quality over quantity approach
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import fitz  # PyMuPDF
import pandas as pd
import tabula

from economic_metrics_schema import (
    MetricCategory, MetricType, Unit,
    GeographicScope, Sector, DataQuality
)


@dataclass
class MetricCandidate:
    """Candidate metric for human validation"""
    candidate_id: str
    source_document: str
    page_number: int
    extraction_method: str  # text, table, ocr, pattern
    
    # Extracted data
    raw_value: str
    numeric_value: float
    unit_hint: str
    
    # Context
    surrounding_text: str
    confidence_score: float
    
    # Suggested classification
    suggested_category: str
    suggested_type: str
    suggested_geography: str
    
    # Validation
    is_validated: bool = False
    validation_decision: str = ""  # accept, reject, modify
    validated_category: str = ""
    validated_type: str = ""
    notes: str = ""


class MultiStagePipeline:
    """Orchestrates multiple extraction methods"""
    
    def __init__(self, output_dir: Path = Path("extraction_output")):
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # Confidence thresholds
        self.MIN_CONFIDENCE = 0.3  # Include uncertain candidates for human review
        self.HIGH_CONFIDENCE = 0.8  # Pre-populate suggestions for these
        
    def extract_from_pdf(self, pdf_path: Path) -> List[MetricCandidate]:
        """Run all extraction stages on a PDF"""
        
        self.logger.info(f"Starting multi-stage extraction for {pdf_path.name}")
        candidates = []
        
        # Stage 1: Text extraction for inline metrics
        text_candidates = self._stage1_text_extraction(pdf_path)
        candidates.extend(text_candidates)
        self.logger.info(f"Stage 1 (Text): Found {len(text_candidates)} candidates")
        
        # Stage 2: Table extraction with tabula-py
        table_candidates = self._stage2_table_extraction(pdf_path)
        candidates.extend(table_candidates)
        self.logger.info(f"Stage 2 (Tables): Found {len(table_candidates)} candidates")
        
        # Stage 3: Pattern matching for known formats
        pattern_candidates = self._stage3_pattern_matching(pdf_path)
        candidates.extend(pattern_candidates)
        self.logger.info(f"Stage 3 (Patterns): Found {len(pattern_candidates)} candidates")
        
        # Stage 4: Deduplication and ranking
        unique_candidates = self._stage4_deduplication(candidates)
        self.logger.info(f"Stage 4 (Dedup): Reduced to {len(unique_candidates)} unique candidates")
        
        # Stage 5: Classification and context enhancement
        enriched_candidates = self._stage5_enrichment(unique_candidates)
        self.logger.info(f"Stage 5 (Enrichment): Enhanced {len(enriched_candidates)} candidates")
        
        # Save candidates for validation
        self._save_candidates(enriched_candidates, pdf_path.name)
        
        return enriched_candidates
    
    def _stage1_text_extraction(self, pdf_path: Path) -> List[MetricCandidate]:
        """Extract inline metrics from text"""
        candidates = []
        
        doc = fitz.open(pdf_path)
        
        # Patterns for inline metrics
        patterns = [
            # Percentages
            (r'(\d+(?:\.\d+)?)\s*%\s+of\s+([\w\s]+)', 'percentage'),
            (r'(\d+(?:\.\d+)?)\s*percent\s+of\s+([\w\s]+)', 'percentage'),
            # Financial
            (r'\$\s*(\d+(?:\.\d+)?)\s*(billion|million)', 'financial'),
            (r'(\d+(?:\.\d+)?)\s*(billion|million)\s*(?:USD|dollars)', 'financial'),
            # Growth rates
            (r'(\d+(?:\.\d+)?)\s*%\s+(?:growth|increase|decrease)', 'rate'),
            # Years with metrics
            (r'(?:in|by)\s+(20\d{2})[,:\s]+(\d+(?:\.\d+)?)\s*%', 'temporal'),
        ]
        
        import re
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            
            for pattern, hint in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        # Extract value
                        value_str = match.group(1)
                        value = float(value_str)
                        
                        # Skip likely years
                        if 2000 <= value <= 2030 and hint != 'temporal':
                            continue
                        
                        # Get surrounding context
                        start = max(0, match.start() - 100)
                        end = min(len(text), match.end() + 100)
                        context = text[start:end].strip()
                        
                        # Create candidate
                        candidate = MetricCandidate(
                            candidate_id=f"{pdf_path.stem}_p{page_num}_t{len(candidates)}",
                            source_document=pdf_path.name,
                            page_number=page_num,
                            extraction_method="text",
                            raw_value=match.group(0),
                            numeric_value=value,
                            unit_hint=hint,
                            surrounding_text=context,
                            confidence_score=0.7,
                            suggested_category=self._suggest_category(context),
                            suggested_type=self._suggest_type(context, hint),
                            suggested_geography=self._extract_geography(context)
                        )
                        
                        candidates.append(candidate)
                        
                    except ValueError:
                        continue
        
        doc.close()
        return candidates
    
    def _stage2_table_extraction(self, pdf_path: Path) -> List[MetricCandidate]:
        """Extract metrics from tables using tabula-py"""
        candidates = []
        
        try:
            # Extract all tables from PDF
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                pandas_options={'header': None}
            )
            
            for page_idx, table in enumerate(tables):
                if table.empty:
                    continue
                    
                # Process each cell in the table
                for row_idx, row in table.iterrows():
                    for col_idx, cell in enumerate(row):
                        if pd.isna(cell):
                            continue
                            
                        cell_str = str(cell)
                        
                        # Look for numeric values
                        import re
                        numeric_match = re.search(r'(\d+(?:\.\d+)?)\s*(%|billion|million)?', cell_str)
                        
                        if numeric_match:
                            try:
                                value = float(numeric_match.group(1))
                                unit_hint = numeric_match.group(2) or ""
                                
                                # Get context from surrounding cells
                                context_parts = []
                                
                                # Row header (first column)
                                if col_idx > 0 and not pd.isna(row[0]):
                                    context_parts.append(str(row[0]))
                                
                                # Column header (first row)
                                if row_idx > 0 and not pd.isna(table.iloc[0, col_idx]):
                                    context_parts.append(str(table.iloc[0, col_idx]))
                                
                                context = " | ".join(context_parts)
                                
                                candidate = MetricCandidate(
                                    candidate_id=f"{pdf_path.stem}_tbl{page_idx}_r{row_idx}c{col_idx}",
                                    source_document=pdf_path.name,
                                    page_number=page_idx + 1,  # Approximate
                                    extraction_method="table",
                                    raw_value=cell_str,
                                    numeric_value=value,
                                    unit_hint=unit_hint,
                                    surrounding_text=context,
                                    confidence_score=0.8,  # Tables are usually structured
                                    suggested_category=self._suggest_category(context),
                                    suggested_type=self._suggest_type(context, unit_hint),
                                    suggested_geography=self._extract_geography(context)
                                )
                                
                                candidates.append(candidate)
                                
                            except ValueError:
                                continue
                                
        except Exception as e:
            self.logger.warning(f"Table extraction failed: {e}")
            
        return candidates
    
    def _stage3_pattern_matching(self, pdf_path: Path) -> List[MetricCandidate]:
        """Apply known patterns for specific report types"""
        candidates = []
        
        # Identify report type
        report_patterns = {
            "mckinsey": ["McKinsey", "mckinsey.com"],
            "oecd": ["OECD", "oecd.org"],
            "stanford": ["Stanford", "HAI"],
        }
        
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text().lower()
        doc.close()
        
        report_type = None
        for rtype, patterns in report_patterns.items():
            if any(p.lower() in first_page_text for p in patterns):
                report_type = rtype
                break
        
        if not report_type:
            return candidates
        
        # Apply report-specific patterns
        doc = fitz.open(pdf_path)
        
        if report_type == "mckinsey":
            # McKinsey-specific patterns
            patterns = [
                r'(\d+)\s*percent\s+of\s+executives',
                r'(\d+)%\s+(?:increase|improvement)\s+in',
                r'ROI\s+of\s+(\d+)%',
            ]
        elif report_type == "oecd":
            # OECD-specific patterns
            patterns = [
                r'(\d+(?:\.\d+)?)\s*%\s+of\s+GDP',
                r'(\d+)\s+countries',
                r'average\s+of\s+(\d+(?:\.\d+)?)\s*%',
            ]
        else:
            patterns = []
        
        import re
        
        for page_num, page in enumerate(doc, 1):
            text = page.get_text()
            
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    try:
                        value = float(match.group(1))
                        
                        # Context
                        start = max(0, match.start() - 150)
                        end = min(len(text), match.end() + 150)
                        context = text[start:end].strip()
                        
                        candidate = MetricCandidate(
                            candidate_id=f"{pdf_path.stem}_p{page_num}_pat{len(candidates)}",
                            source_document=pdf_path.name,
                            page_number=page_num,
                            extraction_method="pattern",
                            raw_value=match.group(0),
                            numeric_value=value,
                            unit_hint="percentage",
                            surrounding_text=context,
                            confidence_score=0.85,  # High confidence for specific patterns
                            suggested_category=self._suggest_category(context),
                            suggested_type=self._suggest_type(context, "percentage"),
                            suggested_geography=self._extract_geography(context)
                        )
                        
                        candidates.append(candidate)
                        
                    except ValueError:
                        continue
        
        doc.close()
        return candidates
    
    def _stage4_deduplication(self, candidates: List[MetricCandidate]) -> List[MetricCandidate]:
        """Remove duplicate candidates"""
        unique = []
        seen = set()
        
        for candidate in candidates:
            # Create signature for deduplication
            sig = (
                candidate.page_number,
                candidate.numeric_value,
                candidate.unit_hint,
                # Include first 50 chars of context to differentiate same values
                candidate.surrounding_text[:50]
            )
            
            if sig not in seen:
                seen.add(sig)
                unique.append(candidate)
            else:
                # If duplicate, keep the one with higher confidence
                for idx, existing in enumerate(unique):
                    if (existing.page_number == candidate.page_number and
                        existing.numeric_value == candidate.numeric_value and
                        existing.unit_hint == candidate.unit_hint):
                        if candidate.confidence_score > existing.confidence_score:
                            unique[idx] = candidate
                        break
        
        return unique
    
    def _stage5_enrichment(self, candidates: List[MetricCandidate]) -> List[MetricCandidate]:
        """Enhance candidates with better classification"""
        
        for candidate in candidates:
            # Enhance category suggestion
            if candidate.confidence_score >= self.HIGH_CONFIDENCE:
                candidate.suggested_category = self._suggest_category_enhanced(
                    candidate.surrounding_text,
                    candidate.unit_hint
                )
                
            # Add validation hints
            if candidate.numeric_value > 100 and candidate.unit_hint == "percentage":
                candidate.notes = "Warning: Percentage > 100"
                candidate.confidence_score *= 0.5
                
            # Flag potential issues
            if 2000 <= candidate.numeric_value <= 2030:
                candidate.notes = "Possible year misidentified as metric"
                candidate.confidence_score *= 0.7
        
        # Sort by confidence for review priority
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return candidates
    
    def _suggest_category(self, context: str) -> str:
        """Suggest metric category based on context"""
        context_lower = context.lower()
        
        category_keywords = {
            "adoption": ["adopt", "using", "implement", "deploy"],
            "investment": ["invest", "funding", "capital", "billion", "million"],
            "labor_market": ["job", "employ", "hire", "talent", "worker"],
            "productivity": ["productiv", "efficien", "output", "performance"],
            "cost": ["cost", "expense", "budget", "spend", "roi"],
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in context_lower for kw in keywords):
                return category
                
        return "unknown"
    
    def _suggest_type(self, context: str, unit_hint: str) -> str:
        """Suggest metric type based on context and unit"""
        context_lower = context.lower()
        
        if unit_hint == "percentage":
            if "adopt" in context_lower:
                return "adoption_rate"
            elif "growth" in context_lower or "increase" in context_lower:
                return "growth_rate"
            elif "job" in context_lower:
                return "job_postings_rate"
                
        elif unit_hint == "financial":
            if "invest" in context_lower or "funding" in context_lower:
                return "investment_amount"
            elif "revenue" in context_lower:
                return "revenue"
                
        return "general_metric"
    
    def _extract_geography(self, context: str) -> str:
        """Extract geographic information from context"""
        context_lower = context.lower()
        
        countries = [
            "united states", "usa", "china", "india", "germany",
            "united kingdom", "uk", "france", "japan", "canada"
        ]
        
        for country in countries:
            if country in context_lower:
                return country.title()
                
        if "global" in context_lower or "worldwide" in context_lower:
            return "Global"
            
        return "Not specified"
    
    def _suggest_category_enhanced(self, context: str, unit_hint: str) -> str:
        """Enhanced category suggestion with unit consideration"""
        base_category = self._suggest_category(context)
        
        # Override based on unit
        if unit_hint == "financial" and base_category == "unknown":
            return "investment"
        elif unit_hint == "percentage" and "compan" in context.lower():
            return "adoption"
            
        return base_category
    
    def _save_candidates(self, candidates: List[MetricCandidate], source_name: str):
        """Save candidates to JSON for validation UI"""
        
        # Convert to serializable format
        candidates_data = []
        for candidate in candidates:
            data = asdict(candidate)
            # Add metadata
            data['extraction_timestamp'] = datetime.now().isoformat()
            data['pipeline_version'] = "1.0"
            candidates_data.append(data)
        
        # Save to JSON
        output_file = self.output_dir / f"{source_name}_candidates.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(candidates_data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {len(candidates)} candidates to {output_file}")
        
        # Also save summary statistics
        summary = {
            "source_document": source_name,
            "total_candidates": len(candidates),
            "by_extraction_method": {},
            "by_confidence": {
                "high": len([c for c in candidates if c.confidence_score >= 0.8]),
                "medium": len([c for c in candidates if 0.5 <= c.confidence_score < 0.8]),
                "low": len([c for c in candidates if c.confidence_score < 0.5]),
            },
            "by_category": {}
        }
        
        # Count by method
        for candidate in candidates:
            method = candidate.extraction_method
            summary["by_extraction_method"][method] = summary["by_extraction_method"].get(method, 0) + 1
            
            category = candidate.suggested_category
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        summary_file = self.output_dir / f"{source_name}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)


# Example usage
if __name__ == "__main__":
    pipeline = MultiStagePipeline()
    
    # Test on a PDF
    pdf_path = Path("../data/data/raw_pdfs/ai-and-the-global-economy.pdf")
    if pdf_path.exists():
        candidates = pipeline.extract_from_pdf(pdf_path)
        print(f"\nExtracted {len(candidates)} metric candidates")
        print("\nTop 5 high-confidence candidates:")
        for candidate in candidates[:5]:
            print(f"\n{candidate.numeric_value} {candidate.unit_hint}")
            print(f"  Category: {candidate.suggested_category}")
            print(f"  Context: {candidate.surrounding_text[:100]}...")
            print(f"  Confidence: {candidate.confidence_score:.2f}")