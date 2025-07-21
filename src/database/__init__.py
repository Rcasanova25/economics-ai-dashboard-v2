"""
Database Package for Economics AI Dashboard

Provides SQLite database functionality for storing and querying AI metrics.
"""

from .models import (
    DataSource, AIMetric, ConflictingMetric, ExtractionLog,
    get_engine, create_tables, get_session
)
from .operations import MetricsDatabase, DatabaseError, session_scope

__all__ = [
    'DataSource',
    'AIMetric', 
    'ConflictingMetric',
    'ExtractionLog',
    'get_engine',
    'create_tables',
    'get_session',
    'MetricsDatabase',
    'DatabaseError',
    'session_scope'
]