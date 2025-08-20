# Portfolio Flask Application - Logging Utility

## Overview

This document describes the centralized logging utility that has been implemented for the Portfolio Flask application. The logging system provides structured, configurable, and production-ready logging capabilities.

## Features

- **Centralized Configuration**: Single point of configuration for all logging settings
- **Multiple Output Formats**: Simple, detailed, and JSON formats
- **File Rotation**: Automatic log file rotation with configurable size limits
- **Structured Logging**: Support for extra metadata and structured data
- **Request/Response Logging**: Automatic API request and response logging
- **Security Event Logging**: Specialized logging for security-related events
- **Database Operation Logging**: Structured logging for database operations
- **Easy Integration**: Simple import and usage throughout the application

## Quick Start

### Basic Usage

```python
# Import the logger
from app.utilities.logger import get_logger

# Create a logger instance
logger = get_logger(__name__)

# Use it like any standard logger
logger.info("Application started")
logger.error("Something went wrong")
logger.debug("Debug information")
```

### Convenience Functions

```python
# Import convenience functions for quick logging
from app.utilities.logger import log_info, log_error, log_debug, log_warning, log_critical

log_info("User logged in successfully")
log_error("Database connection failed")
log_debug("Processing user data")
```

### Structured Logging with Extra Data

```python
from app.utilities.logger import log_info, log_error

# Log with structured data
log_info("User operation completed", {
    "user_id": "12345",
    "operation": "profile_update",
    "duration_ms": 245
})

log_error("Payment failed", {
    "payment_id": "pay_123",
    "amount": 99.99,
    "error_code": "CARD_DECLINED"
})
```

## Configuration

Configure logging through environment variables in your `.env` file:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Output format (simple, detailed, json)
LOG_FORMAT=detailed

# Enable/disable file logging
LOG_TO_FILE=true

# Enable/disable console logging
LOG_TO_CONSOLE=true

# Log file settings
LOG_FILE_PATH=logs
LOG_FILE_NAME=portfolio.log

# File rotation settings
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Application name (used in JSON logs)
APP_NAME=Portfolio
```

## Specialized Logging Functions

### Database Operations

```python
from app.utilities.logger import log_database_operation

log_database_operation(
    operation="CREATE",
    model="User",
    success=True,
    details={"user_id": "12345", "email": "user@example.com"}
)
```

### API Requests

```python
from app.utilities.logger import log_api_request

log_api_request(
    method="POST",
    endpoint="/api/users",
    status_code=201,
    duration=245.5,
    user_id="12345"
)
```

### Security Events

```python
from app.utilities.logger import log_security_event

log_security_event(
    event_type="LOGIN_FAILURE",
    description="Failed login attempt",
    ip_address="192.168.1.100",
    user_id="user123",
    severity="WARNING"
)
```

### Exception Logging

```python
from app.utilities.logger import log_exception

try:
    # Some risky operation
    result = process_data()
except Exception as e:
    log_exception("Data processing failed", {
        "input_size": len(data),
        "error_type": type(e).__name__
    })
    raise
```

## Middleware Integration

The application automatically includes request logging middleware. To enable it in your Flask app:

```python
from app.utilities.logging_middleware import setup_request_logging

def create_app():
    app = Flask(__name__)

    # This is already included in app/__init__.py
    setup_request_logging(app)

    return app
```

## Log Formats

### Simple Format
```
INFO - User logged in successfully
ERROR - Database connection failed
```

### Detailed Format
```
2023-12-07 10:30:45,123 - app.models.user - INFO - create_user:45 - User created successfully
2023-12-07 10:31:15,456 - app.routes.auth - ERROR - authenticate:78 - Authentication failed
```

### JSON Format
```json
{
  "timestamp": "2023-12-07T10:30:45.123456",
  "application": "Portfolio",
  "level": "INFO",
  "logger": "app.models.user",
  "message": "User created successfully",
  "module": "user",
  "function": "create_user",
  "line": 45,
  "extra": {
    "user_id": "12345",
    "operation": "CREATE"
  }
}
```

## File Structure

After setup, your log files will be organized as:

```
logs/
├── portfolio.log          # Current active log file
├── portfolio.log.1        # Most recent backup
├── portfolio.log.2        # Second backup
├── ...
└── portfolio.log.5        # Oldest backup (if LOG_BACKUP_COUNT=5)
```

## Migration Guide

If you have existing code using standard Python logging, here's how to migrate:

### Before (Standard Logging)
```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.info("Operation completed")
    logger.error(f"Error occurred: {error_message}")
```

### After (Portfolio Logger)
```python
from app.utilities.logger import get_logger

logger = get_logger(__name__)

def some_function():
    logger.info("Operation completed")
    logger.error("Error occurred", extra={
        "error_message": error_message,
        "operation": "some_function"
    })
```

## Best Practices

1. **Use appropriate log levels**:
   - DEBUG: Detailed diagnostic information
   - INFO: General information about program execution
   - WARNING: Something unexpected happened but the app continues
   - ERROR: A serious problem occurred
   - CRITICAL: A very serious error occurred

2. **Include relevant context**:
   ```python
   # Good
   log_info("User profile updated", {
       "user_id": user.id,
       "fields_updated": ["name", "email"],
       "updated_by": current_user.id
   })

   # Not as useful
   log_info("Profile updated")
   ```

3. **Don't log sensitive information**:
   ```python
   # Good
   log_info("Login attempt", {
       "user_id": user.id,
       "success": True
   })

   # Bad - contains password
   log_info("Login attempt", {
       "email": email,
       "password": password  # DON'T DO THIS
   })
   ```

4. **Use structured data for better analysis**:
   ```python
   # Good - structured
   log_error("Payment failed", {
       "payment_id": "pay_123",
       "amount": 99.99,
       "error_code": "CARD_DECLINED"
   })

   # Less useful - unstructured
   log_error("Payment pay_123 for $99.99 failed: CARD_DECLINED")
   ```

## Integration in Models

The `BaseModel` class has been updated to use the new logging system. All database operations are automatically logged with structured data:

```python
# This is already implemented in app/models/base.py
class MyModel(BaseModel):
    # All CRUD operations are automatically logged
    def save(self):
        # Logs database operation with success/failure details
        return super().save()
```

## Monitoring and Troubleshooting

### Common Issues

1. **Logs not appearing**: Check environment variables and file permissions
2. **File not rotating**: Verify LOG_MAX_BYTES and write permissions
3. **JSON format errors**: Ensure all extra data is JSON serializable

### Log Analysis

The JSON format is ideal for log aggregation tools like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Cloud logging services (AWS CloudWatch, Google Cloud Logging, etc.)

## Performance Considerations

- Logging is asynchronous where possible
- File rotation prevents disk space issues
- Structured logging adds minimal overhead
- Debug logging can be disabled in production

## Security

- No sensitive information is logged by default
- Security events are tracked separately
- Request logging excludes sensitive headers and data
- IP addresses and user IDs are logged for audit trails

This logging utility provides a robust foundation for monitoring, debugging, and maintaining your Portfolio Flask application in development and production environments.
