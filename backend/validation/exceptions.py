class ValidationError(Exception):
    """Base validation error."""
    def __init__(self, message, code="VALIDATION_ERROR", details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class LifecycleViolationException(ValidationError):
    """Exception raised when an invalid entity lifecycle transition is attempted."""
    def __init__(self, message, details=None):
        super().__init__(message, code="LIFECYCLE_VIOLATION", details=details)


class MaterialReconciliationException(ValidationError):
    """Exception raised when material consumption violates BOM or lot availability."""
    def __init__(self, message, details=None):
        super().__init__(message, code="MATERIAL_RECONCILIATION_ERROR", details=details)


class QuantityValidationException(ValidationError):
    """Exception raised when defect or inspection quantities are mathematically invalid."""
    def __init__(self, message, details=None):
        super().__init__(message, code="QUANTITY_VALIDATION_ERROR", details=details)


class TraceabilityBrokenException(ValidationError):
    """Exception raised when an upstream or downstream traceability link is missing."""
    def __init__(self, message, details=None):
        super().__init__(message, code="TRACEABILITY_BROKEN", details=details)
