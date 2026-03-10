from dataclasses import dataclass


@dataclass
class ImportError:
    row: int
    reason: str


@dataclass
class ImportResult:
    total: int
    created: int
    errors: list[ImportError]
