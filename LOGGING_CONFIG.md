# Logging Configuration Guide

This document explains how to configure and use the centralized logging utility in the Portfolio Flask application.

## Overview

The logging utility provides:
- Centralized configuration
- Multiple output formats (simple, detailed, JSON)
- File rotation
- Structured logging with extra data
- Easy-to-use convenience functions
- Request/response logging middleware
- Security event logging

## Environment Variables

Add these variables to your `.env` file to configure logging:

```bash
# Logging Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=detailed               # simple, detailed, json
LOG_TO_FILE=true                 # Enable/disable file logging
LOG_TO_CONSOLE=true              # Enable/disable console logging
LOG_FILE_PATH=logs               # Directory for log files
LOG_FILE_NAME=portfolio.log      # Log file name
LOG_MAX_BYTES=10485760           # Max file size before rotation (10MB)
LOG_BACKUP_COUNT=5               # Number of backup files to keep
APP_NAME=Portfolio               # Application name for JSON logs
```

## Basic Usage

### Import and Use Logger

```python
# Method 1: Get a logger instance
from app.utilities.logger import get_logger

logger = get_logger(__name__)
logger.info("This is an info message")
logger.error("This is an error message")

# Method 2: Use convenience functions
from app.utilities.logger import log_info, log_error, log_debug

log_info("Application started")
log_error("Something went wrong")
log_debug("Debug information")
```

### Structured Logging with Extra Data

```python
from app.utilities.logger import log_info, log_error

# Log with extra structured data
log_info("User login successful", {
    "user_id": "12345",
    "ip_address": "192.168.1.1",
    "login_method": "password"
})

log_error("Database connection failed", {
    "database": "mysql",
    "host": "localhost",
    "error_code": "2003"
})
```

### Database Operation Logging

```python
from app.utilities.logger import log_database_operation

# Automatically used in BaseModel, but can be used elsewhere
log_database_operation(
    operation="CREATE",
    model="User",
    success=True,
    details={"user_id": "12345", "email": "user@example.com"}
)
```

### API Request Logging

```python
from app.utilities.logger import log_api_request

log_api_request(
    method="POST",
    endpoint="/api/users",
    status_code=201,
    duration=245.5,  # milliseconds
    user_id="12345"
)
```

### Security Event Logging

```python
from app.utilities.logger import log_security_event

log_security_event(
    event_type="LOGIN_ATTEMPT",
    description="Failed login attempt for user@example.com",
    ip_address="192.168.1.100",
    user_id="12345",
    severity="WARNING"
)
```

### Exception Logging

```python
from app.utilities.logger import log_exception

try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    log_exception("Risky operation failed", {
        "operation": "data_processing",
        "input_data": "sample_data"
    })
    raise  # Re-raise if needed
```

## Middleware and Decorators

### Automatic Request Logging

```python
from app.utilities.logging_middleware import setup_request_logging

# In your app factory
def create_app():
    app = Flask(__name__)

    # Setup automatic request/response logging
    setup_request_logging(app)

    return app
```

### Route-Level Logging Decorators

```python
from app.utilities.logging_middleware import log_requests, log_auth_events, log_sensitive_operations

@bp.route('/api/users')
@log_requests  # Automatically logs request/response details
def get_users():
    return jsonify(users)

@bp.route('/api/login', methods=['POST'])
@log_auth_events  # Logs authentication events
def login():
    # Login logic
    return response

@bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@log_sensitive_operations('DELETE_USER')  # Logs sensitive operations
def delete_user(user_id):
    # Deletion logic
    return response
```

## Log Formats

### Simple Format
```
INFO - Application started successfully
ERROR - Database connection failed
```

### Detailed Format
```
2023-12-07 10:30:45,123 - app.models.user - INFO - create_user:45 - User created successfully
2023-12-07 10:30:46,456 - app.routes.auth - ERROR - login:78 - Authentication failed
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

## Log Files

### File Structure
```
logs/
├── portfolio.log          # Current log file
├── portfolio.log.1        # First backup
├── portfolio.log.2        # Second backup
└── ...                    # Up to LOG_BACKUP_COUNT files
```

### Log Rotation
- Files rotate when they reach `LOG_MAX_BYTES` size
- Keeps `LOG_BACKUP_COUNT` backup files
- Oldest backups are deleted automatically

## Best Practices

### 1. Use Appropriate Log Levels
- `DEBUG`: Detailed diagnostic information
- `INFO`: General information about application flow
- `WARNING`: Something unexpected happened, but app continues
- `ERROR`: Serious problem occurred
- `CRITICAL`: Very serious error occurred

### 2. Include Relevant Context
```python
# Good - includes context
log_info("User profile updated", {
    "user_id": user.id,
    "updated_fields": ["name", "email"],
    "updated_by": current_user.id
})

# Poor - lacks context
log_info("Profile updated")
```

### 3. Don't Log Sensitive Information
```python
# Good - logs without sensitive data
log_info("User authentication attempt", {
    "user_id": user.id,
    "ip_address": request.remote_addr,
    "success": True
})

# Bad - logs password
log_info("User login", {
    "email": user.email,
    "password": user.password,  # DON'T DO THIS
    "success": True
})
```

### 4. Use Structured Logging
```python
# Good - structured data
log_error("Payment processing failed", {
    "payment_id": "pay_123",
    "amount": 99.99,
    "currency": "USD",
    "error_code": "CARD_DECLINED"
})

# Poor - unstructured message
log_error(f"Payment pay_123 for $99.99 USD failed with error CARD_DECLINED")
```

## Migration from Standard Logging

### Before (Standard Logging)
```python
import logging

logger = logging.getLogger(__name__)

def create_user(data):
    try:
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        logger.info(f"User {user.id} created successfully")
        return user
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise
```

### After (Portfolio Logger)
```python
from app.utilities.logger import get_logger, log_database_operation, log_exception

logger = get_logger(__name__)

def create_user(data):
    try:
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        log_database_operation("CREATE", "User", True, {
            "user_id": user.id,
            "email": user.email
        })
        return user
    except Exception as e:
        log_database_operation("CREATE", "User", False, {
            "error": str(e),
            "input_data": data
        })
        log_exception("User creation failed", {
            "attempted_data": data
        })
        raise
```

## Monitoring and Alerts

### Log Analysis
- Use log aggregation tools like ELK Stack, Splunk, or cloud logging services
- JSON format is ideal for log parsing and analysis
- Set up alerts for ERROR and CRITICAL level logs

### Performance Monitoring
- Track request duration using the middleware
- Monitor database operation success rates
- Set up alerts for high error rates

### Security Monitoring
- Monitor authentication failures
- Track suspicious IP addresses
- Alert on security events

## Troubleshooting

### Common Issues

1. **Logs not appearing in files**
   - Check `LOG_TO_FILE=true` in environment
   - Verify log directory permissions
   - Ensure disk space is available

2. **Logs not appearing in console**
   - Check `LOG_TO_CONSOLE=true` in environment
   - Verify `LOG_LEVEL` is appropriate

3. **Log file not rotating**
   - Check `LOG_MAX_BYTES` setting
   - Verify file permissions for rotation

4. **JSON format errors**
   - Ensure extra data is JSON serializable
   - Avoid circular references in extra data

### Debug Logging Configuration
```python
from app.utilities.logger import get_logger

# Enable debug logging for the logger itself
debug_logger = get_logger('app.utilities.logger')
debug_logger.setLevel('DEBUG')
```
