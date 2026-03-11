from sqlalchemy.ext.asyncio import AsyncSession

from modules.suppliers.infrastructure.repos.supplier_repository import (
    SupplierRepository,
)


async def test_get_existing_tax_ids_empty(db_session: AsyncSession):
    repo = SupplierRepository(db_session)
    result = await repo.get_existing_tax_ids(["B12345674", "A98765432"])
    assert result == set()


async def test_get_existing_tax_ids_returns_matches(db_session: AsyncSession):
    repo = SupplierRepository(db_session)
    await repo.bulk_create([
        {"name": "Proveedor A", "tax_id": "B12345674", "address": "Calle 1", "city": "Madrid", "province": "Madrid", "postal_code": "28001", "phone": "910000000", "email": "a@test.com"},
    ])
    result = await repo.get_existing_tax_ids(["B12345674", "A00000000"])
    assert result == {"B12345674"}


async def test_bulk_create_returns_count(db_session: AsyncSession):
    repo = SupplierRepository(db_session)
    suppliers = [
        {"name": "Proveedor A", "tax_id": "B11111111", "address": "Calle 1", "city": "Madrid", "province": "Madrid", "postal_code": "28001", "phone": "910000001", "email": "a@test.com"},
        {"name": "Proveedor B", "tax_id": "B22222222", "address": "Calle 2", "city": "Barcelona", "province": "Barcelona", "postal_code": "08001", "phone": "930000001", "email": "b@test.com"},
    ]
    count = await repo.bulk_create(suppliers)
    assert count == 2


async def test_bulk_create_skips_duplicate_tax_ids(db_session: AsyncSession):
    repo = SupplierRepository(db_session)
    data = {"name": "Proveedor A", "tax_id": "B33333333", "address": "Calle 1", "city": "Madrid", "province": "Madrid", "postal_code": "28001", "phone": "910000002", "email": "a@test.com"}
    await repo.bulk_create([data])
    existing = await repo.get_existing_tax_ids(["B33333333"])
    assert "B33333333" in existing
