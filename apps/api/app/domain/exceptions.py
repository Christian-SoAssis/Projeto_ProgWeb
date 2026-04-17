from typing import Any

class DomainError(Exception):
    """Base class for domain exceptions."""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.message = message
        self.details = details

class EntityNotFoundError(DomainError):
    """Raised when an entity is not found."""
    def __init__(self, entity_name: str, entity_id: Any):
        super().__init__(f"{entity_name} with id {entity_id} not found")

class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""
    pass

class UnauthorizedError(DomainError):
    """Raised when an action is not authorized."""
    pass
