from __future__ import annotations


class ProcurementError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DataLoadError(ProcurementError):
    pass


class PolicyViolationError(ProcurementError):
    pass


class VendorServiceError(ProcurementError):
    pass


class LedgerError(ProcurementError):
    pass


class ModelInferenceError(ProcurementError):
    pass
