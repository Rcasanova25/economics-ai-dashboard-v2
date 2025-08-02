"""
Economics AI Dashboard - Comprehensive Sector and Metric Schema
Version: 2.1 FINAL
Date: January 24, 2025

This schema defines all sectors, metric types, and validation rules
for the new extraction system. It serves as the single source of truth
for data validation and classification.

Changes in v2.1:
- Added energy_consumption to ICT and Manufacturing metrics_focus
- All previous v2.0 changes included
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass


class SectorType(Enum):
    """All economic sectors we track for AI adoption analysis"""
    MANUFACTURING = "manufacturing"
    ICT = "information_communication_technology"
    FINANCIAL = "financial_services"
    HEALTHCARE = "healthcare"
    RETAIL = "retail_ecommerce"
    EDUCATION = "education"
    GOVERNMENT = "government_public"
    ENERGY = "energy_utilities"
    TRANSPORTATION = "transportation_logistics"
    AGRICULTURE = "agriculture"
    REAL_ESTATE = "real_estate_construction"
    ENTERTAINMENT = "entertainment_media"
    PROFESSIONAL = "professional_services"
    HOSPITALITY = "hospitality_tourism"
    CROSS_SECTOR = "cross_sector"  # For economy-wide metrics
    UNKNOWN = "unknown"


class MetricCategory(Enum):
    """High-level categories of metrics"""
    ADOPTION = "adoption"
    INVESTMENT = "investment"
    PRODUCTIVITY = "productivity"
    EMPLOYMENT = "employment"  # Includes both job creation and displacement
    COST = "cost"
    REVENUE = "revenue"
    INNOVATION = "innovation"
    INFRASTRUCTURE = "infrastructure"
    SENTIMENT = "sentiment"
    REGULATION = "regulation"
    ENERGY_CONSUMPTION = "energy_consumption"  # Critical for AI sustainability


@dataclass
class MetricDefinition:
    """Defines a specific metric type with validation rules"""
    name: str
    category: MetricCategory
    description: str
    valid_units: List[str]
    value_range: Tuple[float, float]
    required_context: List[str]  # Keywords that should appear in context
    excluded_context: List[str]  # Keywords that indicate wrong classification
    zero_valid: bool = True
    negative_valid: bool = False


# COMPREHENSIVE SECTOR SCHEMA
SECTOR_SCHEMA = {
    SectorType.MANUFACTURING: {
        "keywords": [
            "manufacturing", "factory", "production", "assembly", "industrial",
            "automotive", "aerospace", "machinery", "fabrication", "plant",
            "supply chain", "lean", "quality control", "oem", "production line",
            "assembly line", "industrial automation", "smart factory"
        ],
        "example_entities": [
            "general motors", "ford", "toyota", "boeing", "airbus", "3m",
            "caterpillar", "general electric", "siemens", "honeywell"
        ],
        "patterns": [
            r"\b(?:auto|aero|industrial)[\s-]?(?:manufact|product)",
            r"\bfactor(?:y|ies)\b",
            r"\bassembly[\s-]?line",
            r"\bproduction[\s-]?facilit",
            r"\bmanufacturing[\s-]?(?:company|firm|sector)"
        ],
        "metrics_focus": [
            MetricCategory.PRODUCTIVITY,
            MetricCategory.EMPLOYMENT,
            MetricCategory.COST,
            MetricCategory.INNOVATION,
            MetricCategory.ENERGY_CONSUMPTION  # Added v2.1
        ]
    },
    
    SectorType.ICT: {
        "keywords": [
            "ict", "information technology", "communication technology",
            "telecommunications", "telecom", "software", "hardware",
            "digital infrastructure", "cloud", "data center", "networking",
            "cybersecurity", "it services", "tech", "silicon valley",
            "saas", "paas", "iaas", "digital transformation"
        ],
        "example_entities": [
            "microsoft", "google", "amazon", "apple", "ibm", "cisco",
            "oracle", "salesforce", "at&t", "verizon", "meta", "nvidia"
        ],
        "patterns": [
            r"\b(?:information|info)[\s-]?(?:and|&)?[\s-]?communication",
            r"\bict\b",
            r"\btelecom(?:munication)?s?\b",
            r"\bdigital[\s-]?infrastruct",
            r"\b(?:cloud|saas|paas|iaas)\b",
            r"\b(?:tech|technology)[\s-]?(?:company|firm|sector)"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.INVESTMENT,
            MetricCategory.INFRASTRUCTURE,
            MetricCategory.INNOVATION,
            MetricCategory.COST,
            MetricCategory.EMPLOYMENT,
            MetricCategory.ENERGY_CONSUMPTION  # Added v2.1
        ]
    },
    
    SectorType.FINANCIAL: {
        "keywords": [
            "financial", "banking", "insurance", "investment", "fintech",
            "capital markets", "asset management", "wealth", "trading",
            "payments", "lending", "credit", "mortgage", "derivatives",
            "six sigma", "risk management", "compliance", "portfolio"
        ],
        "example_entities": [
            "jpmorgan", "bank of america", "wells fargo", "goldman sachs",
            "morgan stanley", "citi", "blackrock", "visa", "mastercard",
            "paypal", "square", "stripe", "fidelity", "charles schwab"
        ],
        "patterns": [
            r"\bfinanc(?:e|ial)[\s-]?(?:service|institution)",
            r"\bbank(?:ing|s)?\b",
            r"\bfin[\s-]?tech\b",
            r"\basset[\s-]?manag",
            r"\bcapital[\s-]?market",
            r"\bsix[\s-]?sigma\b"
        ],
        "metrics_focus": [
            MetricCategory.INVESTMENT,
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.REGULATION
        ]
    },
    
    SectorType.HEALTHCARE: {
        "keywords": [
            "healthcare", "medical", "hospital", "clinical", "pharmaceutical",
            "biotech", "patient", "diagnosis", "treatment", "drug discovery",
            "telemedicine", "health tech", "medical devices", "therapy",
            "ehr", "electronic health records", "clinical trials"
        ],
        "example_entities": [
            "johnson & johnson", "pfizer", "unitedhealth", "cvs health",
            "anthem", "merck", "abbvie", "mayo clinic", "cleveland clinic",
            "kaiser permanente", "hca healthcare", "moderna"
        ],
        "patterns": [
            r"\bhealth[\s-]?care\b",
            r"\bmedic(?:al|ine)\b",
            r"\bhospital(?:s)?\b",
            r"\bpharma(?:ceutical)?\b",
            r"\bclinic(?:al|s)?\b",
            r"\b(?:health|medical)[\s-]?(?:company|provider|system)"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.INNOVATION,
            MetricCategory.EMPLOYMENT
        ]
    },
    
    SectorType.RETAIL: {
        "keywords": [
            "retail", "e-commerce", "shopping", "consumer", "store",
            "merchandise", "inventory", "point of sale", "omnichannel",
            "marketplace", "fulfillment", "customer experience",
            "supply chain", "distribution", "wholesale"
        ],
        "example_entities": [
            "walmart", "amazon", "target", "costco", "home depot",
            "cvs", "walgreens", "best buy", "lowes", "kroger",
            "alibaba", "ebay", "shopify", "etsy"
        ],
        "patterns": [
            r"\bretail(?:er|ing)?\b",
            r"\be[\s-]?commerce\b",
            r"\bonline[\s-]?(?:shop|store)",
            r"\bconsumer[\s-]?goods\b",
            r"\bmerchandi[sz]",
            r"\b(?:retail|commerce)[\s-]?(?:company|chain|sector)"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.REVENUE,
            MetricCategory.COST,
            MetricCategory.EMPLOYMENT,
            MetricCategory.INVESTMENT
        ]
    },
    
    SectorType.EDUCATION: {
        "keywords": [
            "education", "academic", "university", "college", "school",
            "learning", "training", "student", "curriculum", "edtech",
            "online learning", "mooc", "educational technology"
        ],
        "example_entities": [
            "harvard", "stanford", "mit", "oxford", "cambridge",
            "pearson", "mcgraw-hill", "coursera", "khan academy",
            "blackboard", "canvas", "chegg", "udemy"
        ],
        "patterns": [
            r"\beducat(?:ion|ional)\b",
            r"\bacademic(?:s)?\b",
            r"\buniversit(?:y|ies)\b",
            r"\b(?:online|distance)[\s-]?learn",
            r"\bed[\s-]?tech\b"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.EMPLOYMENT
        ]
    },
    
    SectorType.GOVERNMENT: {
        "keywords": [
            "government", "public sector", "federal", "state", "municipal",
            "agency", "department", "administration", "policy", "regulation",
            "public service", "civic", "bureaucracy", "e-government",
            "smart city", "digital government", "public administration"
        ],
        "example_entities": [
            "department of", "ministry of", "federal", "state of",
            "city of", "county", "municipality", "agency",
            "administration", "bureau", "commission"
        ],
        "patterns": [
            r"\bgovernment(?:al)?\b",
            r"\bpublic[\s-]?sector\b",
            r"\bfederal[\s-]?(?:agency|department)",
            r"\bmunicipa(?:l|lity)\b",
            r"\be[\s-]?gov(?:ernment)?\b",
            r"\b(?:state|local|federal)[\s-]?government"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.REGULATION,
            MetricCategory.INVESTMENT,
            MetricCategory.EMPLOYMENT,
            MetricCategory.ENERGY_CONSUMPTION
        ]
    },
    
    SectorType.ENERGY: {
        "keywords": [
            "energy", "utilities", "power", "electricity", "renewable",
            "oil", "gas", "solar", "wind", "nuclear", "grid",
            "generation", "transmission", "distribution"
        ],
        "example_entities": [
            "exxonmobil", "chevron", "shell", "bp", "total",
            "duke energy", "nextera", "southern company", "pge",
            "engie", "enel", "iberdrola", "orsted"
        ],
        "patterns": [
            r"\benergy[\s-]?(?:sector|company|utility)",
            r"\b(?:electric|power)[\s-]?(?:utility|company)",
            r"\brenewable(?:s)?\b",
            r"\boil[\s-]?(?:and|&)[\s-]?gas\b",
            r"\b(?:solar|wind)[\s-]?(?:power|energy)"
        ],
        "metrics_focus": [
            MetricCategory.INVESTMENT,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.INFRASTRUCTURE,
            MetricCategory.COST
        ]
    },
    
    SectorType.TRANSPORTATION: {
        "keywords": [
            "transportation", "logistics", "shipping", "freight", "airline",
            "railway", "trucking", "delivery", "supply chain", "fleet",
            "autonomous vehicles", "mobility", "transit"
        ],
        "example_entities": [
            "ups", "fedex", "dhl", "maersk", "delta", "united airlines",
            "american airlines", "uber", "lyft", "union pacific",
            "csx", "norfolk southern", "jb hunt"
        ],
        "patterns": [
            r"\btransport(?:ation)?\b",
            r"\blogistic(?:s)?\b",
            r"\b(?:air|rail|truck|ship)[\s-]?(?:line|ing)",
            r"\bfreight[\s-]?(?:forward|carrier)",
            r"\bautonomous[\s-]?vehicle"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.EMPLOYMENT
        ]
    },
    
    SectorType.AGRICULTURE: {
        "keywords": [
            "agriculture", "farming", "crop", "livestock", "agtech",
            "precision agriculture", "farm", "harvest", "irrigation",
            "agricultural", "agribusiness", "food production"
        ],
        "example_entities": [
            "john deere", "monsanto", "cargill", "archer daniels midland",
            "bayer crop science", "syngenta", "corteva"
        ],
        "patterns": [
            r"\bagri(?:culture|cultural|business)\b",
            r"\bfarm(?:ing|er|s)?\b",
            r"\bcrop(?:s)?\b",
            r"\blivestock\b",
            r"\bag[\s-]?tech\b"
        ],
        "metrics_focus": [
            MetricCategory.PRODUCTIVITY,
            MetricCategory.COST,
            MetricCategory.ADOPTION,
            MetricCategory.INNOVATION
        ]
    },
    
    SectorType.REAL_ESTATE: {
        "keywords": [
            "real estate", "property", "construction", "housing",
            "commercial real estate", "residential", "realty",
            "property management", "development", "building"
        ],
        "example_entities": [
            "cbre", "jll", "cushman & wakefield", "remax", "keller williams",
            "brookfield", "prologis", "simon property group"
        ],
        "patterns": [
            r"\breal[\s-]?estate\b",
            r"\bpropert(?:y|ies)\b",
            r"\bconstruction\b",
            r"\b(?:commercial|residential)[\s-]?(?:property|real estate)"
        ],
        "metrics_focus": [
            MetricCategory.COST,
            MetricCategory.PRODUCTIVITY,
            MetricCategory.ADOPTION,
            MetricCategory.INVESTMENT
        ]
    },
    
    SectorType.ENTERTAINMENT: {
        "keywords": [
            "entertainment", "media", "streaming", "gaming", "content",
            "broadcast", "film", "music", "social media", "digital media"
        ],
        "example_entities": [
            "disney", "netflix", "warner bros", "comcast", "spotify",
            "activision", "electronic arts", "tiktok", "youtube"
        ],
        "patterns": [
            r"\bentertainment\b",
            r"\bmedia[\s-]?(?:company|content)",
            r"\bstream(?:ing)?\b",
            r"\bgam(?:e|ing)\b",
            r"\b(?:film|movie|music)[\s-]?(?:industry|production)"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.REVENUE,
            MetricCategory.INNOVATION,
            MetricCategory.COST
        ]
    },
    
    SectorType.PROFESSIONAL: {
        "keywords": [
            "professional services", "consulting", "legal", "accounting",
            "audit", "advisory", "law firm", "management consulting"
        ],
        "example_entities": [
            "deloitte", "pwc", "ey", "kpmg", "mckinsey", "bain",
            "boston consulting group", "accenture"
        ],
        "patterns": [
            r"\bprofessional[\s-]?service",
            r"\bconsult(?:ing|ant)",
            r"\b(?:law|legal)[\s-]?firm",
            r"\baccounting\b",
            r"\bauditor?\b"
        ],
        "metrics_focus": [
            MetricCategory.PRODUCTIVITY,
            MetricCategory.COST,
            MetricCategory.ADOPTION,
            MetricCategory.EMPLOYMENT
        ]
    },
    
    SectorType.HOSPITALITY: {
        "keywords": [
            "hospitality", "hotel", "tourism", "restaurant", "travel",
            "accommodation", "resort", "cruise", "airline", "dining"
        ],
        "example_entities": [
            "marriott", "hilton", "hyatt", "airbnb", "booking.com",
            "expedia", "tripadvisor", "carnival", "royal caribbean"
        ],
        "patterns": [
            r"\bhospitality\b",
            r"\bhotel(?:s|ier)?\b",
            r"\btourism\b",
            r"\brestaurant(?:s)?\b",
            r"\btravel[\s-]?(?:industry|sector)"
        ],
        "metrics_focus": [
            MetricCategory.ADOPTION,
            MetricCategory.COST,
            MetricCategory.REVENUE,
            MetricCategory.EMPLOYMENT
        ]
    }
}


# COMPREHENSIVE METRIC DEFINITIONS
METRIC_DEFINITIONS = {
    # ADOPTION METRICS
    "ai_adoption_rate": MetricDefinition(
        name="AI Adoption Rate",
        category=MetricCategory.ADOPTION,
        description="Percentage of companies/organizations using AI",
        valid_units=["percentage", "percent"],
        value_range=(0, 100),
        required_context=["adopt", "using", "implement", "deploy", "utiliz"],
        excluded_context=["considering", "planning", "might", "could"],
        zero_valid=True
    ),
    
    "ai_implementation_count": MetricDefinition(
        name="AI Implementation Count",
        category=MetricCategory.ADOPTION,
        description="Number of AI systems/solutions implemented",
        valid_units=["number", "count"],
        value_range=(0, 10000),
        required_context=["implement", "deploy", "system", "solution", "application"],
        excluded_context=["potential", "planned", "proposed"],
        zero_valid=True
    ),
    
    # INVESTMENT METRICS
    "ai_investment_amount": MetricDefinition(
        name="AI Investment Amount",
        category=MetricCategory.INVESTMENT,
        description="Financial investment in AI initiatives",
        valid_units=["millions_usd", "billions_usd", "dollars"],
        value_range=(0, 1000000),
        required_context=["invest", "spending", "budget", "capital", "funding"],
        excluded_context=["return", "roi", "revenue"],
        zero_valid=True
    ),
    
    "ai_budget_percentage": MetricDefinition(
        name="AI Budget Percentage",
        category=MetricCategory.INVESTMENT,
        description="Percentage of IT/total budget allocated to AI",
        valid_units=["percentage", "percent"],
        value_range=(0, 100),
        required_context=["budget", "allocation", "spending", "investment"],
        excluded_context=["growth", "increase", "decrease"],
        zero_valid=True
    ),
    
    # PRODUCTIVITY METRICS
    "productivity_improvement": MetricDefinition(
        name="Productivity Improvement",
        category=MetricCategory.PRODUCTIVITY,
        description="Productivity gains from AI adoption",
        valid_units=["percentage", "percent"],
        value_range=(-50, 500),
        required_context=["productiv", "efficiency", "output", "performance"],
        excluded_context=["cost", "price", "revenue"],
        zero_valid=True,
        negative_valid=True
    ),
    
    "time_savings": MetricDefinition(
        name="Time Savings",
        category=MetricCategory.PRODUCTIVITY,
        description="Hours or percentage time saved through AI",
        valid_units=["hours", "percentage", "percent"],
        value_range=(0, 10000),
        required_context=["time", "hours", "saved", "reduction", "faster"],
        excluded_context=["cost", "money", "dollar"],
        zero_valid=True
    ),
    
    # EMPLOYMENT METRICS - Separated creation and displacement
    "job_creation": MetricDefinition(
        name="Job Creation",
        category=MetricCategory.EMPLOYMENT,
        description="Number or percentage of jobs created by AI",
        valid_units=["number", "count", "percentage", "percent"],
        value_range=(0, 1000000),
        required_context=["job", "creat", "new position", "hiring", "employment growth"],
        excluded_context=["loss", "displace", "eliminat", "replac"],
        zero_valid=True
    ),
    
    "job_displacement": MetricDefinition(
        name="Job Displacement",
        category=MetricCategory.EMPLOYMENT,
        description="Number or percentage of jobs displaced by AI",
        valid_units=["number", "count", "percentage", "percent"],
        value_range=(0, 1000000),
        required_context=["job", "displace", "replace", "eliminat", "automat"],
        excluded_context=["creat", "new", "hiring", "growth"],
        zero_valid=True
    ),
    
    "net_employment_change": MetricDefinition(
        name="Net Employment Change",
        category=MetricCategory.EMPLOYMENT,
        description="Net change in employment (can be positive or negative)",
        valid_units=["number", "count", "percentage", "percent"],
        value_range=(-1000000, 1000000),
        required_context=["employment", "job", "workforce", "net", "overall"],
        excluded_context=["revenue", "cost", "investment"],
        zero_valid=True,
        negative_valid=True
    ),
    
    "workforce_augmentation": MetricDefinition(
        name="Workforce Augmentation",
        category=MetricCategory.EMPLOYMENT,
        description="Number of workers augmented by AI tools",
        valid_units=["number", "count", "percentage", "percent"],
        value_range=(0, 1000000),
        required_context=["worker", "employee", "augment", "assist", "support"],
        excluded_context=["replace", "displace", "eliminate"],
        zero_valid=True
    ),
    
    # COST METRICS
    "cost_reduction": MetricDefinition(
        name="Cost Reduction",
        category=MetricCategory.COST,
        description="Cost savings from AI implementation",
        valid_units=["millions_usd", "billions_usd", "percentage", "percent"],
        value_range=(-1000, 10000),
        required_context=["cost", "saving", "reduction", "expense", "efficient"],
        excluded_context=["revenue", "profit", "income"],
        zero_valid=True,
        negative_valid=True
    ),
    
    "operational_cost": MetricDefinition(
        name="Operational Cost",
        category=MetricCategory.COST,
        description="Cost of running AI systems",
        valid_units=["millions_usd", "billions_usd", "dollars"],
        value_range=(0, 100000),
        required_context=["operational", "running", "maintenance", "cost"],
        excluded_context=["investment", "capital", "revenue"],
        zero_valid=True
    ),
    
    # REVENUE METRICS
    "revenue_increase": MetricDefinition(
        name="Revenue Increase",
        category=MetricCategory.REVENUE,
        description="Revenue gains from AI adoption",
        valid_units=["millions_usd", "billions_usd", "percentage", "percent"],
        value_range=(-100, 1000),
        required_context=["revenue", "income", "sales", "profit", "earnings"],
        excluded_context=["cost", "expense", "investment"],
        zero_valid=True,
        negative_valid=True
    ),
    
    # ENERGY CONSUMPTION METRICS
    "ai_energy_consumption": MetricDefinition(
        name="AI Energy Consumption",
        category=MetricCategory.ENERGY_CONSUMPTION,
        description="Energy consumed by AI systems and infrastructure",
        valid_units=["mwh", "gwh", "twh", "megawatts", "gigawatts"],
        value_range=(0, 100000),
        required_context=["energy", "power", "consumption", "electricity", "usage"],
        excluded_context=["cost", "price", "revenue"],
        zero_valid=True
    ),
    
    "ai_carbon_footprint": MetricDefinition(
        name="AI Carbon Footprint",
        category=MetricCategory.ENERGY_CONSUMPTION,
        description="CO2 emissions from AI operations",
        valid_units=["tons_co2", "mt_co2", "kg_co2"],
        value_range=(0, 1000000),
        required_context=["carbon", "co2", "emission", "footprint", "greenhouse"],
        excluded_context=["reduction", "savings", "offset"],
        zero_valid=True
    ),
    
    "energy_efficiency_improvement": MetricDefinition(
        name="Energy Efficiency Improvement",
        category=MetricCategory.ENERGY_CONSUMPTION,
        description="Improvement in AI energy efficiency",
        valid_units=["percentage", "percent"],
        value_range=(-50, 200),
        required_context=["efficiency", "energy", "improvement", "optimization"],
        excluded_context=["cost", "revenue", "profit"],
        zero_valid=True,
        negative_valid=True
    ),
    
    # INNOVATION METRICS
    "ai_patents_filed": MetricDefinition(
        name="AI Patents Filed",
        category=MetricCategory.INNOVATION,
        description="Number of AI-related patents filed",
        valid_units=["number", "count"],
        value_range=(0, 10000),
        required_context=["patent", "intellectual property", "ip", "filing"],
        excluded_context=["cost", "revenue", "employment"],
        zero_valid=True
    ),
    
    "rd_investment": MetricDefinition(
        name="R&D Investment",
        category=MetricCategory.INNOVATION,
        description="Research and development spending on AI",
        valid_units=["millions_usd", "billions_usd", "percentage"],
        value_range=(0, 100000),
        required_context=["research", "development", "r&d", "innovation"],
        excluded_context=["operational", "maintenance", "revenue"],
        zero_valid=True
    ),
    
    # INFRASTRUCTURE METRICS
    "ai_infrastructure_investment": MetricDefinition(
        name="AI Infrastructure Investment",
        category=MetricCategory.INFRASTRUCTURE,
        description="Investment in AI computing infrastructure",
        valid_units=["millions_usd", "billions_usd"],
        value_range=(0, 100000),
        required_context=["infrastructure", "data center", "compute", "gpu", "server"],
        excluded_context=["operational", "revenue", "employment"],
        zero_valid=True
    )
}


# Helper functions remain the same
def classify_sector(text: str, known_company: Optional[str] = None) -> Tuple[SectorType, float]:
    """
    Classify text into a sector with confidence score.
    
    Args:
        text: Text to classify
        known_company: Optional company name for better classification
        
    Returns:
        Tuple of (SectorType, confidence_score)
    """
    text_lower = text.lower()
    scores = {}
    
    for sector, schema in SECTOR_SCHEMA.items():
        score = 0.0
        
        # Check keywords (weight: 0.4)
        keyword_matches = sum(1 for kw in schema["keywords"] if kw in text_lower)
        score += (keyword_matches / len(schema["keywords"])) * 0.4
        
        # Check example entities (weight: 0.2) - not exclusive
        example_matches = sum(1 for entity in schema["example_entities"] if entity in text_lower)
        if example_matches > 0:
            score += 0.2
        
        # If a known company is provided, boost score for likely sector
        if known_company and known_company.lower() in text_lower:
            score += 0.1  # Boost for having company context
        
        # Check patterns (weight: 0.3)
        import re
        pattern_matches = sum(1 for pattern in schema["patterns"] 
                            if re.search(pattern, text_lower, re.IGNORECASE))
        if pattern_matches > 0:
            score += (pattern_matches / len(schema["patterns"])) * 0.3
        
        scores[sector] = score
    
    # Get best match
    if scores:
        best_sector = max(scores, key=scores.get)
        confidence = scores[best_sector]
        
        # If confidence is too low, return UNKNOWN
        if confidence < 0.1:
            return (SectorType.UNKNOWN, 0.0)
        
        return (best_sector, confidence)
    
    return (SectorType.UNKNOWN, 0.0)


def validate_metric(value: float, unit: str, metric_type: str, 
                   sector: SectorType, context: str) -> Dict[str, any]:
    """
    Validate a metric against schema rules.
    
    Returns:
        Dict with 'valid' (bool), 'confidence' (float), and 'issues' (list)
    """
    result = {
        "valid": True,
        "confidence": 1.0,
        "issues": []
    }
    
    # Check if metric type exists
    if metric_type not in METRIC_DEFINITIONS:
        result["valid"] = False
        result["issues"].append(f"Unknown metric type: {metric_type}")
        return result
    
    metric_def = METRIC_DEFINITIONS[metric_type]
    
    # Validate unit
    if unit not in metric_def.valid_units:
        result["valid"] = False
        result["confidence"] *= 0.5
        result["issues"].append(f"Invalid unit '{unit}' for {metric_type}")
    
    # Validate range
    min_val, max_val = metric_def.value_range
    if not (min_val <= value <= max_val):
        result["confidence"] *= 0.7
        result["issues"].append(f"Value {value} outside typical range [{min_val}, {max_val}]")
    
    # Context validation
    context_lower = context.lower()
    
    # Check required context
    if metric_def.required_context:
        found_required = any(keyword in context_lower for keyword in metric_def.required_context)
        if not found_required:
            result["confidence"] *= 0.8
            result["issues"].append("Missing required context keywords")
    
    # Check excluded context
    if metric_def.excluded_context:
        found_excluded = any(keyword in context_lower for keyword in metric_def.excluded_context)
        if found_excluded:
            result["confidence"] *= 0.6
            result["issues"].append("Context contains excluded keywords")
    
    return result