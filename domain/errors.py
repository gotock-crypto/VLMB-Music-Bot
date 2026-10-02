"""Stable domain/application error taxonomy."""
class DomainError(Exception):
    """Base error for domain-level failures."""
class InvalidTransition(DomainError):
    """An event is not valid from the current state."""
class UnknownCallback(DomainError):
    """Callback prefix is not registered."""
class ProviderDomainError(DomainError):
    """Provider operation failed at the domain boundary."""
