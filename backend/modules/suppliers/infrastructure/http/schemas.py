from decimal import Decimal

from pydantic import BaseModel, Field


class ImportErrorDTO(BaseModel):
    row: int
    reason: str


class ImportResultDTO(BaseModel):
    total: int
    created: int
    errors: int
    error_detail: list[ImportErrorDTO]


class SupplierProductDTO(BaseModel):
    product_id: int
    supplier_price: Decimal


class SupplierDTO(BaseModel):
    supplier_id: int
    name: str
    tax_id: str
    city: str
    is_active: bool


class SupplierDetailDTO(SupplierDTO):
    address: str
    province: str
    postal_code: str
    phone: str
    email: str
    products: list[SupplierProductDTO]


class UpdateSupplierDTO(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    address: str | None = Field(None, min_length=1, max_length=300)
    city: str | None = Field(None, min_length=1, max_length=100)
    province: str | None = Field(None, min_length=1, max_length=100)
    postal_code: str | None = Field(None, min_length=1, max_length=10)
    phone: str | None = Field(None, min_length=1, max_length=20)
    email: str | None = Field(None, min_length=1, max_length=255)


class SetSupplierActiveDTO(BaseModel):
    is_active: bool
