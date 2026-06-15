from __future__ import annotations

"""Application-specific exception hierarchy."""

from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str = "Application error",
        *,
        status_code: int = 500,
        error_code: str = "application_error",
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Serialize the exception for API responses."""
        payload: dict[str, Any] = {
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details is not None:
            payload["error"]["details"] = self.details
        return payload


class NotFoundException(AppException):
    """Raised when a requested resource cannot be found."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=404,
            error_code="not_found",
            details=details,
        )


class UnauthorizedException(AppException):
    """Raised when authentication fails or is missing."""

    def __init__(
        self,
        message: str = "Authentication required",
        *,
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=401,
            error_code="unauthorized",
            details=details,
        )


class ForbiddenException(AppException):
    """Raised when an authenticated user lacks sufficient permissions."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        *,
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=403,
            error_code="forbidden",
            details=details,
        )


class ValidationException(AppException):
    """Raised when application-level validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        *,
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=422,
            error_code="validation_error",
            details=details,
        )


class AIServiceException(AppException):
    """Raised when external AI providers fail or return invalid data."""

    def __init__(
        self,
        message: str = "AI service request failed",
        *,
        details: dict[str, Any] | list[Any] | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=502,
            error_code="ai_service_error",
            details=details,
        )
