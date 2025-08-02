"""
Economic Metrics Extraction Schema
Based on Stanford AI Index structure with extensions for comprehensive economic analysis
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict
from datetime import datetime


class MetricCategory(Enum):
    """Primary economic categories aligned with Stanford AI Index"""
    LABOR_MARKET = "labor_market"          # Jobs, skills, talent
    INVESTMENT = "investment"              # VC, M&A, R&D spending  
    ADOPTION = "adoption"                  # Implementation rates
    PRODUCTIVITY = "productivity"          # Output, efficiency gains
    COST = "cost"                         # Implementation costs, ROI
    MARKET_SIZE = "market_size"           # Revenue, market value
    INNOVATION = "innovation"             # Patents, research output


class MetricType(Enum):
    """Specific metric types within categories"""
    # Labor Market
    JOB_POSTINGS_RATE = "job_postings_rate"
    TALENT_CONCENTRATION = "talent_concentration"
    SKILL_DEMAND = "skill_demand"
    WAGE_PREMIUM = "wage_premium"
    EMPLOYMENT_IMPACT = "employment_impact"
    
    # Investment
    VC_FUNDING = "vc_funding"
    MA_ACTIVITY = "ma_activity"
    RD_SPENDING = "rd_spending"
    CORPORATE_INVESTMENT = "corporate_investment"
    GOVERNMENT_FUNDING = "government_funding"
    
    # Adoption
    ADOPTION_RATE = "adoption_rate"
    IMPLEMENTATION_STAGE = "implementation_stage"
    USE_CASE_PENETRATION = "use_case_penetration"
    TECHNOLOGY_MATURITY = "technology_maturity"
    
    # Productivity
    OUTPUT_GAIN = "output_gain"
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement"
    TIME_SAVINGS = "time_savings"
    QUALITY_IMPROVEMENT = "quality_improvement"
    AUTOMATION_RATE = "automation_rate"
    
    # Cost
    IMPLEMENTATION_COST = "implementation_cost"
    OPERATIONAL_COST = "operational_cost"
    ROI = "roi"
    PAYBACK_PERIOD = "payback_period"
    COST_REDUCTION = "cost_reduction"
    
    # Market Size
    MARKET_VALUE = "market_value"
    REVENUE = "revenue"
    GROWTH_RATE = "growth_rate"
    MARKET_SHARE = "market_share"


class Unit(Enum):
    """Standardized units for economic metrics"""
    # Percentage units
    PERCENTAGE = "percentage"
    PERCENTAGE_POINT = "percentage_point"
    
    # Monetary units
    USD = "usd"
    USD_MILLIONS = "usd_millions"
    USD_BILLIONS = "usd_billions"
    
    # Count units
    COUNT = "count"
    THOUSANDS = "thousands"
    MILLIONS = "millions"
    
    # Time units
    YEARS = "years"
    MONTHS = "months"
    HOURS = "hours"
    
    # Rate units
    CAGR = "cagr"  # Compound Annual Growth Rate
    YOY = "yoy"    # Year-over-year


class GeographicScope(Enum):
    """Geographic categorization"""
    GLOBAL = "global"
    REGIONAL = "regional"
    COUNTRY = "country"
    STATE_PROVINCE = "state_province"
    CITY = "city"


class Sector(Enum):
    """Industry sectors - expandable based on PDF content"""
    ALL_SECTORS = "all_sectors"
    TECHNOLOGY = "technology"
    FINANCIAL_SERVICES = "financial_services"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    EDUCATION = "education"
    GOVERNMENT = "government"
    TELECOMMUNICATIONS = "telecommunications"
    MEDIA_ENTERTAINMENT = "media_entertainment"
    PROFESSIONAL_SERVICES = "professional_services"


class CompanySize(Enum):
    """Company size categories"""
    ALL_SIZES = "all_sizes"
    ENTERPRISE = "enterprise"      # 1000+ employees
    MID_MARKET = "mid_market"      # 100-999 employees
    SMB = "smb"                    # <100 employees
    STARTUP = "startup"            # <10 employees


class DataQuality(Enum):
    """Confidence in extracted data"""
    HIGH = "high"          # Explicit number with clear context
    MEDIUM = "medium"      # Requires some interpretation
    LOW = "low"           # Inferred or approximate


@dataclass
class EconomicMetric:
    """Core data model for extracted economic metrics"""
    # Identification
    metric_id: str                      # Unique identifier
    source_document: str                # PDF filename
    page_number: int                    # Page where found
    
    # Temporal
    year: Optional[int]                 # Specific year
    time_period: Optional[str]          # E.g., "Q1 2024", "2020-2023"
    forecast_year: Optional[int]        # If projection
    
    # Metric details
    category: MetricCategory
    metric_type: MetricType
    value: float
    unit: Unit
    
    # Dimensions
    geographic_scope: GeographicScope
    geographic_detail: Optional[str]    # E.g., "United States", "Europe"
    sector: Sector
    sector_detail: Optional[str]        # E.g., "Investment Banking"
    company_size: Optional[CompanySize]
    
    # Context
    description: str                    # What this metric measures
    methodology: Optional[str]          # How it was calculated
    sample_size: Optional[str]          # Survey respondents, etc.
    context: str                        # Surrounding text
    
    # Quality
    data_quality: DataQuality
    confidence_score: float             # 0-1 confidence
    is_projection: bool                 # Future estimate vs historical
    
    # Tracking
    extracted_at: datetime
    extractor_version: str


@dataclass
class ExtractionTarget:
    """Defines what to look for in PDFs"""
    category: MetricCategory
    metric_types: List[MetricType]
    keywords: List[str]                 # Terms that signal this metric
    patterns: List[str]                 # Regex patterns
    units: List[Unit]                   # Expected units
    
    # Validation rules
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    require_year: bool = True
    require_geography: bool = False


# Pre-defined extraction targets based on Stanford structure
EXTRACTION_TARGETS = [
    ExtractionTarget(
        category=MetricCategory.LABOR_MARKET,
        metric_types=[MetricType.JOB_POSTINGS_RATE, MetricType.TALENT_CONCENTRATION],
        keywords=["job postings", "AI talent", "AI jobs", "hiring", "workforce"],
        patterns=[r"\d+(\.\d+)?%?\s*of\s*(all\s*)?job\s*postings?"],
        units=[Unit.PERCENTAGE, Unit.COUNT, Unit.THOUSANDS]
    ),
    ExtractionTarget(
        category=MetricCategory.INVESTMENT,
        metric_types=[MetricType.VC_FUNDING, MetricType.MA_ACTIVITY],
        keywords=["investment", "funding", "venture capital", "M&A", "acquisition"],
        patterns=[r"\$?\d+(\.\d+)?\s*(billion|million|B|M)\s*(USD)?"],
        units=[Unit.USD_BILLIONS, Unit.USD_MILLIONS]
    ),
    ExtractionTarget(
        category=MetricCategory.ADOPTION,
        metric_types=[MetricType.ADOPTION_RATE, MetricType.USE_CASE_PENETRATION],
        keywords=["adoption", "implementation", "using AI", "deployed", "penetration"],
        patterns=[r"\d+(\.\d+)?%?\s*of\s*(companies|organizations|firms)"],
        units=[Unit.PERCENTAGE]
    ),
    ExtractionTarget(
        category=MetricCategory.PRODUCTIVITY,
        metric_types=[MetricType.OUTPUT_GAIN, MetricType.EFFICIENCY_IMPROVEMENT],
        keywords=["productivity", "efficiency", "output", "performance", "improvement"],
        patterns=[r"\d+(\.\d+)?%?\s*(increase|improvement|gain|growth)"],
        units=[Unit.PERCENTAGE, Unit.PERCENTAGE_POINT]
    ),
    ExtractionTarget(
        category=MetricCategory.COST,
        metric_types=[MetricType.ROI, MetricType.COST_REDUCTION],
        keywords=["ROI", "return on investment", "cost savings", "payback", "cost reduction"],
        patterns=[r"\d+(\.\d+)?%?\s*(ROI|return|savings)"],
        units=[Unit.PERCENTAGE, Unit.USD_MILLIONS, Unit.YEARS]
    )
]


def validate_metric(metric: EconomicMetric) -> tuple[bool, str]:
    """Validate an extracted metric against business rules"""
    # Check year makes sense
    if metric.year and (metric.year < 2010 or metric.year > 2030):
        return False, f"Invalid year: {metric.year}"
    
    # Check value ranges by metric type
    if metric.unit == Unit.PERCENTAGE:
        if metric.value < 0 or metric.value > 100:
            return False, f"Invalid percentage: {metric.value}"
    
    # Ensure financial metrics aren't tiny
    if metric.unit in [Unit.USD_BILLIONS] and metric.value < 0.01:
        return False, f"Suspiciously small billions value: {metric.value}"
    
    # Check category/type alignment
    if metric.category == MetricCategory.LABOR_MARKET:
        if metric.unit in [Unit.USD_BILLIONS, Unit.USD_MILLIONS]:
            return False, "Labor market metric with financial unit"
    
    return True, "Valid"


def should_extract_metric(text: str, target: ExtractionTarget) -> bool:
    """Determine if text segment contains target metric"""
    text_lower = text.lower()
    
    # Check for any keywords
    if not any(keyword in text_lower for keyword in target.keywords):
        return False
    
    # Check for numeric values
    import re
    if not re.search(r'\d+(\.\d+)?', text):
        return False
    
    # Avoid citation years
    if re.search(r'\(\d{4}\)', text):
        return False
    
    return True


# Example usage pattern
if __name__ == "__main__":
    # Example metric that would be extracted
    example = EconomicMetric(
        metric_id="MCK_2024_001",
        source_document="mckinsey_ai_state_2024.pdf",
        page_number=15,
        year=2024,
        time_period="2024",
        forecast_year=None,
        category=MetricCategory.ADOPTION,
        metric_type=MetricType.ADOPTION_RATE,
        value=72.0,
        unit=Unit.PERCENTAGE,
        geographic_scope=GeographicScope.GLOBAL,
        geographic_detail=None,
        sector=Sector.ALL_SECTORS,
        sector_detail=None,
        company_size=CompanySize.ENTERPRISE,
        description="Percentage of enterprises that have adopted AI in at least one business function",
        methodology="Survey of 1,000+ companies",
        sample_size="1,243 respondents",
        context="Our latest survey shows that 72% of enterprises have adopted AI...",
        data_quality=DataQuality.HIGH,
        confidence_score=0.95,
        is_projection=False,
        extracted_at=datetime.now(),
        extractor_version="2.0"
    )
    
    is_valid, message = validate_metric(example)
    print(f"Metric valid: {is_valid} - {message}")