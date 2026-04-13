from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.sales.domain.entities.sale import Sale
from modules.sales.domain.entities.sale_line import SaleLine
from modules.sales.domain.interfaces.repositories.i_sale_repository import (
    ISaleRepository,
)
from shared.domain.dtos.paginated_result import PaginatedResult
from shared.domain.interfaces.i_sale_reader import ISaleReader
from shared.infrastructure.database.read_tables import clients_table

SORT_FIELDS = {
    "sale_number": Sale.sale_number,
    "client_name": clients_table.c.name,
    "status": Sale.status,
    "sale_date": Sale.sale_date,
    "total": Sale.total,
    "created_at": Sale.created_at,
}


class SaleRepository(ISaleRepository, ISaleReader):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def generate_sale_number(self) -> str:
        year = datetime.now().year
        prefix = f"VEN-{year}-"
        result = await self._db.execute(
            text("SELECT MAX(sale_number) FROM sales WHERE sale_number LIKE :pattern"),
            {"pattern": f"{prefix}%"},
        )
        max_number = result.scalar_one_or_none()
        if max_number:
            seq = int(max_number.split("-")[-1]) + 1
        else:
            seq = 1
        return f"{prefix}{seq:04d}"

    async def create(
        self,
        sale_number: str,
        client_id: int,
        delivery_address: str,
        user_id: int,
        status: str,
        subtotal: Decimal,
        taxes: Decimal,
        total: Decimal,
        lines: list[dict],
    ) -> Sale:
        sale = Sale(
            sale_number=sale_number,
            client_id=client_id,
            delivery_address=delivery_address,
            user_id=user_id,
            status=status,
            subtotal=subtotal,
            taxes=taxes,
            total=total,
        )
        self._db.add(sale)
        await self._db.flush()

        for line in lines:
            sale_line = SaleLine(
                sale_id=sale.sale_id,
                product_id=line["product_id"],
                quantity=line["quantity"],
                unit_price=line["unit_price"],
                vat_rate=line["vat_rate"],
                line_subtotal=line["line_subtotal"],
                line_tax=line["line_tax"],
            )
            self._db.add(sale_line)

        await self._db.flush()
        await self._db.refresh(sale, ["lines"])
        return sale

    async def get_by_id(self, sale_id: int) -> Sale | None:
        result = await self._db.execute(
            select(Sale, clients_table.c.name.label("client_name"))
            .outerjoin(clients_table, Sale.client_id == clients_table.c.client_id)
            .where(Sale.sale_id == sale_id)
        )
        row = result.one_or_none()
        if row is None:
            return None

        sale, client_name = row
        setattr(sale, "client_name", client_name)
        return sale

    async def update(
        self,
        sale_id: int,
        client_id: int,
        delivery_address: str,
        subtotal: Decimal,
        taxes: Decimal,
        total: Decimal,
        lines: list[dict],
    ) -> Sale:
        result = await self._db.execute(select(Sale).where(Sale.sale_id == sale_id))
        sale = result.scalar_one()
        sale.client_id = client_id
        sale.delivery_address = delivery_address
        sale.subtotal = subtotal
        sale.taxes = taxes
        sale.total = total

        existing_lines_result = await self._db.execute(
            select(SaleLine).where(SaleLine.sale_id == sale_id)
        )
        for existing_line in existing_lines_result.scalars().all():
            await self._db.delete(existing_line)

        await self._db.flush()

        for line in lines:
            sale_line = SaleLine(
                sale_id=sale.sale_id,
                product_id=line["product_id"],
                quantity=line["quantity"],
                unit_price=line["unit_price"],
                vat_rate=line["vat_rate"],
                line_subtotal=line["line_subtotal"],
                line_tax=line["line_tax"],
            )
            self._db.add(sale_line)

        await self._db.flush()
        await self._db.refresh(sale, ["lines"])
        updated_sale = await self.get_by_id(sale_id)
        return updated_sale if updated_sale is not None else sale

    async def cancel(
        self,
        sale_id: int,
        cancelled_at: datetime,
        cancelled_by_user_id: int,
    ) -> Sale:
        result = await self._db.execute(select(Sale).where(Sale.sale_id == sale_id))
        sale = result.scalar_one()
        sale.status = "Cancelled"
        sale.cancelled_at = cancelled_at
        sale.cancelled_by_user_id = cancelled_by_user_id
        await self._db.flush()
        updated_sale = await self.get_by_id(sale_id)
        return updated_sale if updated_sale is not None else sale

    async def delete(self, sale_id: int) -> None:
        sale_result = await self._db.execute(
            select(Sale).where(Sale.sale_id == sale_id)
        )
        sale = sale_result.scalar_one()

        existing_lines_result = await self._db.execute(
            select(SaleLine).where(SaleLine.sale_id == sale_id)
        )
        for existing_line in existing_lines_result.scalars().all():
            await self._db.delete(existing_line)

        await self._db.delete(sale)
        await self._db.flush()

    async def get_all_paginated(
        self,
        page: int,
        page_size: int,
        sort_field: str,
        sort_order: str,
        status: str | None,
        client_id: int | None,
        date_from: datetime | None,
        date_to: datetime | None,
        search: str | None = None,
    ) -> PaginatedResult:
        filters = []
        if search:
            pattern = f"%{search}%"
            filters.append(
                Sale.sale_number.ilike(pattern) | clients_table.c.name.ilike(pattern)
            )
        if status:
            filters.append(Sale.status == status)
        if client_id:
            filters.append(Sale.client_id == client_id)
        if date_from:
            filters.append(Sale.sale_date >= date_from)
        if date_to:
            filters.append(Sale.sale_date <= date_to)

        count_stmt = (
            select(func.count())
            .select_from(Sale)
            .outerjoin(clients_table, Sale.client_id == clients_table.c.client_id)
            .where(*filters)
        )
        total_result = await self._db.execute(count_stmt)
        total = total_result.scalar_one()

        order_col = SORT_FIELDS.get(sort_field, Sale.created_at)
        order_expr = order_col.desc() if sort_order == "desc" else order_col.asc()
        offset = (page - 1) * page_size

        data_stmt = (
            select(Sale, clients_table.c.name.label("client_name"))
            .outerjoin(clients_table, Sale.client_id == clients_table.c.client_id)
            .where(*filters)
            .order_by(order_expr)
            .limit(page_size)
            .offset(offset)
        )

        result = await self._db.execute(data_stmt)
        items = list(result.all())

        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    async def has_sales_for_user(self, user_id: int) -> bool:
        result = await self._db.execute(
            select(func.count()).select_from(Sale).where(Sale.user_id == user_id)
        )
        return result.scalar_one() > 0
