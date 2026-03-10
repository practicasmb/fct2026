from pydantic import BaseModel


class ImportErrorDTO(BaseModel):
    row: int
    reason: str


class ImportResultDTO(BaseModel):
    total: int
    created: int
    errors: int
    error_detail: list[ImportErrorDTO]
