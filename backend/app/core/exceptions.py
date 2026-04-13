"""
Custom exception classes for domain-specific errors.

Provides structured error responses with HTTP status codes.
"""

from typing import Any, Dict, Optional


class NovelAIForgeError(Exception):
    """Base exception for all application-specific errors."""
    
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class NotFoundError(NovelAIForgeError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: Any) -> None:
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404)


class ValidationError(NovelAIForgeError):
    """Raised when input data fails validation."""
    
    def __init__(self, message: str, field_errors: Optional[Dict] = None) -> None:
        super().__init__(message=message, status_code=422, details=field_errors)


class AuthenticationError(NovelAIForgeError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message, status_code=401)


class AuthorizationError(NovelAIForgeError):
    """Raised when user lacks permission for an action."""
    
    def __init__(self, action: str) -> None:
        message = f"Insufficient permissions to perform: {action}"
        super().__init__(message=message, status_code=403)


class AIProviderError(NovelAIForgeError):
    """Raised when AI generation fails."""
    
    def __init__(
        self,
        provider: str,
        message: str = "AI provider request failed",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message=message, status_code=502)
        self.provider = provider
        self.original_error = original_error
        self.details["provider"] = provider


class PromptTemplateError(NovelAIForgeError):
    """Raised when prompt template is missing or invalid."""
    
    def __init__(self, template_name: str, reason: str = "not found") -> None:
        message = f"Prompt template '{template_name}' {reason}"
        super().__init__(message=message, status_code=500)
        self.template_name = template_name
