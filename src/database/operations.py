"""
Database Operations for Economics AI Dashboard

This module provides safe, efficient database operations with proper
error handling, transaction management, and data validation.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import and_, or_, func

from .models import (
    get_engine, get_session, create_tables,
    DataSource, AIMetric, ConflictingMetric, ExtractionLog
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


@contextmanager
def session_scope(engine):
    """
    Provide a transactional scope for database operations.
    
    This ensures proper transaction management and error handling.
    """
    session = get_session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        session.close()


class MetricsDatabase:
    """Main interface for database operations."""
    
    def __init__(self, db_path: str = "data/processed/economics_ai.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.engine = get_engine(db_path)
        
        # Ensure database exists
        self._ensure_database()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist."""
        try:
            create_tables(self.engine)
            logger.info(f"Database initialized at: {self.db_path}")
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def add_source(self, name: str, organization: str = None, 
                   pdf_path: str = None, url: str = None,
                   publication_date: datetime = None, 
                   page_count: int = None) -> int:
        """
        Add a new data source to the database.
        
        Returns:
            source_id: The ID of the created source
        """
        with session_scope(self.engine) as session:
            # Check if source already exists
            existing = session.query(DataSource).filter_by(name=name).first()
            if existing:
                logger.info(f"Source already exists: {name}")
                return existing.id
            
            source = DataSource(
                name=name,
                organization=organization,
                pdf_path=pdf_path,
                url=url,
                publication_date=publication_date,
                page_count=page_count
            )
            
            session.add(source)
            session.flush()  # Get the ID before commit
            source_id = source.id
            
            logger.info(f"Added source: {name} (ID: {source_id})")
            return source_id
    
    def add_metrics_batch(self, metrics: List[Dict], source_name: str) -> Tuple[int, int]:
        """
        Add multiple metrics in a single transaction.
        
        Args:
            metrics: List of metric dictionaries
            source_name: Name of the data source
            
        Returns:
            (success_count, duplicate_count)
        """
        success_count = 0
        duplicate_count = 0
        
        with session_scope(self.engine) as session:
            # Get or create source
            source = session.query(DataSource).filter_by(name=source_name).first()
            if not source:
                # Create source if it doesn't exist
                source = DataSource(name=source_name)
                session.add(source)
                session.flush()
            
            for metric_data in metrics:
                try:
                    metric = AIMetric(
                        source_id=source.id,
                        metric_type=metric_data['metric_type'],
                        value=float(metric_data['value']),
                        unit=metric_data['unit'],
                        year=int(metric_data.get('year', 2025)),
                        sector=metric_data.get('sector'),
                        region=metric_data.get('region'),
                        technology=metric_data.get('technology'),
                        context=metric_data.get('context'),
                        confidence=float(metric_data.get('confidence', 1.0)),
                        page_number=metric_data.get('page_number')
                    )
                    
                    session.add(metric)
                    success_count += 1
                    
                except IntegrityError:
                    # Handle duplicates gracefully
                    session.rollback()
                    duplicate_count += 1
                    continue
                except Exception as e:
                    logger.error(f"Failed to add metric: {e}")
                    session.rollback()
                    continue
            
            # Log the extraction
            log_entry = ExtractionLog(
                source_id=source.id,
                extraction_type='batch_import',
                status='success',
                metrics_extracted=success_count,
                completed_at=datetime.utcnow()
            )
            session.add(log_entry)
        
        logger.info(f"Added {success_count} metrics, {duplicate_count} duplicates skipped")
        return success_count, duplicate_count
    
    def get_metrics_by_type(self, metric_type: str, 
                           year: Optional[int] = None,
                           sector: Optional[str] = None) -> List[Dict]:
        """
        Retrieve metrics by type with optional filters.
        
        Returns list of metric dictionaries with source information.
        """
        with session_scope(self.engine) as session:
            query = session.query(AIMetric).join(DataSource)
            
            # Apply filters
            query = query.filter(AIMetric.metric_type == metric_type)
            if year:
                query = query.filter(AIMetric.year == year)
            if sector:
                query = query.filter(AIMetric.sector == sector)
            
            # Order by year and confidence
            query = query.order_by(AIMetric.year.desc(), AIMetric.confidence.desc())
            
            results = []
            for metric in query.all():
                results.append({
                    'id': metric.id,
                    'value': metric.value,
                    'unit': metric.unit,
                    'year': metric.year,
                    'sector': metric.sector,
                    'region': metric.region,
                    'confidence': metric.confidence,
                    'source': metric.source.name,
                    'organization': metric.source.organization,
                    'context': metric.context
                })
            
            return results
    
    def find_conflicts(self, metric_type: str, year: int, 
                      threshold: float = 0.1) -> List[Dict]:
        """
        Find conflicting metrics for the same type and year.
        
        Args:
            metric_type: Type of metric to check
            year: Year to check
            threshold: Relative difference threshold (0.1 = 10%)
            
        Returns:
            List of conflict dictionaries
        """
        with session_scope(self.engine) as session:
            # Get all metrics of this type and year
            metrics = session.query(AIMetric).join(DataSource).filter(
                and_(
                    AIMetric.metric_type == metric_type,
                    AIMetric.year == year
                )
            ).all()
            
            if len(metrics) < 2:
                return []
            
            conflicts = []
            
            # Compare metrics pairwise
            for i in range(len(metrics)):
                for j in range(i + 1, len(metrics)):
                    m1, m2 = metrics[i], metrics[j]
                    
                    # Skip if different units or sectors
                    if m1.unit != m2.unit:
                        continue
                    if m1.sector != m2.sector and (m1.sector and m2.sector):
                        continue
                    
                    # Calculate relative difference
                    # Handle zero values
                    max_value = max(abs(m1.value), abs(m2.value))
                    if max_value == 0:
                        continue
                    diff = abs(m1.value - m2.value) / max_value
                    
                    if diff > threshold:
                        conflicts.append({
                            'metric_type': metric_type,
                            'year': year,
                            'value1': m1.value,
                            'value2': m2.value,
                            'unit': m1.unit,
                            'source1': m1.source.name,
                            'source2': m2.source.name,
                            'difference_pct': round(diff * 100, 2),
                            'sector': m1.sector or m2.sector,
                            'region': m1.region or m2.region
                        })
            
            # Record conflicts
            if conflicts:
                conflict_record = ConflictingMetric(
                    metric_type=metric_type,
                    year=year,
                    conflict_description=f"Found {len(conflicts)} conflicting values"
                )
                session.add(conflict_record)
            
            return conflicts
    
    def get_summary_stats(self) -> Dict:
        """Get database summary statistics."""
        with session_scope(self.engine) as session:
            stats = {
                'total_sources': session.query(DataSource).count(),
                'total_metrics': session.query(AIMetric).count(),
                'metric_types': session.query(
                    func.distinct(AIMetric.metric_type)
                ).count(),
                'year_range': session.query(
                    func.min(AIMetric.year),
                    func.max(AIMetric.year)
                ).first(),
                'sectors': session.query(
                    func.distinct(AIMetric.sector)
                ).filter(AIMetric.sector.isnot(None)).count(),
                'avg_confidence': session.query(
                    func.avg(AIMetric.confidence)
                ).scalar()
            }
            
            # Get metrics by type
            type_counts = session.query(
                AIMetric.metric_type,
                func.count(AIMetric.id)
            ).group_by(AIMetric.metric_type).all()
            
            stats['metrics_by_type'] = dict(type_counts)
            
            return stats
    
    def export_to_dict(self, limit: Optional[int] = None) -> Dict:
        """Export all metrics as dictionary for analysis."""
        with session_scope(self.engine) as session:
            query = session.query(AIMetric).join(DataSource)
            
            if limit:
                query = query.limit(limit)
            
            metrics = []
            for metric in query.all():
                metrics.append({
                    'metric_type': metric.metric_type,
                    'value': metric.value,
                    'unit': metric.unit,
                    'year': metric.year,
                    'sector': metric.sector,
                    'region': metric.region,
                    'technology': metric.technology,
                    'confidence': metric.confidence,
                    'source': metric.source.name,
                    'organization': metric.source.organization
                })
            
            return {
                'metrics': metrics,
                'count': len(metrics),
                'export_date': datetime.utcnow().isoformat()
            }


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = MetricsDatabase()
    
    # Add a test source
    source_id = db.add_source(
        name="Test Report 2025",
        organization="Test Organization",
        publication_date=datetime(2025, 1, 1)
    )
    
    # Add test metrics
    test_metrics = [
        {
            'metric_type': 'adoption_rate',
            'value': 75.5,
            'unit': 'percentage',
            'year': 2024,
            'sector': 'Enterprise',
            'confidence': 0.95
        },
        {
            'metric_type': 'investment',
            'value': 250.0,
            'unit': 'billions_usd',
            'year': 2024,
            'sector': 'Global',
            'confidence': 0.90
        }
    ]
    
    success, dupes = db.add_metrics_batch(test_metrics, "Test Report 2025")
    print(f"Added {success} metrics")
    
    # Get summary
    stats = db.get_summary_stats()
    print(f"Database stats: {stats}")