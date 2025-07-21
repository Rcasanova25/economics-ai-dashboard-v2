"""
Centralized Logging Configuration for Economics AI Dashboard
Provides structured logging with rotation and different log levels
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured log records"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured data"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'source_id'):
            log_data['source_id'] = record.source_id
        if hasattr(record, 'operation'):
            log_data['operation'] = record.operation
        if hasattr(record, 'records_affected'):
            log_data['records_affected'] = record.records_affected
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
            
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


class CleanupLogger:
    """Specialized logger for data cleanup operations"""
    
    def __init__(self, name: str = "data_cleanup"):
        self.logger = logging.getLogger(name)
        
    def log_cleanup_start(self, source_id: int, total_records: int):
        """Log the start of a cleanup operation"""
        self.logger.info(
            f"Starting cleanup for source {source_id}",
            extra={
                'source_id': source_id,
                'operation': 'cleanup_start',
                'records_affected': total_records
            }
        )
        
    def log_cleanup_action(self, source_id: int, action: str, count: int, reason: str = ""):
        """Log a specific cleanup action"""
        self.logger.info(
            f"Cleanup action: {action} - {count} records",
            extra={
                'source_id': source_id,
                'operation': f'cleanup_{action}',
                'records_affected': count,
                'reason': reason
            }
        )
        
    def log_cleanup_complete(self, source_id: int, summary: Dict[str, Any]):
        """Log cleanup completion with summary"""
        self.logger.info(
            f"Cleanup completed for source {source_id}",
            extra={
                'source_id': source_id,
                'operation': 'cleanup_complete',
                **summary
            }
        )
        
    def log_error(self, source_id: int, error: Exception, context: str = ""):
        """Log an error during cleanup"""
        self.logger.error(
            f"Error during cleanup: {str(error)}",
            extra={
                'source_id': source_id,
                'operation': 'cleanup_error',
                'error_type': type(error).__name__,
                'context': context
            },
            exc_info=True
        )


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_structured: bool = False
):
    """
    Set up logging configuration for the entire application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to log to console
        enable_file: Whether to log to file
        enable_structured: Whether to use structured (JSON) logging
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if enable_structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # Main log file with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / "economics_ai.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / "economics_ai_errors.log",
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)
        
        # Cleanup operations log
        cleanup_handler = logging.handlers.RotatingFileHandler(
            log_path / "cleanup_operations.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        cleanup_handler.setFormatter(formatter)
        cleanup_handler.setLevel(logging.INFO)
        
        # Add cleanup handler only to cleanup logger
        cleanup_logger = logging.getLogger("data_cleanup")
        cleanup_logger.addHandler(cleanup_handler)
        cleanup_logger.propagate = True  # Also log to root logger
    
    # Log startup
    logging.info("Logging system initialized")
    logging.info(f"Log level: {log_level}")
    logging.info(f"Log directory: {log_path.absolute()}")
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def get_cleanup_logger() -> CleanupLogger:
    """Get a specialized cleanup logger instance"""
    return CleanupLogger()


# Example usage
if __name__ == "__main__":
    # Setup logging
    setup_logging(
        log_level="DEBUG",
        enable_structured=True
    )
    
    # Test regular logging
    logger = get_logger(__name__)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Test cleanup logging
    cleanup_logger = get_cleanup_logger()
    cleanup_logger.log_cleanup_start(source_id=3, total_records=1000)
    cleanup_logger.log_cleanup_action(
        source_id=3, 
        action="remove_duplicates", 
        count=250,
        reason="Duplicate records identified"
    )
    cleanup_logger.log_cleanup_complete(
        source_id=3,
        summary={
            'total_processed': 1000,
            'kept': 700,
            'removed': 250,
            'modified': 50,
            'duration_seconds': 12.5
        }
    )
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        cleanup_logger.log_error(source_id=3, error=e, context="Testing error logging")