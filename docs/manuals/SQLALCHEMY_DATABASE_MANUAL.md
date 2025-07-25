# SQLAlchemy Database Manual for Economists
## A Step-by-Step Guide to Managing Economic Data with Databases

**Purpose:** This manual teaches economists how to store, query, and analyze data using SQLAlchemy and SQLite databases. Perfect for managing extracted PDF data, time series, and economic indicators.

---

## Table of Contents
1. [Understanding Databases for Economics](#understanding)
2. [Setting Up SQLAlchemy](#setup)
3. [Creating Your First Database](#first-database)
4. [Defining Data Models](#data-models)
5. [Adding Data (INSERT)](#adding-data)
6. [Querying Data (SELECT)](#querying-data)
7. [Updating Data (UPDATE)](#updating-data)
8. [Deleting Data (DELETE)](#deleting-data)
9. [Advanced Queries for Analysis](#advanced-queries)
10. [Data Cleaning and Validation](#data-cleaning)
11. [Handling Duplicate Data](#duplicates)
12. [Exporting Data](#exporting)
13. [Best Practices](#best-practices)
14. [Complete Working Example](#complete-example)
15. [Common Economic Queries](#economic-queries)
16. [Troubleshooting](#troubleshooting)

---

## 1. Understanding Databases for Economics {#understanding}

### Why Databases Instead of Excel/CSV?

1. **Handle millions of records** without crashing
2. **Query specific data** instantly (e.g., "all GDP data for 2023")
3. **Prevent accidental data loss** with transaction safety
4. **Track relationships** between datasets
5. **Multiple users** can access simultaneously

### Key Concepts

- **Table**: Like an Excel sheet (e.g., "economic_indicators")
- **Row**: One record (e.g., "US GDP 2023: $25.5 trillion")
- **Column**: Data field (e.g., "country", "year", "value")
- **Primary Key**: Unique identifier for each row
- **Query**: Request for specific data

---

## 2. Setting Up SQLAlchemy {#setup}

### Installation

```bash
pip install sqlalchemy>=2.0.30
pip install pandas  # For data manipulation
```

### Basic Imports

```python
# Standard imports for any database project
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import pandas as pd

# Create base class for models
Base = declarative_base()
```

### Understanding the Components

```python
# 1. Engine: Connection to database
engine = create_engine('sqlite:///economic_data.db', echo=True)

# 2. Session: Workspace for database operations
Session = sessionmaker(bind=engine)
session = Session()

# 3. Base: Parent class for all your tables
Base = declarative_base()
```

---

## 3. Creating Your First Database {#first-database}

### Simple Database Creation

```python
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Step 1: Define database location
database_path = "economic_data.db"

# Step 2: Create engine (connection)
engine = create_engine(f'sqlite:///{database_path}', echo=True)
# echo=True shows SQL commands (helpful for learning)

# Step 3: Create base class
Base = declarative_base()

# Step 4: Define a simple table
class EconomicIndicator(Base):
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True)
    country = Column(String(100))
    indicator = Column(String(100))
    year = Column(Integer)
    value = Column(Float)
    unit = Column(String(50))

# Step 5: Create all tables
Base.metadata.create_all(engine)

print("Database created successfully!")
```

### What This Creates

```sql
-- Behind the scenes, SQLAlchemy creates this SQL:
CREATE TABLE indicators (
    id INTEGER PRIMARY KEY,
    country VARCHAR(100),
    indicator VARCHAR(100),
    year INTEGER,
    value FLOAT,
    unit VARCHAR(50)
);
```

---

## 4. Defining Data Models {#data-models}

### Economic Data Model Example

```python
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

class DataSource(Base):
    """Table for PDF/data sources"""
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    organization = Column(String(255))
    url = Column(String(500))
    extraction_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to metrics
    metrics = relationship("EconomicMetric", back_populates="source")

class EconomicMetric(Base):
    """Table for individual economic metrics"""
    __tablename__ = 'economic_metrics'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Foreign key to source
    source_id = Column(Integer, ForeignKey('data_sources.id'))
    
    # Metric data
    indicator_type = Column(String(100), nullable=False)  # 'gdp', 'inflation', etc.
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # 'percentage', 'billions_usd', etc.
    
    # Time and location
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)  # 1-4, optional
    country = Column(String(100))
    region = Column(String(100))
    
    # Metadata
    confidence = Column(Float, default=1.0)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    source = relationship("DataSource", back_populates="metrics")
    
    # Indexes for fast queries
    __table_args__ = (
        Index('idx_indicator_year', 'indicator_type', 'year'),
        Index('idx_country_year', 'country', 'year'),
    )

# Create tables
Base.metadata.create_all(engine)
```

### Understanding Model Components

1. **`__tablename__`**: Name of the table in database
2. **`Column`**: Defines a field and its type
3. **`primary_key=True`**: Unique identifier
4. **`nullable=False`**: Required field
5. **`ForeignKey`**: Links to another table
6. **`relationship`**: Easy access to related data
7. **`Index`**: Makes queries faster

---

## 5. Adding Data (INSERT) {#adding-data}

### Method 1: Adding Single Records

```python
from sqlalchemy.orm import Session

# Create session
session = Session(engine)

# Create new metric
new_metric = EconomicMetric(
    indicator_type='gdp_growth',
    value=2.5,
    unit='percentage',
    year=2024,
    country='United States',
    confidence=0.95,
    notes='Q3 preliminary estimate'
)

# Add to session
session.add(new_metric)

# Commit to database
session.commit()

print(f"Added metric with ID: {new_metric.id}")
```

### Method 2: Adding Multiple Records

```python
# List of metrics to add
metrics_data = [
    {
        'indicator_type': 'inflation',
        'value': 3.2,
        'unit': 'percentage',
        'year': 2024,
        'country': 'United States'
    },
    {
        'indicator_type': 'unemployment',
        'value': 3.9,
        'unit': 'percentage',
        'year': 2024,
        'country': 'United States'
    },
    {
        'indicator_type': 'gdp_nominal',
        'value': 27.36,
        'unit': 'trillions_usd',
        'year': 2024,
        'country': 'United States'
    }
]

# Create metric objects
metrics = [EconomicMetric(**data) for data in metrics_data]

# Add all at once
session.add_all(metrics)
session.commit()

print(f"Added {len(metrics)} metrics")
```

### Method 3: Bulk Insert (Fastest for Large Data)

```python
# For thousands of records
bulk_data = []

# Example: Import from extracted PDF data
for item in extracted_pdf_data:
    bulk_data.append({
        'indicator_type': item['type'],
        'value': float(item['value']),
        'unit': item['unit'],
        'year': int(item['year']),
        'country': item.get('country', 'Global'),
        'confidence': item.get('confidence', 0.8)
    })

# Bulk insert
session.bulk_insert_mappings(EconomicMetric, bulk_data)
session.commit()

print(f"Bulk inserted {len(bulk_data)} records")
```

### Adding with Error Handling

```python
def safe_add_metric(session, metric_data):
    """Add metric with duplicate checking"""
    try:
        # Check if already exists
        existing = session.query(EconomicMetric).filter_by(
            indicator_type=metric_data['indicator_type'],
            year=metric_data['year'],
            country=metric_data.get('country')
        ).first()
        
        if existing:
            print(f"Metric already exists: {metric_data}")
            return existing
        
        # Create and add new metric
        new_metric = EconomicMetric(**metric_data)
        session.add(new_metric)
        session.commit()
        
        return new_metric
        
    except Exception as e:
        session.rollback()
        print(f"Error adding metric: {e}")
        return None
```

---

## 6. Querying Data (SELECT) {#querying-data}

### Basic Queries

```python
# Get all records
all_metrics = session.query(EconomicMetric).all()
print(f"Total metrics: {len(all_metrics)}")

# Get first record
first_metric = session.query(EconomicMetric).first()
print(f"First metric: {first_metric.indicator_type} = {first_metric.value}")

# Get by ID
metric = session.query(EconomicMetric).get(1)  # ID = 1
```

### Filtering Data

```python
# Filter by single condition
gdp_metrics = session.query(EconomicMetric).filter(
    EconomicMetric.indicator_type == 'gdp_growth'
).all()

# Multiple conditions (AND)
us_2024_metrics = session.query(EconomicMetric).filter(
    EconomicMetric.country == 'United States',
    EconomicMetric.year == 2024
).all()

# OR conditions
from sqlalchemy import or_

gdp_or_inflation = session.query(EconomicMetric).filter(
    or_(
        EconomicMetric.indicator_type == 'gdp_growth',
        EconomicMetric.indicator_type == 'inflation'
    )
).all()

# Range queries
recent_metrics = session.query(EconomicMetric).filter(
    EconomicMetric.year >= 2020,
    EconomicMetric.year <= 2024
).all()

# Using IN
countries = ['United States', 'China', 'Germany']
major_economies = session.query(EconomicMetric).filter(
    EconomicMetric.country.in_(countries)
).all()
```

### Sorting Results

```python
# Sort by year (ascending)
sorted_by_year = session.query(EconomicMetric).order_by(
    EconomicMetric.year
).all()

# Sort by year descending, then by value
sorted_metrics = session.query(EconomicMetric).order_by(
    EconomicMetric.year.desc(),
    EconomicMetric.value.desc()
).all()
```

### Limiting Results

```python
# Get top 10
top_10 = session.query(EconomicMetric).limit(10).all()

# Get page 2 (items 11-20)
page_2 = session.query(EconomicMetric).offset(10).limit(10).all()
```

### Counting and Aggregation

```python
from sqlalchemy import func

# Count total records
total = session.query(func.count(EconomicMetric.id)).scalar()
print(f"Total records: {total}")

# Average GDP growth
avg_gdp = session.query(func.avg(EconomicMetric.value)).filter(
    EconomicMetric.indicator_type == 'gdp_growth'
).scalar()
print(f"Average GDP growth: {avg_gdp:.2f}%")

# Group by country
country_counts = session.query(
    EconomicMetric.country,
    func.count(EconomicMetric.id).label('count')
).group_by(EconomicMetric.country).all()

for country, count in country_counts:
    print(f"{country}: {count} metrics")
```

---

## 7. Updating Data (UPDATE) {#updating-data}

### Update Single Record

```python
# Find record to update
metric = session.query(EconomicMetric).filter_by(id=1).first()

if metric:
    # Update values
    metric.value = 2.7  # Updated GDP growth
    metric.notes = "Revised estimate"
    
    # Save changes
    session.commit()
    print("Metric updated")
```

### Update Multiple Records

```python
# Update all US metrics to add a note
session.query(EconomicMetric).filter(
    EconomicMetric.country == 'United States'
).update({
    'notes': 'Source: Federal Reserve'
})

session.commit()
```

### Conditional Updates

```python
# Increase confidence for recent data
session.query(EconomicMetric).filter(
    EconomicMetric.year >= 2023,
    EconomicMetric.confidence < 0.9
).update({
    'confidence': EconomicMetric.confidence + 0.1
})

session.commit()
```

---

## 8. Deleting Data (DELETE) {#deleting-data}

### Delete Single Record

```python
# Find and delete
metric = session.query(EconomicMetric).filter_by(id=1).first()

if metric:
    session.delete(metric)
    session.commit()
    print("Metric deleted")
```

### Delete Multiple Records

```python
# Delete all metrics before 2010
old_metrics = session.query(EconomicMetric).filter(
    EconomicMetric.year < 2010
).delete()

session.commit()
print(f"Deleted {old_metrics} old metrics")
```

### Safe Deletion with Backup

```python
def safe_delete_metrics(session, condition):
    """Delete metrics with backup"""
    # First, backup to CSV
    metrics_to_delete = session.query(EconomicMetric).filter(condition).all()
    
    if metrics_to_delete:
        # Create backup
        backup_data = [{
            'id': m.id,
            'indicator_type': m.indicator_type,
            'value': m.value,
            'year': m.year,
            'country': m.country
        } for m in metrics_to_delete]
        
        df = pd.DataFrame(backup_data)
        backup_file = f"backup_delete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(backup_file, index=False)
        print(f"Backup saved to {backup_file}")
        
        # Now delete
        count = session.query(EconomicMetric).filter(condition).delete()
        session.commit()
        
        return count
    
    return 0
```

---

## 9. Advanced Queries for Analysis {#advanced-queries}

### Time Series Analysis

```python
def get_time_series(indicator_type, country, start_year=2010):
    """Get time series data for analysis"""
    
    data = session.query(
        EconomicMetric.year,
        EconomicMetric.value
    ).filter(
        EconomicMetric.indicator_type == indicator_type,
        EconomicMetric.country == country,
        EconomicMetric.year >= start_year
    ).order_by(EconomicMetric.year).all()
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data, columns=['year', 'value'])
    return df

# Example: Get US GDP growth time series
gdp_series = get_time_series('gdp_growth', 'United States')
print(gdp_series)
```

### Comparing Countries

```python
def compare_countries(indicator_type, year, countries):
    """Compare indicator across countries"""
    
    data = session.query(
        EconomicMetric.country,
        EconomicMetric.value,
        EconomicMetric.unit
    ).filter(
        EconomicMetric.indicator_type == indicator_type,
        EconomicMetric.year == year,
        EconomicMetric.country.in_(countries)
    ).all()
    
    # Format for display
    comparison = pd.DataFrame(data, columns=['country', 'value', 'unit'])
    return comparison.sort_values('value', ascending=False)

# Compare inflation rates
countries = ['United States', 'Germany', 'Japan', 'China']
inflation_comparison = compare_countries('inflation', 2024, countries)
print(inflation_comparison)
```

### Finding Trends

```python
from sqlalchemy import func

def find_growth_trends(indicator_type, min_years=5):
    """Find countries with consistent growth"""
    
    # Subquery for year-over-year changes
    subquery = session.query(
        EconomicMetric.country,
        EconomicMetric.year,
        EconomicMetric.value,
        func.lag(EconomicMetric.value).over(
            partition_by=EconomicMetric.country,
            order_by=EconomicMetric.year
        ).label('prev_value')
    ).filter(
        EconomicMetric.indicator_type == indicator_type
    ).subquery()
    
    # Calculate growth rates
    growth_data = session.query(
        subquery.c.country,
        subquery.c.year,
        ((subquery.c.value - subquery.c.prev_value) / subquery.c.prev_value * 100).label('growth_rate')
    ).filter(
        subquery.c.prev_value != None
    ).all()
    
    return pd.DataFrame(growth_data)
```

### Finding Anomalies

```python
def find_anomalies(indicator_type, threshold_std=2):
    """Find unusual values in data"""
    
    # Get statistics
    stats = session.query(
        func.avg(EconomicMetric.value).label('mean'),
        func.stddev(EconomicMetric.value).label('std')
    ).filter(
        EconomicMetric.indicator_type == indicator_type
    ).first()
    
    if not stats.std:
        return []
    
    # Find outliers
    lower_bound = stats.mean - (threshold_std * stats.std)
    upper_bound = stats.mean + (threshold_std * stats.std)
    
    anomalies = session.query(EconomicMetric).filter(
        EconomicMetric.indicator_type == indicator_type,
        or_(
            EconomicMetric.value < lower_bound,
            EconomicMetric.value > upper_bound
        )
    ).all()
    
    return anomalies
```

---

## 10. Data Cleaning and Validation {#data-cleaning}

### Remove Duplicates

```python
def remove_duplicate_metrics():
    """Remove duplicate entries keeping the most recent"""
    
    # Find duplicates
    duplicates = session.query(
        EconomicMetric.indicator_type,
        EconomicMetric.country,
        EconomicMetric.year,
        func.count(EconomicMetric.id).label('count')
    ).group_by(
        EconomicMetric.indicator_type,
        EconomicMetric.country,
        EconomicMetric.year
    ).having(func.count(EconomicMetric.id) > 1).all()
    
    removed_count = 0
    
    for dup in duplicates:
        # Get all matching records
        metrics = session.query(EconomicMetric).filter_by(
            indicator_type=dup.indicator_type,
            country=dup.country,
            year=dup.year
        ).order_by(EconomicMetric.created_at.desc()).all()
        
        # Keep the most recent, delete others
        for metric in metrics[1:]:
            session.delete(metric)
            removed_count += 1
    
    session.commit()
    print(f"Removed {removed_count} duplicate metrics")
```

### Validate Data Ranges

```python
def validate_metrics():
    """Check for invalid data"""
    
    issues = []
    
    # Check percentages
    invalid_percentages = session.query(EconomicMetric).filter(
        EconomicMetric.unit == 'percentage',
        or_(
            EconomicMetric.value < -100,
            EconomicMetric.value > 1000
        )
    ).all()
    
    if invalid_percentages:
        issues.append(f"Found {len(invalid_percentages)} invalid percentages")
    
    # Check years
    current_year = datetime.now().year
    invalid_years = session.query(EconomicMetric).filter(
        or_(
            EconomicMetric.year < 1900,
            EconomicMetric.year > current_year + 10
        )
    ).all()
    
    if invalid_years:
        issues.append(f"Found {len(invalid_years)} invalid years")
    
    # Check for null values
    null_values = session.query(EconomicMetric).filter(
        or_(
            EconomicMetric.value == None,
            EconomicMetric.indicator_type == None
        )
    ).all()
    
    if null_values:
        issues.append(f"Found {len(null_values)} records with null values")
    
    return issues
```

### Standardize Data

```python
def standardize_country_names():
    """Fix common country name variations"""
    
    replacements = {
        'USA': 'United States',
        'US': 'United States',
        'UK': 'United Kingdom',
        'Deutschland': 'Germany',
        'PRC': 'China',
        'Republic of Korea': 'South Korea'
    }
    
    for old_name, new_name in replacements.items():
        updated = session.query(EconomicMetric).filter(
            EconomicMetric.country == old_name
        ).update({'country': new_name})
        
        if updated:
            print(f"Updated {updated} records: {old_name} -> {new_name}")
    
    session.commit()
```

---

## 11. Handling Duplicate Data {#duplicates}

### Prevent Duplicates with Unique Constraints

```python
from sqlalchemy import UniqueConstraint

class EconomicMetricUnique(Base):
    """Metric table with unique constraint"""
    __tablename__ = 'economic_metrics_unique'
    
    id = Column(Integer, primary_key=True)
    indicator_type = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    
    # Prevent duplicate entries
    __table_args__ = (
        UniqueConstraint('indicator_type', 'country', 'year', 
                        name='unique_metric'),
    )
```

### Handle Duplicates on Insert

```python
def add_or_update_metric(metric_data):
    """Add metric or update if exists"""
    
    # Check if exists
    existing = session.query(EconomicMetric).filter_by(
        indicator_type=metric_data['indicator_type'],
        country=metric_data['country'],
        year=metric_data['year']
    ).first()
    
    if existing:
        # Update existing
        for key, value in metric_data.items():
            setattr(existing, key, value)
        print(f"Updated existing metric: {existing.id}")
    else:
        # Add new
        new_metric = EconomicMetric(**metric_data)
        session.add(new_metric)
        print("Added new metric")
    
    session.commit()
```

---

## 12. Exporting Data {#exporting}

### Export to CSV

```python
def export_to_csv(filename, indicator_type=None, country=None):
    """Export metrics to CSV"""
    
    query = session.query(EconomicMetric)
    
    # Apply filters
    if indicator_type:
        query = query.filter(EconomicMetric.indicator_type == indicator_type)
    if country:
        query = query.filter(EconomicMetric.country == country)
    
    # Get data
    metrics = query.all()
    
    # Convert to DataFrame
    data = [{
        'id': m.id,
        'indicator_type': m.indicator_type,
        'value': m.value,
        'unit': m.unit,
        'year': m.year,
        'country': m.country,
        'confidence': m.confidence,
        'notes': m.notes
    } for m in metrics]
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Exported {len(df)} records to {filename}")

# Export all US data
export_to_csv("us_economic_data.csv", country="United States")
```

### Export to Excel with Multiple Sheets

```python
def export_to_excel(filename):
    """Export data organized by indicator type"""
    
    with pd.ExcelWriter(filename) as writer:
        # Get unique indicator types
        indicators = session.query(
            EconomicMetric.indicator_type
        ).distinct().all()
        
        for (indicator,) in indicators:
            # Get data for this indicator
            metrics = session.query(EconomicMetric).filter(
                EconomicMetric.indicator_type == indicator
            ).all()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'country': m.country,
                'year': m.year,
                'value': m.value,
                'unit': m.unit
            } for m in metrics])
            
            # Write to sheet
            if not df.empty:
                df.to_excel(writer, sheet_name=indicator[:31], index=False)
        
    print(f"Exported data to {filename}")
```

### Export to JSON

```python
import json

def export_to_json(filename):
    """Export data as JSON"""
    
    metrics = session.query(EconomicMetric).all()
    
    data = {
        'export_date': datetime.now().isoformat(),
        'total_records': len(metrics),
        'metrics': [{
            'id': m.id,
            'indicator_type': m.indicator_type,
            'value': m.value,
            'unit': m.unit,
            'year': m.year,
            'country': m.country,
            'confidence': m.confidence
        } for m in metrics]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Exported {len(metrics)} records to {filename}")
```

---

## 13. Best Practices {#best-practices}

### 1. Always Use Sessions Properly

```python
from contextlib import contextmanager

@contextmanager
def get_db_session():
    """Ensure sessions are properly closed"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# Usage
with get_db_session() as session:
    metric = EconomicMetric(indicator_type='gdp', value=2.5, year=2024)
    session.add(metric)
```

### 2. Use Transactions for Multiple Operations

```python
def import_economic_report(report_data):
    """Import complete report in one transaction"""
    
    try:
        # Start transaction
        session.begin()
        
        # Add source
        source = DataSource(name=report_data['source'])
        session.add(source)
        session.flush()  # Get source ID
        
        # Add all metrics
        for metric_data in report_data['metrics']:
            metric = EconomicMetric(
                source_id=source.id,
                **metric_data
            )
            session.add(metric)
        
        # Commit if all successful
        session.commit()
        print(f"Imported {len(report_data['metrics'])} metrics")
        
    except Exception as e:
        # Rollback on any error
        session.rollback()
        print(f"Import failed: {e}")
        raise
```

### 3. Index Frequently Queried Columns

```python
# Add indexes after table creation
from sqlalchemy import Index

# Create index on frequently queried columns
Index('idx_year_country', EconomicMetric.year, EconomicMetric.country)
Index('idx_indicator_value', EconomicMetric.indicator_type, EconomicMetric.value)
```

### 4. Use Lazy Loading for Large Datasets

```python
def process_large_dataset():
    """Process data in chunks to avoid memory issues"""
    
    # Use yield_per for memory efficiency
    query = session.query(EconomicMetric).yield_per(1000)
    
    processed = 0
    for metric in query:
        # Process each metric
        process_metric(metric)
        processed += 1
        
        if processed % 1000 == 0:
            print(f"Processed {processed} metrics...")
```

---

## 14. Complete Working Example {#complete-example}

### Economic Database Manager

```python
"""
Complete Economic Database Manager
Save as: economic_db_manager.py
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, func, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from contextlib import contextmanager
import pandas as pd
import json

# Create base
Base = declarative_base()

# Define models
class EconomicMetric(Base):
    __tablename__ = 'economic_metrics'
    
    id = Column(Integer, primary_key=True)
    indicator_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)
    country = Column(String(100), default='Global')
    region = Column(String(100))
    source = Column(String(255))
    confidence = Column(Float, default=1.0)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EconomicDatabaseManager:
    """Manager class for economic database operations"""
    
    def __init__(self, db_path="economic_data.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
    
    def add_metric(self, indicator_type, value, unit, year, **kwargs):
        """Add single economic metric"""
        with self.get_session() as session:
            metric = EconomicMetric(
                indicator_type=indicator_type,
                value=value,
                unit=unit,
                year=year,
                **kwargs
            )
            session.add(metric)
            return metric.id
    
    def bulk_add_metrics(self, metrics_list):
        """Add multiple metrics efficiently"""
        with self.get_session() as session:
            # Check for duplicates
            added = 0
            skipped = 0
            
            for metric_data in metrics_list:
                # Check if exists
                existing = session.query(EconomicMetric).filter_by(
                    indicator_type=metric_data['indicator_type'],
                    year=metric_data['year'],
                    country=metric_data.get('country', 'Global')
                ).first()
                
                if not existing:
                    metric = EconomicMetric(**metric_data)
                    session.add(metric)
                    added += 1
                else:
                    skipped += 1
            
            print(f"Added {added} metrics, skipped {skipped} duplicates")
    
    def get_time_series(self, indicator_type, country='Global', start_year=None):
        """Get time series data for indicator"""
        with self.get_session() as session:
            query = session.query(
                EconomicMetric.year,
                EconomicMetric.value,
                EconomicMetric.unit
            ).filter(
                EconomicMetric.indicator_type == indicator_type,
                EconomicMetric.country == country
            )
            
            if start_year:
                query = query.filter(EconomicMetric.year >= start_year)
            
            data = query.order_by(EconomicMetric.year).all()
            
            return pd.DataFrame(data, columns=['year', 'value', 'unit'])
    
    def compare_countries(self, indicator_type, year):
        """Compare indicator across all countries for a year"""
        with self.get_session() as session:
            data = session.query(
                EconomicMetric.country,
                EconomicMetric.value,
                EconomicMetric.unit
            ).filter(
                EconomicMetric.indicator_type == indicator_type,
                EconomicMetric.year == year
            ).order_by(EconomicMetric.value.desc()).all()
            
            return pd.DataFrame(data, columns=['country', 'value', 'unit'])
    
    def get_latest_value(self, indicator_type, country='Global'):
        """Get most recent value for indicator"""
        with self.get_session() as session:
            metric = session.query(EconomicMetric).filter(
                EconomicMetric.indicator_type == indicator_type,
                EconomicMetric.country == country
            ).order_by(EconomicMetric.year.desc()).first()
            
            if metric:
                return {
                    'value': metric.value,
                    'unit': metric.unit,
                    'year': metric.year,
                    'notes': metric.notes
                }
            return None
    
    def find_correlations(self, indicator1, indicator2, country='Global'):
        """Find correlation between two indicators"""
        with self.get_session() as session:
            # Get both series
            data1 = session.query(
                EconomicMetric.year,
                EconomicMetric.value
            ).filter(
                EconomicMetric.indicator_type == indicator1,
                EconomicMetric.country == country
            ).all()
            
            data2 = session.query(
                EconomicMetric.year,
                EconomicMetric.value
            ).filter(
                EconomicMetric.indicator_type == indicator2,
                EconomicMetric.country == country
            ).all()
            
            # Convert to DataFrames
            df1 = pd.DataFrame(data1, columns=['year', indicator1])
            df2 = pd.DataFrame(data2, columns=['year', indicator2])
            
            # Merge on year
            merged = pd.merge(df1, df2, on='year')
            
            if len(merged) > 2:
                correlation = merged[indicator1].corr(merged[indicator2])
                return {
                    'correlation': correlation,
                    'data_points': len(merged),
                    'years': f"{merged['year'].min()}-{merged['year'].max()}"
                }
            
            return None
    
    def export_data(self, filename, format='csv', filters=None):
        """Export data in various formats"""
        with self.get_session() as session:
            query = session.query(EconomicMetric)
            
            # Apply filters if provided
            if filters:
                if 'indicator_type' in filters:
                    query = query.filter(
                        EconomicMetric.indicator_type == filters['indicator_type']
                    )
                if 'country' in filters:
                    query = query.filter(
                        EconomicMetric.country == filters['country']
                    )
                if 'year_min' in filters:
                    query = query.filter(
                        EconomicMetric.year >= filters['year_min']
                    )
            
            # Get data
            metrics = query.all()
            
            # Convert to desired format
            if format == 'csv':
                df = pd.DataFrame([{
                    'indicator_type': m.indicator_type,
                    'value': m.value,
                    'unit': m.unit,
                    'year': m.year,
                    'country': m.country,
                    'source': m.source
                } for m in metrics])
                df.to_csv(filename, index=False)
                
            elif format == 'json':
                data = {
                    'export_date': datetime.now().isoformat(),
                    'records': len(metrics),
                    'metrics': [self._metric_to_dict(m) for m in metrics]
                }
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
            
            print(f"Exported {len(metrics)} records to {filename}")
    
    def _metric_to_dict(self, metric):
        """Convert metric object to dictionary"""
        return {
            'id': metric.id,
            'indicator_type': metric.indicator_type,
            'value': metric.value,
            'unit': metric.unit,
            'year': metric.year,
            'country': metric.country,
            'source': metric.source,
            'confidence': metric.confidence
        }
    
    def get_summary_statistics(self):
        """Get database summary"""
        with self.get_session() as session:
            total = session.query(func.count(EconomicMetric.id)).scalar()
            
            indicators = session.query(
                EconomicMetric.indicator_type,
                func.count(EconomicMetric.id)
            ).group_by(EconomicMetric.indicator_type).all()
            
            countries = session.query(
                func.count(func.distinct(EconomicMetric.country))
            ).scalar()
            
            year_range = session.query(
                func.min(EconomicMetric.year),
                func.max(EconomicMetric.year)
            ).first()
            
            return {
                'total_metrics': total,
                'unique_indicators': len(indicators),
                'unique_countries': countries,
                'year_range': f"{year_range[0]}-{year_range[1]}",
                'indicators': dict(indicators)
            }


# Example usage
if __name__ == "__main__":
    # Initialize manager
    db = EconomicDatabaseManager()
    
    # Add sample data
    sample_metrics = [
        {
            'indicator_type': 'gdp_growth',
            'value': 2.5,
            'unit': 'percentage',
            'year': 2024,
            'country': 'United States',
            'source': 'World Bank'
        },
        {
            'indicator_type': 'inflation',
            'value': 3.2,
            'unit': 'percentage',
            'year': 2024,
            'country': 'United States',
            'source': 'Federal Reserve'
        },
        {
            'indicator_type': 'unemployment',
            'value': 3.9,
            'unit': 'percentage',
            'year': 2024,
            'country': 'United States',
            'source': 'BLS'
        }
    ]
    
    # Add metrics
    db.bulk_add_metrics(sample_metrics)
    
    # Get time series
    gdp_series = db.get_time_series('gdp_growth', 'United States')
    print("\nGDP Growth Time Series:")
    print(gdp_series)
    
    # Get latest values
    latest_gdp = db.get_latest_value('gdp_growth', 'United States')
    print(f"\nLatest GDP Growth: {latest_gdp}")
    
    # Get summary
    summary = db.get_summary_statistics()
    print(f"\nDatabase Summary: {summary}")
    
    # Export data
    db.export_data('us_economic_data.csv', filters={'country': 'United States'})
```

---

## 15. Common Economic Queries {#economic-queries}

### Query Templates for Economic Analysis

```python
# 1. Year-over-Year Growth
def calculate_yoy_growth(indicator_type, country):
    """Calculate year-over-year growth rates"""
    
    with get_db_session() as session:
        # Get current and previous year data
        current = session.query(EconomicMetric).filter(
            EconomicMetric.indicator_type == indicator_type,
            EconomicMetric.country == country,
            EconomicMetric.year == 2024
        ).first()
        
        previous = session.query(EconomicMetric).filter(
            EconomicMetric.indicator_type == indicator_type,
            EconomicMetric.country == country,
            EconomicMetric.year == 2023
        ).first()
        
        if current and previous:
            growth = ((current.value - previous.value) / previous.value) * 100
            return {
                'growth_rate': round(growth, 2),
                'current_value': current.value,
                'previous_value': previous.value
            }

# 2. Find Economic Turning Points
def find_turning_points(indicator_type, country):
    """Find years where trend changed"""
    
    with get_db_session() as session:
        data = session.query(
            EconomicMetric.year,
            EconomicMetric.value
        ).filter(
            EconomicMetric.indicator_type == indicator_type,
            EconomicMetric.country == country
        ).order_by(EconomicMetric.year).all()
        
        turning_points = []
        
        for i in range(1, len(data) - 1):
            prev_change = data[i][1] - data[i-1][1]
            next_change = data[i+1][1] - data[i][1]
            
            # Direction changed
            if prev_change * next_change < 0:
                turning_points.append({
                    'year': data[i][0],
                    'value': data[i][1],
                    'type': 'peak' if prev_change > 0 else 'trough'
                })
        
        return turning_points

# 3. Regional Analysis
def analyze_by_region(indicator_type, year):
    """Aggregate metrics by region"""
    
    with get_db_session() as session:
        regional_data = session.query(
            EconomicMetric.region,
            func.avg(EconomicMetric.value).label('avg_value'),
            func.min(EconomicMetric.value).label('min_value'),
            func.max(EconomicMetric.value).label('max_value'),
            func.count(EconomicMetric.id).label('country_count')
        ).filter(
            EconomicMetric.indicator_type == indicator_type,
            EconomicMetric.year == year,
            EconomicMetric.region != None
        ).group_by(EconomicMetric.region).all()
        
        return pd.DataFrame(regional_data)
```

---

## 16. Troubleshooting {#troubleshooting}

### Common Issues and Solutions

#### Issue 1: "Table already exists"
```python
# Solution: Drop existing tables (WARNING: deletes all data!)
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
```

#### Issue 2: "No such column"
```python
# Solution: Update database schema
from alembic import op
import sqlalchemy as sa

# Add new column to existing table
def upgrade():
    op.add_column('economic_metrics', 
                  sa.Column('new_field', sa.String(100)))
```

#### Issue 3: Session not committing
```python
# Always use context manager or explicit commit
session.add(metric)
session.commit()  # Don't forget this!

# Or use context manager (recommended)
with get_db_session() as session:
    session.add(metric)
    # Commits automatically
```

#### Issue 4: Slow queries
```python
# Solution 1: Add indexes
Index('idx_year_country', EconomicMetric.year, EconomicMetric.country)

# Solution 2: Use query optimization
# Bad - loads all data
all_metrics = session.query(EconomicMetric).all()
filtered = [m for m in all_metrics if m.year == 2024]

# Good - filters in database
filtered = session.query(EconomicMetric).filter(
    EconomicMetric.year == 2024
).all()
```

#### Issue 5: Memory issues with large datasets
```python
# Use chunking for large operations
def process_large_dataset():
    offset = 0
    chunk_size = 1000
    
    while True:
        chunk = session.query(EconomicMetric).offset(offset).limit(chunk_size).all()
        
        if not chunk:
            break
            
        process_chunk(chunk)
        offset += chunk_size
```

---

## Quick Reference

### Essential SQLAlchemy Commands
```python
# Create
session.add(object)
session.add_all([obj1, obj2])

# Read
session.query(Model).all()
session.query(Model).first()
session.query(Model).filter_by(field=value).all()
session.query(Model).filter(Model.field == value).all()

# Update
obj.field = new_value
session.query(Model).filter_by(id=1).update({'field': value})

# Delete
session.delete(object)
session.query(Model).filter_by(id=1).delete()

# Aggregate
session.query(func.count(Model.id)).scalar()
session.query(func.avg(Model.value)).scalar()
session.query(func.sum(Model.value)).scalar()

# Commit changes
session.commit()

# Rollback on error
session.rollback()
```

---

## Next Steps

1. **Practice**: Start with the complete example and modify for your data
2. **Optimize**: Add indexes for your common queries
3. **Backup**: Regularly export your data
4. **Scale**: Consider PostgreSQL for very large datasets
5. **Visualize**: Connect your database to Dash/Plotly for charts

Remember: Databases are powerful tools for economic analysis. Take time to understand the queries - they'll save you hours of manual work!