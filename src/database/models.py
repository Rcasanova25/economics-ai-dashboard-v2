"""
Database Models for Economics AI Dashboard

This module defines the SQLite database schema using SQLAlchemy ORM.
Follows best practices for data integrity and query performance.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, 
    DateTime, ForeignKey, Index, UniqueConstraint, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class DataSource(Base):
    """Store information about PDF sources."""
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    organization = Column(String(255))
    pdf_path = Column(String(500))
    url = Column(String(500))
    publication_date = Column(DateTime)
    extraction_date = Column(DateTime, default=datetime.utcnow)
    page_count = Column(Integer)
    
    # Relationships
    metrics = relationship("AIMetric", back_populates="source")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_name', 'name'),
        Index('idx_source_org', 'organization'),
    )


class AIMetric(Base):
    """Store individual AI metrics extracted from PDFs."""
    __tablename__ = 'ai_metrics'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('data_sources.id'), nullable=False)
    
    # Metric details
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Optional categorization
    sector = Column(String(100))
    region = Column(String(100))
    technology = Column(String(100))
    
    # Context and confidence
    context = Column(Text)  # Full context for verification
    confidence = Column(Float, default=1.0)
    page_number = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("DataSource", back_populates="metrics")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_metric_type_year', 'metric_type', 'year'),
        Index('idx_metric_source', 'source_id'),
        Index('idx_metric_sector', 'sector'),
        Index('idx_metric_region', 'region'),
        # Prevent exact duplicates
        UniqueConstraint('source_id', 'metric_type', 'value', 'unit', 'year', 
                        'sector', 'region', name='uq_metric'),
    )


class ConflictingMetric(Base):
    """Track metrics that conflict across sources for analysis."""
    __tablename__ = 'conflicting_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_type = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    sector = Column(String(100))
    region = Column(String(100))
    
    # Store conflicting values as JSON or separate table
    conflict_description = Column(Text)
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_conflict_type_year', 'metric_type', 'year'),
    )


class ExtractionLog(Base):
    """Track extraction runs for debugging and auditing."""
    __tablename__ = 'extraction_logs'
    
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('data_sources.id'))
    
    extraction_type = Column(String(50))  # 'specialized', 'universal', etc.
    status = Column(String(20))  # 'success', 'failed', 'partial'
    metrics_extracted = Column(Integer, default=0)
    statistics_found = Column(Integer, default=0)
    
    error_message = Column(Text)
    extraction_time_seconds = Column(Float)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Indexes
    __table_args__ = (
        Index('idx_log_source', 'source_id'),
        Index('idx_log_status', 'status'),
    )


# Database connection and session management
def get_engine(db_path: str = "data/processed/economics_ai.db"):
    """Create database engine with optimized settings."""
    engine = create_engine(
        f"sqlite:///{db_path}",
        # Performance optimizations for SQLite
        connect_args={
            "check_same_thread": False,  # Allow multi-threading
            "timeout": 30,  # 30 second timeout
        },
        # Connection pool settings
        pool_pre_ping=True,  # Verify connections before use
        echo=False  # Set to True for SQL debugging
    )
    return engine


def create_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()


# Example usage and best practices
if __name__ == "__main__":
    # This demonstrates proper database initialization
    engine = get_engine()
    create_tables(engine)
    print("Database schema created successfully!")