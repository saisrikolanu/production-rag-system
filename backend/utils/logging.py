"""
Logging configuration module
Structured logging for production system
"""

import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger

def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """
    Setup structured logging with file and console handlers
    
    Args:
        log_level: Logging level (INFO, DEBUG, ERROR, etc.)
        log_file: Path to log file
    """
    try:
        # Create logs directory
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # JSON formatter for structured logging
        json_formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
        
        # Console handler (human-readable)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (JSON structured)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
        
        logging.info("✓ Logging configured")
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        raise

def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a module
    
    Args:
        name: Module name (__name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class StructuredLogger:
    """Wrapper for structured logging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def info(self, message: str, **kwargs):
        """Log info with context"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error with context"""
        if error:
            kwargs['error'] = str(error)
            kwargs['error_type'] = type(error).__name__
        self.logger.error(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug with context"""
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning with context"""
        self.logger.warning(message, extra=kwargs)