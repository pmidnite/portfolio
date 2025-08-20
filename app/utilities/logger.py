import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class LoggerConfig:
    """Configuration class for the logger utility"""

    def __init__(self):
        # Default configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.LOG_FORMAT = os.getenv('LOG_FORMAT', 'detailed')  # 'simple', 'detailed', 'json'
        self.LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'true').lower() == 'true'
        self.LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true'
        self.LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs')
        self.LOG_FILE_NAME = os.getenv('LOG_FILE_NAME', 'portfolio.log')
        self.LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
        self.APP_NAME = os.getenv('APP_NAME', 'Portfolio')

        # Ensure log directory exists
        if self.LOG_TO_FILE:
            Path(self.LOG_FILE_PATH).mkdir(parents=True, exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def __init__(self, app_name: str = "Portfolio"):
        super().__init__()
        self.app_name = app_name

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "application": self.app_name,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry["extra"] = record.extra_data

        return json.dumps(log_entry)


class PortfolioLogger:
    """
    Centralized logging utility for the Portfolio application.
    Provides structured logging with file rotation, multiple output formats,
    and easy-to-use methods for different log levels.
    """

    _instance = None
    _loggers: Dict[str, logging.Logger] = {}
    _config: LoggerConfig = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PortfolioLogger, cls).__new__(cls)
            cls._config = LoggerConfig()
            cls._setup_root_logger()
        return cls._instance

    @classmethod
    def _setup_root_logger(cls):
        """Setup the root logger configuration"""
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, cls._config.LOG_LEVEL))

        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Setup formatters
        formatters = cls._get_formatters()

        # Console handler
        if cls._config.LOG_TO_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, cls._config.LOG_LEVEL))
            console_handler.setFormatter(formatters['console'])
            root_logger.addHandler(console_handler)

        # File handler with rotation
        if cls._config.LOG_TO_FILE:
            log_file_path = os.path.join(cls._config.LOG_FILE_PATH, cls._config.LOG_FILE_NAME)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=cls._config.LOG_MAX_BYTES,
                backupCount=cls._config.LOG_BACKUP_COUNT
            )
            file_handler.setLevel(getattr(logging, cls._config.LOG_LEVEL))
            file_handler.setFormatter(formatters['file'])
            root_logger.addHandler(file_handler)

    @classmethod
    def _get_formatters(cls):
        """Get formatters based on configuration"""
        formatters = {}

        if cls._config.LOG_FORMAT == 'simple':
            console_format = '%(levelname)s - %(message)s'
            file_format = '%(asctime)s - %(levelname)s - %(message)s'
        elif cls._config.LOG_FORMAT == 'json':
            console_format = file_format = None  # Will use JSONFormatter
        else:  # detailed
            console_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            file_format = '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'

        if cls._config.LOG_FORMAT == 'json':
            formatters['console'] = JSONFormatter(cls._config.APP_NAME)
            formatters['file'] = JSONFormatter(cls._config.APP_NAME)
        else:
            formatters['console'] = logging.Formatter(console_format)
            formatters['file'] = logging.Formatter(file_format)

        return formatters

    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """
        Get a logger instance for the specified name.

        Args:
            name: Logger name (usually __name__ of the calling module)

        Returns:
            logging.Logger: Configured logger instance
        """
        if name is None:
            name = 'app'

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def log_with_extra(cls, level: str, message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
        """
        Log a message with extra structured data.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            extra_data: Additional data to include in the log
            logger_name: Name of the logger to use
        """
        logger = cls.get_logger(logger_name)
        log_level = getattr(logging, level.upper())

        if extra_data:
            # Create a custom LogRecord with extra data
            record = logger.makeRecord(
                logger.name, log_level, "", 0, message, (), None
            )
            record.extra_data = extra_data
            logger.handle(record)
        else:
            logger.log(log_level, message)


# Convenience functions for easy importing
def get_logger(name: str = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__ of the calling module)

    Returns:
        logging.Logger: Configured logger instance

    Example:
        from app.utilities.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is a log message")
    """
    return PortfolioLogger.get_logger(name)


def log_info(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """Log an INFO level message with optional extra data"""
    PortfolioLogger.log_with_extra('INFO', message, extra_data, logger_name)


def log_debug(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """Log a DEBUG level message with optional extra data"""
    PortfolioLogger.log_with_extra('DEBUG', message, extra_data, logger_name)


def log_warning(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """Log a WARNING level message with optional extra data"""
    PortfolioLogger.log_with_extra('WARNING', message, extra_data, logger_name)


def log_error(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """Log an ERROR level message with optional extra data"""
    PortfolioLogger.log_with_extra('ERROR', message, extra_data, logger_name)


def log_critical(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """Log a CRITICAL level message with optional extra data"""
    PortfolioLogger.log_with_extra('CRITICAL', message, extra_data, logger_name)


def log_exception(message: str, extra_data: Dict[str, Any] = None, logger_name: str = None):
    """
    Log an exception with stack trace.

    Args:
        message: Log message
        extra_data: Additional data to include in the log
        logger_name: Name of the logger to use
    """
    logger = PortfolioLogger.get_logger(logger_name)
    if extra_data:
        record = logger.makeRecord(
            logger.name, logging.ERROR, "", 0, message, (), sys.exc_info()
        )
        record.extra_data = extra_data
        logger.handle(record)
    else:
        logger.exception(message)


def log_database_operation(operation: str, model: str, success: bool, details: Dict[str, Any] = None, logger_name: str = None):
    """
    Log database operations with structured data.

    Args:
        operation: Type of operation (CREATE, READ, UPDATE, DELETE)
        model: Name of the model/table
        success: Whether the operation was successful
        details: Additional details about the operation
        logger_name: Name of the logger to use
    """
    extra_data = {
        "operation": operation,
        "model": model,
        "success": success,
        "details": details or {}
    }

    level = "INFO" if success else "ERROR"
    message = f"Database {operation} operation on {model} {'succeeded' if success else 'failed'}"

    PortfolioLogger.log_with_extra(level, message, extra_data, logger_name)


def log_api_request(method: str, endpoint: str, status_code: int, duration: float = None, user_id: str = None, logger_name: str = None):
    """
    Log API requests with structured data.

    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: HTTP status code
        duration: Request duration in milliseconds
        user_id: User ID if authenticated
        logger_name: Name of the logger to use
    """
    extra_data = {
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "duration_ms": duration,
        "user_id": user_id
    }

    level = "INFO" if status_code < 400 else "WARNING" if status_code < 500 else "ERROR"
    message = f"{method} {endpoint} - {status_code}"

    PortfolioLogger.log_with_extra(level, message, extra_data, logger_name)


def log_security_event(event_type: str, description: str, ip_address: str = None, user_id: str = None, severity: str = "INFO", logger_name: str = None):
    """
    Log security-related events.

    Args:
        event_type: Type of security event
        description: Event description
        ip_address: Client IP address
        user_id: User ID if available
        severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
        logger_name: Name of the logger to use
    """
    extra_data = {
        "event_type": event_type,
        "ip_address": ip_address,
        "user_id": user_id,
        "security_event": True
    }

    PortfolioLogger.log_with_extra(severity, description, extra_data, logger_name)


# Initialize the logger on import
_logger_instance = PortfolioLogger()
