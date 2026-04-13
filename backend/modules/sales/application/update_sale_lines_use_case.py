from decimal import Decimal

from modules.sales.domain.entities.sale import Sale
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from modules.sales.domain.interfaces.repositories.i_sale_repository import (
    ISaleRepository,
)
from modules.sales.domain.interfaces.use_cases.i_update_sale_lines_use_case import (
    IUpdateSaleLinesUseCase,
)
from shared.domain.interfaces.i_product_reader import IProductReader
from shared.domain.interfaces.i_product_stock_updater import IProductStockUpdater


class UpdateSaleLinesUseCase(IUpdateSaleLinesUseCase):
    def __init__(
        self,
        sale_repo: ISaleRepository,
        product_reader: IProductReader,
        stock_updater: IProductStockUpdater,
    ) -> None:
        self._sale_repo = sale_repo
        self._product_reader = product_reader
        self._stock_updater = stock_updater

    async def execute(self, sale_id: int, lines: list[dict]) -> Sale:
        sale = await self._sale_repo.get_by_id(sale_id)
        if sale is None:
            raise SaleException(SaleExceptionInfo.SALE_NOT_FOUND)
        if sale.status != "Pending":
            raise SaleException(SaleExceptionInfo.SALE_NOT_PENDING)
        if not lines:
            raise SaleException(SaleExceptionInfo.EMPTY_SALE_LINES)

        # Restore stock for all existing lines
        for old_line in sale.lines:
            product = await self._product_reader.get_by_id(old_line.product_id)
            if product is not None:
                await self._stock_updater.update_stock_current(
                    old_line.product_id,
                    product.stock_current + old_line.quantity,
                )

        # Validate and process new lines
        processed_lines: list[dict] = []
        subtotal = Decimal("0")

        for line in lines:
            product = await self._product_reader.get_by_id(line["product_id"])
            if product is None:
                raise SaleException(SaleExceptionInfo.PRODUCT_NOT_FOUND)
            if not product.is_active:
                raise SaleException(SaleExceptionInfo.PRODUCT_NOT_ACTIVE)
            if product.stock_current < line["quantity"]:
                raise SaleException(SaleExceptionInfo.INSUFFICIENT_STOCK)

            quantity = line["quantity"]
            unit_price = Decimal(str(product.price))
            vat_rate = product.vat_rate
            discount = Decimal(str(line.get("discount", "0")))
            gross = quantity * unit_price
            if discount < Decimal("0") or discount > gross:
                raise SaleException(SaleExceptionInfo.INVALID_DISCOUNT)
            line_subtotal = gross - discount
            line_tax = line_subtotal * vat_rate
            subtotal += line_subtotal

            processed_lines.append(
                {
                    "product_id": line["product_id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount": discount,
                    "vat_rate": vat_rate,
                    "line_subtotal": line_subtotal,
                    "line_tax": line_tax,
                }
            )

        # Deduct stock for new lines
        for line, processed in zip(lines, processed_lines):
            product = await self._product_reader.get_by_id(line["product_id"])
            if product is not None:
                await self._stock_updater.update_stock_current(
                    line["product_id"],
                    product.stock_current - processed["quantity"],
                )

        taxes = sum(pl["line_tax"] for pl in processed_lines)
        total = subtotal + taxes

        await self._sale_repo.replace_lines(sale_id, processed_lines)
        return await self._sale_repo.update_totals(sale_id, subtotal, taxes, total)
