"""
Economic Metrics Validation Schema
Based on top 5 priority metrics for the Economics AI Dashboard
"""

METRIC_VALIDATION_SCHEMA = {
    # 1. ADOPTION RATE - Most important metric
    "adoption_metric": {
        "valid_units": ["percentage", "count", "number"],
        "invalid_units": ["millions_usd", "billions_usd", "dollars", "co2_emissions", "energy_unit"],
        "value_ranges": {
            "percentage": (0, 100),  # Adoption can't exceed 100%
            "count": (0, 1_000_000),  # Reasonable number of adopters
            "number": (0, 1_000_000)
        },
        "zero_value_valid": True,  # 0% adoption is valid (non-adopters)
        "patterns_required": ["adopt", "implement", "deploy", "using", "utiliz", "rollout", "integration"],
        "patterns_exclude": ["cost of adoption", "adoption cost"],  # These are costs, not adoption rates
        "common_errors": [
            "Citation years (2020, 2021, etc.) extracted as adoption counts",
            "Percentage values over 100",
            "Financial units mixed with adoption rates"
        ]
    },
    
    # 2. INVESTMENTS - Financial commitments to AI
    "investment_metric": {
        "valid_units": ["millions_usd", "billions_usd", "dollars", "percentage"],
        "invalid_units": ["number", "count", "co2_emissions", "energy_unit"],
        "value_ranges": {
            "millions_usd": (0, 100_000),  # Up to $100B in millions
            "billions_usd": (0, 1_000),    # Up to $1T
            "dollars": (0, 1_000_000_000_000),  # Up to $1T
            "percentage": (0, 100)  # % of budget/revenue
        },
        "zero_value_valid": True,  # Some may have 0 investment
        "patterns_required": ["invest", "funding", "capital", "budget", "spending", "expenditure", "allocation"],
        "patterns_exclude": ["return on investment", "roi"],  # ROI is a different metric
        "common_errors": [
            "Employee counts misclassified as investment amounts",
            "Years (2020-2030) extracted as dollar amounts"
        ]
    },
    
    # 3. PRODUCTIVITY - Output and efficiency gains
    "productivity_metric": {
        "valid_units": ["percentage", "ratio", "index", "hours", "number"],
        "invalid_units": ["millions_usd", "billions_usd", "co2_emissions"],
        "value_ranges": {
            "percentage": (-50, 500),  # Productivity can increase significantly
            "ratio": (0, 10),         # Productivity ratios
            "hours": (-10_000, 10_000),  # Hours saved/lost
            "number": (0, 1_000_000)  # Generic productivity measures
        },
        "zero_value_valid": True,  # No change in productivity
        "patterns_required": ["productiv", "efficiency", "output", "performance", "throughput", "yield"],  # productiv catches all forms
        "patterns_exclude": ["cost", "price", "expense"],
        "common_errors": [
            "Financial values misclassified as productivity",
            "Negative productivity gains not properly signed"
        ]
    },
    
    # 4. LABOR - Employment and workforce metrics
    "employment_metric": {
        "valid_units": ["number", "count", "percentage", "fte"],  # FTE = Full Time Equivalent
        "invalid_units": ["millions_usd", "billions_usd", "dollars", "co2_emissions"],
        "value_ranges": {
            "number": (0, 10_000_000),  # Reasonable employment figures
            "count": (0, 10_000_000),
            "percentage": (-100, 200),  # Can have job losses or growth
            "fte": (0, 10_000_000)
        },
        "zero_value_valid": False,  # 0 employees is suspicious unless it's a change metric
        "patterns_required": ["employ", "worker", "job", "labor", "workforce", "staff", "personnel", "fte"],
        "patterns_exclude": ["cost", "expense", "salary", "wage"],  # These are cost metrics
        "common_errors": [
            "Salary/wage amounts classified as employee counts",
            "Years misclassified as employee numbers",
            "Financial units (millions_usd) used for headcount"
        ]
    },
    
    # 5. COSTS - Expenses and cost savings
    "cost_metric": {
        "valid_units": ["millions_usd", "billions_usd", "dollars", "percentage"],
        "invalid_units": ["number", "count", "co2_emissions", "energy_unit"],
        "value_ranges": {
            "millions_usd": (-10_000, 100_000),  # Can have cost savings (negative)
            "billions_usd": (-1_000, 10_000),
            "dollars": (-1_000_000_000_000, 1_000_000_000_000),
            "percentage": (-100, 1000)  # Cost reduction can be negative, increases can be >100%
        },
        "zero_value_valid": True,  # No cost change is valid
        "patterns_required": ["cost", "expense", "spending", "expenditure", "savings", "budget"],
        "patterns_exclude": ["cost-benefit", "low-cost", "cost-effective"],  # These are descriptive, not metrics
        "common_errors": [
            "Productivity percentages misclassified as cost percentages",
            "Employee counts misclassified as costs",
            "Revenue/profit misclassified as costs"
        ]
    }
}

# Cross-metric validation rules
CROSS_METRIC_RULES = [
    {
        "rule": "Financial units should not appear with employment metrics",
        "condition": lambda metric_type, unit: (
            metric_type in ["employment_metric", "labor_metrics"] and 
            unit in ["millions_usd", "billions_usd", "dollars"]
        ),
        "action": "remove",
        "confidence": 0.95
    },
    {
        "rule": "Citation years should not be metric values",
        "condition": lambda value, year, context: (
            value == year and 
            1900 <= value <= 2030 and
            any(pattern in str(context) for pattern in ["(", ")", "et al", "article", "paper"])
        ),
        "action": "remove",
        "confidence": 0.95
    },
    {
        "rule": "Zero employment with specific numbers in context",
        "condition": lambda value, metric_type, context: (
            value == 0 and
            metric_type in ["employment_metric", "labor_metrics"] and
            any(phrase in str(context).lower() for phrase in ["over", "more than", "employees", "workers"]) and
            any(str(num) in str(context) for num in range(100, 10000))
        ),
        "action": "remove",
        "confidence": 0.90
    }
]

# Reclassification priority when multiple patterns match
RECLASSIFICATION_PRIORITY = [
    "adoption_metric",      # Highest priority - core metric
    "investment_metric",    # Financial commitment
    "cost_metric",         # Other financial
    "productivity_metric", # Performance
    "employment_metric"    # Workforce
]