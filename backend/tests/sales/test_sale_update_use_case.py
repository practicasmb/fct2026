from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from modules.sales.application.update_sale_use_case import UpdateSaleUseCase
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale, make_sale_line


@pytest.mark.asyncio
async def test_update_sale_recalculates_totals_and_updates_stock():
    repo = AsyncMock()
    client_reader = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = UpdateSaleUseCase(repo, client_reader, product_reader, stock_updater)

    existing_sale = make_sale(
        status="Pending",
        lines=[make_sale_line(product_id=10, quantity=2)],
    )
    repo.get_by_id.return_value = existing_sale
    client_reader.get_by_id.return_value = MagicMock(is_active=True)

    product_10 = MagicMock(
        is_active=True,
        price=Decimal("50.00"),
        vat_rate=Decimal("0.21"),
        stock_current=8,
    )
    product_11 = MagicMock(
        is_active=True,
        price=Decimal("20.00"),
        vat_rate=Decimal("0.10"),
        stock_current=4,
    )

    async def get_product(product_id: int):
        return {10: product_10, 11: product_11}.get(product_id)

    product_reader.get_by_id.side_effect = get_product
    updated_sale = make_sale(
        client_id=6,
        subtotal=Decimal("90.00"),
        taxes=Decimal("14.50"),
        total=Decimal("104.50"),
        lines=[
            make_sale_line(
                product_id=10,
                quantity=1,
                unit_price=Decimal("50.00"),
                line_subtotal=Decimal("50.00"),
                vat_rate=Decimal("0.21"),
                line_tax=Decimal("10.50"),
            ),
            make_sale_line(
                sale_line_id=2,
                product_id=11,
                quantity=2,
                unit_price=Decimal("20.00"),
                line_subtotal=Decimal("40.00"),
                vat_rate=Decimal("0.10"),
                line_tax=Decimal("4.00"),
            ),
        ],
    )
    repo.update.return_value = updated_sale

    result = await use_case.execute(
        sale_id=1,
        client_id=6,
        delivery_address="New Address 123",
        lines=[
            {"product_id": 10, "quantity": 1},
            {"product_id": 11, "quantity": 2},
        ],
    )

    assert result is updated_sale
    kwargs = repo.update.call_args.kwargs
    assert kwargs["sale_id"] == 1
    assert kwargs["client_id"] == 6
    assert kwargs["delivery_address"] == "New Address 123"
    assert kwargs["subtotal"] == Decimal("90.00")
    assert kwargs["taxes"] == Decimal("14.50")
    assert kwargs["total"] == Decimal("104.50")
    assert kwargs["lines"] == [
        {
            "product_id": 10,
            "quantity": 1,
            "unit_price": Decimal("50.00"),
            "vat_rate": Decimal("0.21"),
            "line_subtotal": Decimal("50.00"),
            "line_tax": Decimal("10.50"),
        },
        {
            "product_id": 11,
            "quantity": 2,
            "unit_price": Decimal("20.00"),
            "vat_rate": Decimal("0.10"),
            "line_subtotal": Decimal("40.00"),
            "line_tax": Decimal("4.00"),
        },
    ]
    stock_updater.update_stock_current.assert_has_awaits(
        [
            call(10, 9),  # old 2 -> new 1, releases one unit
            call(11, 2),  # old 0 -> new 2, consumes two units
        ],
        any_order=True,
    )


@pytest.mark.asyncio
async def test_update_sale_fails_when_status_is_not_pending():
    repo = AsyncMock()
    client_reader = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = UpdateSaleUseCase(repo, client_reader, product_reader, stock_updater)

    repo.get_by_id.return_value = make_sale(status="Approved")

    with pytest.raises(SaleException) as exc_info:
        await use_case.execute(
            sale_id=1,
            client_id=6,
            delivery_address="Some address",
            lines=[{"product_id": 10, "quantity": 1}],
        )

    assert exc_info.value.info == SaleExceptionInfo.SALE_NOT_PENDING
    repo.update.assert_not_called()
