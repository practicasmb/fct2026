from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from modules.sales.application.cancel_sale_use_case import CancelSaleUseCase
from modules.sales.application.delete_sale_use_case import DeleteSaleUseCase
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale, make_sale_line


@pytest.mark.asyncio
@pytest.mark.parametrize("current_status", ["Pending", "Approved"])
async def test_cancel_sale_releases_stock_and_sets_audit_fields(current_status: str):
    repo = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = CancelSaleUseCase(repo, product_reader, stock_updater)

    repo.get_by_id.return_value = make_sale(
        status=current_status,
        lines=[
            make_sale_line(product_id=10, quantity=2),
            make_sale_line(sale_line_id=2, product_id=10, quantity=1),
            make_sale_line(sale_line_id=3, product_id=11, quantity=1),
        ],
    )
    repo.cancel.return_value = make_sale(
        status="Cancelled",
        cancelled_by_user_id=2,
    )

    product_10 = MagicMock(stock_current=8)
    product_11 = MagicMock(stock_current=3)

    async def get_product(product_id: int):
        return {10: product_10, 11: product_11}.get(product_id)

    product_reader.get_by_id.side_effect = get_product

    result = await use_case.execute(sale_id=1, user_id=2)

    assert result.status == "Cancelled"
    stock_updater.update_stock_current.assert_has_awaits(
        [call(10, 11), call(11, 4)],
        any_order=True,
    )
    repo.cancel.assert_awaited_once()
    kwargs = repo.cancel.call_args.kwargs
    assert kwargs["sale_id"] == 1
    assert kwargs["cancelled_by_user_id"] == 2
    assert isinstance(kwargs["cancelled_at"], datetime)
    assert kwargs["cancelled_at"].tzinfo is not None


@pytest.mark.asyncio
async def test_cancel_sale_fails_when_status_is_not_cancellable():
    repo = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = CancelSaleUseCase(repo, product_reader, stock_updater)

    repo.get_by_id.return_value = make_sale(status="In Process")

    with pytest.raises(SaleException) as exc_info:
        await use_case.execute(sale_id=1, user_id=2)

    assert exc_info.value.info == SaleExceptionInfo.SALE_NOT_CANCELLABLE
    repo.cancel.assert_not_called()
    stock_updater.update_stock_current.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sale_releases_stock_and_deletes_when_pending():
    repo = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = DeleteSaleUseCase(repo, product_reader, stock_updater)

    repo.get_by_id.return_value = make_sale(
        status="Pending",
        lines=[
            make_sale_line(product_id=10, quantity=2),
            make_sale_line(sale_line_id=2, product_id=10, quantity=1),
            make_sale_line(sale_line_id=3, product_id=11, quantity=1),
        ],
    )

    product_10 = MagicMock(stock_current=8)
    product_11 = MagicMock(stock_current=3)

    async def get_product(product_id: int):
        return {10: product_10, 11: product_11}.get(product_id)

    product_reader.get_by_id.side_effect = get_product

    await use_case.execute(sale_id=1)

    stock_updater.update_stock_current.assert_has_awaits(
        [call(10, 11), call(11, 4)],
        any_order=True,
    )
    repo.delete.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_delete_sale_fails_when_status_is_not_pending():
    repo = AsyncMock()
    product_reader = AsyncMock()
    stock_updater = AsyncMock()
    use_case = DeleteSaleUseCase(repo, product_reader, stock_updater)

    repo.get_by_id.return_value = make_sale(status="Approved")

    with pytest.raises(SaleException) as exc_info:
        await use_case.execute(sale_id=1)

    assert exc_info.value.info == SaleExceptionInfo.SALE_NOT_DELETABLE
    repo.delete.assert_not_called()
    stock_updater.update_stock_current.assert_not_called()
