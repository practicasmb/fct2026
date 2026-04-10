from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from httpx import AsyncClient

from composition.dependencies import (
    get_cancel_sale_use_case,
    get_delete_sale_use_case,
)
from composition.security import require_sales_department_or_admin
from main import app
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale


async def test_cancel_sale_success_pending(sales_client: AsyncClient):
    sale = make_sale(
        status="Cancelled",
        cancelled_at=datetime(2026, 4, 10, 12, 0, tzinfo=UTC),
        cancelled_by_user_id=2,
        cancelled_by_name="Sales Employee",
    )
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_cancel_sale_use_case] = lambda: mock

    response = await sales_client.patch("/api/v1/sales/1/cancel")
    del app.dependency_overrides[get_cancel_sale_use_case]

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Cancelled"
    assert body["cancelled_by_user_id"] == 2
    assert body["cancelled_by_name"] == "Sales Employee"
    mock.execute.assert_awaited_once_with(sale_id=1, user_id=2)


async def test_cancel_sale_success_approved(sales_client: AsyncClient):
    sale = make_sale(
        status="Cancelled",
        cancelled_at=datetime(2026, 4, 10, 12, 0, tzinfo=UTC),
        cancelled_by_user_id=2,
        cancelled_by_name="Sales Employee",
    )
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_cancel_sale_use_case] = lambda: mock

    response = await sales_client.patch("/api/v1/sales/1/cancel")
    del app.dependency_overrides[get_cancel_sale_use_case]

    assert response.status_code == 200
    assert response.json()["status"] == "Cancelled"


async def test_cancel_sale_not_cancellable_error(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.SALE_NOT_CANCELLABLE)
    )
    app.dependency_overrides[get_cancel_sale_use_case] = lambda: mock

    response = await sales_client.patch("/api/v1/sales/1/cancel")
    del app.dependency_overrides[get_cancel_sale_use_case]

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == SaleExceptionInfo.SALE_NOT_CANCELLABLE.code
    assert body["detail"] == SaleExceptionInfo.SALE_NOT_CANCELLABLE.message


async def test_cancel_sale_forbidden_for_non_sales(sales_client: AsyncClient):
    def override_forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    previous_override = app.dependency_overrides[require_sales_department_or_admin]
    app.dependency_overrides[require_sales_department_or_admin] = override_forbidden
    response = await sales_client.patch("/api/v1/sales/1/cancel")
    app.dependency_overrides[require_sales_department_or_admin] = previous_override
    assert response.status_code == 403


async def test_cancel_sale_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.patch("/api/v1/sales/1/cancel")
    assert response.status_code == 401


async def test_delete_sale_pending_returns_204(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=None)
    app.dependency_overrides[get_delete_sale_use_case] = lambda: mock

    response = await sales_client.delete("/api/v1/sales/1")
    del app.dependency_overrides[get_delete_sale_use_case]

    assert response.status_code == 204
    assert response.text == ""
    mock.execute.assert_awaited_once_with(sale_id=1)


async def test_delete_sale_non_pending_error(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.SALE_NOT_DELETABLE)
    )
    app.dependency_overrides[get_delete_sale_use_case] = lambda: mock

    response = await sales_client.delete("/api/v1/sales/1")
    del app.dependency_overrides[get_delete_sale_use_case]

    assert response.status_code == 400
    body = response.json()
    assert body["error_code"] == SaleExceptionInfo.SALE_NOT_DELETABLE.code
    assert body["detail"] == SaleExceptionInfo.SALE_NOT_DELETABLE.message


async def test_delete_sale_forbidden_for_non_sales(sales_client: AsyncClient):
    def override_forbidden():
        raise HTTPException(status_code=403, detail="Forbidden")

    previous_override = app.dependency_overrides[require_sales_department_or_admin]
    app.dependency_overrides[require_sales_department_or_admin] = override_forbidden
    response = await sales_client.delete("/api/v1/sales/1")
    app.dependency_overrides[require_sales_department_or_admin] = previous_override
    assert response.status_code == 403


async def test_delete_sale_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.delete("/api/v1/sales/1")
    assert response.status_code == 401
