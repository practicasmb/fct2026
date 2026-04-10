from collections import defaultdict

from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from modules.sales.domain.interfaces.repositories.i_sale_repository import (
    ISaleRepository,
)
from modules.sales.domain.interfaces.use_cases.i_delete_sale_use_case import (
    IDeleteSaleUseCase,
)
from shared.domain.interfaces.i_product_reader import IProductReader
from shared.domain.interfaces.i_product_stock_updater import IProductStockUpdater


class DeleteSaleUseCase(IDeleteSaleUseCase):
    def __init__(
        self,
        sale_repo: ISaleRepository,
        product_reader: IProductReader,
        stock_updater: IProductStockUpdater,
    ) -> None:
        self._sale_repo = sale_repo
        self._product_reader = product_reader
        self._stock_updater = stock_updater

    async def execute(self, sale_id: int) -> None:
        sale = await self._sale_repo.get_by_id(sale_id)
        if sale is None:
            raise SaleException(SaleExceptionInfo.SALE_NOT_FOUND)
        if sale.status != "Pending":
            raise SaleException(SaleExceptionInfo.SALE_NOT_DELETABLE)

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

        await self._sale_repo.delete(sale_id)
