"""
Test our data models

As a developer, testing is like double-checking your economic calculations.
We want to make sure our data structures work correctly before building on them.
"""
import pytest
from datetime import datetime
from src.models.schema import (
    AIAdoptionMetric, DataSource, MetricType, Unit, 
    validate_metric, create_sample_data, EconomicImpact
)


def test_adoption_metric_creation():
    """Test creating an adoption metric - our basic data point"""
    metric = AIAdoptionMetric(
        year=2024,
        value=75.5,
        metric_type=MetricType.ADOPTION_RATE.value,
        unit=Unit.PERCENTAGE.value,
        sector='Technology',
        source=DataSource.STANFORD_HAI
    )

    # Check all our fields are set correctly
    assert metric.year == 2024
    assert metric.value == 75.5
    assert metric.confidence == 1.0  # default value
    assert metric.sector == 'Technology'
    assert metric.source == DataSource.STANFORD_HAI
    # Check that extracted_date was automatically set
    assert isinstance(metric.extracted_date, datetime)


def test_metric_validation():
    """Test our validation logic - like checking if economic data makes sense"""
    # Valid metric - this should pass all checks
    good_metric = AIAdoptionMetric(
        year=2024,
        value=75.5,
        metric_type=MetricType.ADOPTION_RATE.value,
        unit=Unit.PERCENTAGE.value
    )
    errors = validate_metric(good_metric)
    assert len(errors) == 0, f"Valid metric should have no errors, got: {errors}"

    # Invalid metric - adoption rate over 100%
    bad_metric = AIAdoptionMetric(
        year=2024,
        value=150,
        metric_type=MetricType.ADOPTION_RATE.value,
        unit=Unit.PERCENTAGE.value
    )
    errors = validate_metric(bad_metric)
    assert len(errors) > 0
    assert "out of range" in errors[0]

    # Invalid year - too far in the future
    future_metric = AIAdoptionMetric(
        year=2050,
        value=50,
        metric_type=MetricType.ADOPTION_RATE.value,
        unit=Unit.PERCENTAGE.value
    )
    errors = validate_metric(future_metric)
    assert len(errors) > 0
    assert "unrealistic" in errors[0].lower()


def test_invalid_enum_values():
    """Test that we catch invalid metric types and units"""
    # Invalid metric type
    bad_type_metric = AIAdoptionMetric(
        year=2024,
        value=50,
        metric_type="invalid_type",  # This isn't in our enum
        unit=Unit.PERCENTAGE.value
    )
    errors = validate_metric(bad_type_metric)
    assert any("Invalid metric_type" in error for error in errors)

    # Invalid unit
    bad_unit_metric = AIAdoptionMetric(
        year=2024,
        value=50,
        metric_type=MetricType.ADOPTION_RATE.value,
        unit="invalid_unit"  # This isn't in our enum
    )
    errors = validate_metric(bad_unit_metric)
    assert any("Invalid unit" in error for error in errors)


def test_economic_impact_creation():
    """Test creating an economic impact assessment"""
    impact = EconomicImpact(
        impact_type="productivity_gain",
        magnitude=15.5,
        unit=Unit.PERCENTAGE.value,
        year=2023,
        sector="Manufacturing",
        methodology="Difference-in-differences analysis",
        source=DataSource.OECD
    )
    
    assert impact.magnitude == 15.5
    assert impact.sector == "Manufacturing"
    assert impact.methodology is not None


def test_sample_data_creation():
    """Test that our sample data generator works"""
    samples = create_sample_data()
    
    # Should return a list
    assert isinstance(samples, list)
    assert len(samples) > 0
    
    # Each sample should be valid
    for sample in samples:
        errors = validate_metric(sample)
        assert len(errors) == 0, f"Sample data should be valid, got errors: {errors}"