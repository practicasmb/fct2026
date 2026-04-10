from collections import defaultdict
from datetime import UTC, datetime

from modules.sales.domain.entities.sale import Sale
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from modules.sales.domain.interfaces.repositories.i_sale_repository import (
    ISaleRepository,
)
from modules.sales.domain.interfaces.use_cases.i_cancel_sale_use_case import (
    ICancelSaleUseCase,
)
from shared.domain.interfaces.i_product_reader import IProductReader
from shared.domain.interfaces.i_product_stock_updater import IProductStockUpdater


class CancelSaleUseCase(ICancelSaleUseCase):
    def __init__(
        self,
        sale_repo: ISaleRepository,
        product_reader: IProductReader,
        stock_updater: IProductStockUpdater,
    ) -> None:
        self._sale_repo = sale_repo
        self._product_reader = product_reader
        self._stock_updater = stock_updater

    async def execute(self, sale_id: int, user_id: int) -> Sale:
        sale = await self._sale_repo.get_by_id(sale_id)
        if sale is None:
            raise SaleException(SaleExceptionInfo.SALE_NOT_FOUND)
        if sale.status not in {"Pending", "Approved"}:
            raise SaleException(SaleExceptionInfo.SALE_NOT_CANCELLABLE)

        qty_by_product: dict[int, int] = defaultdict(int)
        for line in sale.lines:
            qty_by_product[line.product_id] += line.quantity

        for product_id, quantity in qty_by_product.items():
            product = await self._product_reader.get_by_id(product_id)
            if product is None:
                raise SaleException(SaleExceptionInfo.PRODUCT_NOT_FOUND)
            await self._stock_updater.update_stock_current(
                product_id, product.stock_current + quantity
            )

        return await self._sale_repo.cancel(
            sale_id=sale_id,
            cancelled_at=datetime.now(UTC),
            cancelled_by_user_id=user_id,
        )
