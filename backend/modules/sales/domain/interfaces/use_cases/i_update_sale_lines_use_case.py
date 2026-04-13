from abc import ABC, abstractmethod

from modules.sales.domain.entities.sale import Sale


class IUpdateSaleLinesUseCase(ABC):
    @abstractmethod
    async def execute(self, sale_id: int, lines: list[dict]) -> Sale: ...
