"""
Test script to verify ICT, meaningful zero, and citation protections
"""

from metric_validator import MetricValidator

def test_protections():
    validator = MetricValidator()
    
    print("Testing ICT Protection...")
    print("-" * 50)
    
    # Test ICT detection
    ict_contexts = [
        "The ICT sector showed 25% growth",
        "Information and communication technology adoption",
        "Telecom companies invested heavily",
        "Digital infrastructure spending increased",
        "The ict industry is expanding rapidly"
    ]
    
    for context in ict_contexts:
        result = validator.is_ict_data(context)
        print(f"ICT detected: {result} - '{context}'")
    
    print("\n\nTesting Meaningful Zero Detection...")
    print("-" * 50)
    
    # Test meaningful zeros
    zero_contexts = [
        "Survey found 0% productivity gains",
        "Study showed no change in employment",
        "Research indicates zero growth",
        "Companies reported no increase",
        "Analysis found 0% adoption rate",
        "Just 0 companies adopted"  # This should NOT be meaningful
    ]
    
    for context in zero_contexts:
        result = validator.is_meaningful_zero(0, context)
        print(f"Meaningful zero: {result} - '{context}'")
    
    print("\n\nTesting Citation Year Detection...")
    print("-" * 50)
    
    # Test citation detection
    citation_tests = [
        (2024, 2024, "According to Smith (2024), AI adoption is growing"),
        (2023, 2023, "Recent study (Smith et al. 2023) shows"),
        (2022, 2022, "Based on the 2022 article by Johnson"),
        (25, 2024, "Companies showed 25% growth"),  # Not a citation
        (2024, 2024, "In 2024, investment reached new highs")  # Tricky - could be either
    ]
    
    for value, year, context in citation_tests:
        result = validator.detect_citation_year(value, year, context)
        print(f"Citation detected: {result} - value={value}, year={year}, '{context}'")
    
    print("\n\nTesting Cross-Metric Validation...")
    print("-" * 50)
    
    # Test employment with financial units
    issues = validator.apply_cross_metric_rules(
        metric_type="employment_metric",
        value=1000,
        unit="millions_usd",
        year=2024,
        context="Employment increased"
    )
    print(f"Employment with financial units: {len(issues)} issues - {issues[0]['reason'] if issues else 'None'}")
    
    # Test zero employment with specific numbers
    issues = validator.apply_cross_metric_rules(
        metric_type="employment_metric",
        value=0,
        unit="number",
        year=2024,
        context="Company has over 5000 employees"
    )
    print(f"Zero employment with 5000 in context: {len(issues)} issues - {issues[0]['reason'] if issues else 'None'}")

if __name__ == "__main__":
    test_protections()