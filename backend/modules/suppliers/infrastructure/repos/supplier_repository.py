from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.suppliers.domain.entities.supplier import Supplier
from modules.suppliers.domain.interfaces.repositories.i_supplier_repository import (
    ISupplierRepository,
)


class SupplierRepository(ISupplierRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_existing_tax_ids(self, tax_ids: list[str]) -> set[str]:
        result = await self._db.execute(
            select(Supplier.tax_id).where(Supplier.tax_id.in_(tax_ids))
        )
        return set(result.scalars().all())

    async def bulk_create(self, suppliers: list[dict]) -> int:
        objects = [Supplier(**data) for data in suppliers]
        self._db.add_all(objects)
        await self._db.flush()
        return len(objects)
