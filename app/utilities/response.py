from flask import jsonify
from typing import Any, Dict, List, Optional, Union
from app.utilities.logger import get_logger, log_error, log_warning

logger = get_logger(__name__)


class APIResponse:
    """
    Utility class for creating consistent API responses
    """

    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
        """
        Create a successful API response.

        Args:
            data: The data to return
            message: Success message
            status_code: HTTP status code

        Returns:
            tuple: (response, status_code)
        """
        response = {
            "success": True,
            "message": message
        }

        if data is not None:
            response["data"] = data

        return jsonify(response), status_code

    @staticmethod
    def error(message: str = "An error occurred", errors: Optional[Dict] = None, status_code: int = 400) -> tuple:
        """
        Create an error API response.

        Args:
            message: Error message
            errors: Dictionary of field-specific errors
            status_code: HTTP status code

        Returns:
            tuple: (response, status_code)
        """
        response = {
            "success": False,
            "message": message
        }

        if errors:
            response["errors"] = errors

        return jsonify(response), status_code

    @staticmethod
    def not_found(message: str = "Resource not found") -> tuple:
        """
        Create a not found API response.

        Args:
            message: Not found message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.error(message=message, status_code=404)

    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> tuple:
        """
        Create an unauthorized API response.

        Args:
            message: Unauthorized message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.error(message=message, status_code=401)

    @staticmethod
    def forbidden(message: str = "Forbidden access") -> tuple:
        """
        Create a forbidden API response.

        Args:
            message: Forbidden message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.error(message=message, status_code=403)

    @staticmethod
    def validation_error(errors: Dict, message: str = "Validation failed") -> tuple:
        """
        Create a validation error API response.

        Args:
            errors: Dictionary of validation errors
            message: Validation error message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.error(message=message, errors=errors, status_code=422)

    @staticmethod
    def server_error(message: str = "Internal server error") -> tuple:
        """
        Create a server error API response.

        Args:
            message: Server error message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.error(message=message, status_code=500)

    @staticmethod
    def created(data: Any = None, message: str = "Resource created successfully") -> tuple:
        """
        Create a created API response.

        Args:
            data: The created resource data
            message: Success message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.success(data=data, message=message, status_code=201)

    @staticmethod
    def updated(data: Any = None, message: str = "Resource updated successfully") -> tuple:
        """
        Create an updated API response.

        Args:
            data: The updated resource data
            message: Success message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.success(data=data, message=message, status_code=200)

    @staticmethod
    def deleted(message: str = "Resource deleted successfully") -> tuple:
        """
        Create a deleted API response.

        Args:
            message: Success message

        Returns:
            tuple: (response, status_code)
        """
        return APIResponse.success(message=message, status_code=200)

    @staticmethod
    def paginated_response(
        data: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Success"
    ) -> tuple:
        """
        Create a paginated API response.

        Args:
            data: List of data items
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message

        Returns:
            tuple: (response, status_code)
        """
        total_pages = (total + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1

        response_data = {
            "items": data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }

        return APIResponse.success(data=response_data, message=message)
