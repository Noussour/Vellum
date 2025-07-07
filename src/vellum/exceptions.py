from typing import Any

class VellumError(Exception):
    pass

class DocumentNotFoundError(VellumError):
    def __init__(self, doc_id: Any):
        super().__init__(f"Document with ID '{doc_id}' not found.")

class OptimisticLockError(VellumError):
    def __init__(self, doc_id: Any, version: int):
        super().__init__(
            f"Update failed for document ID '{doc_id}'. "
            f"Version {version} is stale."
        )