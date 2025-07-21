"""
Data Models for Economics AI Dashboard

Think of these as standardized forms for collecting AI adoption data.
Just like economic surveys have standard fields, our data has standard structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DataSource(Enum):
    """
    Where did this data come from? 
    Like citing sources in an economic paper.
    """
    STANFORD_HAI = "Stanford HAI AI Index"
    MCKINSEY = "McKinsey Global Institute"
    OECD = "OECD AI Policy Observatory"
    GOLDMAN_SACHS = "Goldman Sachs Research"
    NVIDIA = "NVIDIA Research"
    FEDERAL_RESERVE = "Federal Reserve Papers"
    ACADEMIC_PAPER = "Academic Research Paper"
    OTHER = "Other Source"


class MetricType(Enum):
    """
    What kind of economic metric is this?
    Like distinguishing between GDP, unemployment rate, etc.
    """
    ADOPTION_RATE = "adoption_rate"  # Percentage of firms using AI
    INVESTMENT = "investment"  # Dollar amount invested in AI
    PRODUCTIVITY = "productivity"  # Productivity gains from AI
    EMPLOYMENT = "employment"  # Employment impacts
    COST_SAVINGS = "cost_savings"  # Cost reductions from AI
    REVENUE_IMPACT = "revenue_impact"  # Revenue changes from AI
    MARKET_SIZE = "market_size"  # Total AI market size


class Unit(Enum):
    """
    What units are we measuring in?
    Like knowing if we're talking millions or billions.
    """
    PERCENTAGE = "percentage"
    BILLIONS_USD = "billions_usd"
    MILLIONS_USD = "millions_usd"
    INDEX = "index"  # Like CPI, base year = 100
    COUNT = "count"  # Number of companies, jobs, etc.
    RATIO = "ratio"  # Like productivity per worker


@dataclass
class AIAdoptionMetric:
    """
    A single data point about AI adoption.
    This is like one row in your economic data spreadsheet.
    
    Example: "In 2024, 75% of tech companies adopted AI" would be:
    - year: 2024
    - value: 75.0
    - metric_type: MetricType.ADOPTION_RATE
    - unit: Unit.PERCENTAGE
    - sector: "Technology"
    """
    # Required fields (must always have these)
    year: int
    value: float
    metric_type: str  # Will validate against MetricType enum
    unit: str  # Will validate against Unit enum
    
    # Optional fields (might not always have these)
    sector: Optional[str] = None  # e.g., "Healthcare", "Finance"
    region: Optional[str] = None  # e.g., "North America", "Europe"
    source: Optional[DataSource] = None
    confidence: float = 1.0  # How confident are we in this data? 0-1
    
    # Metadata (automatically set)
    extracted_date: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None  # Any important caveats about the data


@dataclass
class EconomicImpact:
    """
    Broader economic impact assessment.
    This captures cause-and-effect relationships.
    
    Example: "AI adoption led to 15% productivity increase in manufacturing"
    """
    # What happened?
    impact_type: str  # "productivity_gain", "job_displacement", etc.
    magnitude: float  # Size of the impact
    unit: str
    
    # Where and when?
    year: int
    sector: Optional[str] = None
    region: Optional[str] = None
    
    # Supporting evidence
    confidence: float = 1.0
    methodology: Optional[str] = None  # How was this measured?
    source: Optional[DataSource] = None


def validate_metric(metric: AIAdoptionMetric) -> List[str]:
    """
    Check if the data makes sense.
    Like checking if unemployment rate is between 0-100%.
    
    Returns a list of error messages (empty list = valid)
    """
    errors = []
    
    # Check year is reasonable
    if metric.year < 2000 or metric.year > 2030:
        errors.append(f"Year {metric.year} seems unrealistic for AI adoption data")
    
    # Check percentage values are in valid range
    if metric.metric_type == "adoption_rate" and metric.unit == "percentage":
        if metric.value < 0 or metric.value > 100:
            errors.append(f"Adoption rate {metric.value}% is out of range (0-100)")
    
    # Check confidence is valid
    if metric.confidence < 0 or metric.confidence > 1:
        errors.append(f"Confidence {metric.confidence} must be between 0 and 1")
    
    # Validate metric_type is a valid enum value
    valid_metric_types = [mt.value for mt in MetricType]
    if metric.metric_type not in valid_metric_types:
        errors.append(f"Invalid metric_type: {metric.metric_type}")
    
    # Validate unit is a valid enum value
    valid_units = [u.value for u in Unit]
    if metric.unit not in valid_units:
        errors.append(f"Invalid unit: {metric.unit}")
    
    return errors


def create_sample_data() -> List[AIAdoptionMetric]:
    """
    Create some example data for testing.
    This is like having sample economic data to test your models.
    """
    return [
        AIAdoptionMetric(
            year=2023,
            value=45.5,
            metric_type=MetricType.ADOPTION_RATE.value,
            unit=Unit.PERCENTAGE.value,
            sector="Technology",
            region="North America",
            source=DataSource.STANFORD_HAI,
            notes="Based on survey of Fortune 500 companies"
        ),
        AIAdoptionMetric(
            year=2024,
            value=127.8,
            metric_type=MetricType.INVESTMENT.value,
            unit=Unit.BILLIONS_USD.value,
            region="Global",
            source=DataSource.MCKINSEY,
            confidence=0.85
        ),
        AIAdoptionMetric(
            year=2023,
            value=15.2,
            metric_type=MetricType.PRODUCTIVITY.value,
            unit=Unit.PERCENTAGE.value,
            sector="Manufacturing",
            source=DataSource.OECD,
            notes="Productivity gains from AI implementation"
        )
    ]