from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, errors: Dict[str, List[str]]):
        self.errors = errors
        super().__init__(str(errors))


class Validator:
    """
    Utility class for validating request data
    """

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.errors = {}

    def required(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field is present and not empty.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field not in self.data or self.data[field] is None or str(self.data[field]).strip() == '':
            error_msg = message or f"{field} is required"
            self._add_error(field, error_msg)
        return self

    def email(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field contains a valid email address.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field]:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(self.data[field])):
                error_msg = message or f"{field} must be a valid email address"
                self._add_error(field, error_msg)
        return self

    def min_length(self, field: str, min_len: int, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field has minimum length.

        Args:
            field: Field name to validate
            min_len: Minimum length required
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            if len(str(self.data[field])) < min_len:
                error_msg = message or f"{field} must be at least {min_len} characters long"
                self._add_error(field, error_msg)
        return self

    def max_length(self, field: str, max_len: int, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field has maximum length.

        Args:
            field: Field name to validate
            max_len: Maximum length allowed
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            if len(str(self.data[field])) > max_len:
                error_msg = message or f"{field} must not exceed {max_len} characters"
                self._add_error(field, error_msg)
        return self

    def phone(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field contains a valid phone number.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field]:
            # Basic phone validation - allows digits, spaces, hyphens, parentheses, plus sign
            phone_pattern = r'^[\+]?[\d\s\-\(\)]{10,20}$'
            if not re.match(phone_pattern, str(self.data[field])):
                error_msg = message or f"{field} must be a valid phone number"
                self._add_error(field, error_msg)
        return self

    def url(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field contains a valid URL.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field]:
            url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
            if not re.match(url_pattern, str(self.data[field])):
                error_msg = message or f"{field} must be a valid URL"
                self._add_error(field, error_msg)
        return self

    def string(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field is a string.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            if not isinstance(self.data[field], str):
                error_msg = message or f"{field} must be a string"
                self._add_error(field, error_msg)
        return self

    def integer(self, field: str, message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field is an integer.

        Args:
            field: Field name to validate
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            try:
                int(self.data[field])
            except (ValueError, TypeError):
                error_msg = message or f"{field} must be an integer"
                self._add_error(field, error_msg)
        return self

    def in_list(self, field: str, valid_values: List[Any], message: Optional[str] = None) -> 'Validator':
        """
        Validate that a field's value is in a list of valid values.

        Args:
            field: Field name to validate
            valid_values: List of valid values
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            if self.data[field] not in valid_values:
                error_msg = message or f"{field} must be one of: {', '.join(map(str, valid_values))}"
                self._add_error(field, error_msg)
        return self

    def custom(self, field: str, validator_func, message: Optional[str] = None) -> 'Validator':
        """
        Apply a custom validation function to a field.

        Args:
            field: Field name to validate
            validator_func: Function that takes the field value and returns True if valid
            message: Custom error message

        Returns:
            self: For method chaining
        """
        if field in self.data and self.data[field] is not None:
            try:
                if not validator_func(self.data[field]):
                    error_msg = message or f"{field} is not valid"
                    self._add_error(field, error_msg)
            except Exception:
                error_msg = message or f"{field} validation failed"
                self._add_error(field, error_msg)
        return self

    def _add_error(self, field: str, message: str):
        """
        Add an error message for a field.

        Args:
            field: Field name
            message: Error message
        """
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)

    def validate(self) -> bool:
        """
        Check if validation passed.

        Returns:
            bool: True if no errors, False otherwise
        """
        return len(self.errors) == 0

    def get_errors(self) -> Dict[str, List[str]]:
        """
        Get all validation errors.

        Returns:
            dict: Dictionary of field errors
        """
        return self.errors

    def raise_if_invalid(self):
        """
        Raise ValidationError if validation failed.

        Raises:
            ValidationError: If validation errors exist
        """
        if not self.validate():
            raise ValidationError(self.errors)


def validate_about_data(data: Dict[str, Any]) -> Validator:
    """
    Validate about data with specific rules.

    Args:
        data: Dictionary of data to validate

    Returns:
        Validator: Validator instance with results
    """
    validator = Validator(data)

    validator.required('Email').email('Email')
    validator.required('City').string('City').max_length('City', 100)
    validator.required('Current Company').string('Current Company').max_length('Current Company', 150)
    validator.required('Current Designation').string('Current Designation').max_length('Current Designation', 100)
    validator.required('Degree').string('Degree').max_length('Degree', 100)
    validator.required('Description').string('Description')
    validator.required('Phone').phone('Phone').max_length('Phone', 20)
    validator.required('Self Facts').string('Self Facts')
    validator.required('Short Description').string('Short Description')
    validator.required('Summary').string('Summary')
    validator.required('Website').string('Website').max_length('Website', 50)

    return validator


def validate_contact_payload(data: Dict[str, Any]) -> Validator:
    """
    Validate contact form data.
    """
    validator = Validator(data)
    validator.required('Name').string('Name').min_length('Name', 2).max_length('Name', 100)
    validator.required('Email').email('Email').max_length('Email', 120)
    validator.required('Company').string('Company').max_length('Company', 150)
    validator.required('Designation').string('Designation').max_length('Designation', 200)
    validator.required('Message').string('Message').min_length('Message', 10).max_length('Message', 1000)
    return validator


def validate_testimonial_payload(data: Dict[str, Any]) -> Validator:
    """
    Validate testimonial form data.
    """
    validator = Validator(data)
    validator.required('Name').string('Name').min_length('Name', 2).max_length('Name', 100)
    validator.required('Email').email('Email').max_length('Email', 120)
    if 'Company' in data and data['Company']:
        validator.string('Company').max_length('Company', 150)
    validator.required('Designation').string('Designation').max_length('Designation', 200)
    validator.required('Message').string('Message').min_length('Message', 10).max_length('Message', 1000)
    return validator

