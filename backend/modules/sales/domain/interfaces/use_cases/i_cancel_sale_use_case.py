from abc import ABC, abstractmethod

from modules.sales.domain.entities.sale import Sale


class ICancelSaleUseCase(ABC):
    @abstractmethod
    async def execute(self, sale_id: int, user_id: int) -> Sale: ...
