from abc import ABC, abstractmethod


class ISupplierRepository(ABC):
    @abstractmethod
    async def get_existing_tax_ids(self, tax_ids: list[str]) -> set[str]:
        raise NotImplementedError

    @abstractmethod
    async def bulk_create(self, suppliers: list[dict]) -> int:
        raise NotImplementedError
