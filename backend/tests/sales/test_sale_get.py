from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from composition.dependencies import get_get_sale_use_case
from main import app
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale, make_sale_line


async def test_get_sale_success(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/1")
    del app.dependency_overrides[get_get_sale_use_case]
    assert response.status_code == 200
    body = response.json()
    assert body["sale_id"] == 1
    assert body["sale_number"] == "VEN-2026-0001"
    assert body["status"] == "Pending"
    assert body["client_id"] == 5
    assert body["client_name"] == "Cliente Test S.L."
    assert body["user_id"] == 2
    assert body["created_by_name"] == "Sales Employee"
    assert body["cancelled_at"] is None
    assert body["cancelled_by_user_id"] is None
    assert body["cancelled_by_name"] is None
    assert len(body["lines"]) == 1


async def test_get_sale_delivery_address(sales_client: AsyncClient):
    sale = make_sale(delivery_address="Gran Via 10, Barcelona, Cataluña, 08001")
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/1")
    del app.dependency_overrides[get_get_sale_use_case]
    assert response.status_code == 200
    assert (
        response.json()["delivery_address"] == "Gran Via 10, Barcelona, Cataluña, 08001"
    )


async def test_get_sale_economic_summary(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/1")
    del app.dependency_overrides[get_get_sale_use_case]
    assert response.status_code == 200
    body = response.json()
    assert float(body["subtotal"]) == 100.00
    assert float(body["taxes"]) == 21.00
    assert float(body["total"]) == 121.00


async def test_get_sale_line_details(sales_client: AsyncClient):
    from decimal import Decimal

    line = make_sale_line(
        quantity=3,
        unit_price=Decimal("30.00"),
        line_subtotal=Decimal("90.00"),
        vat_rate=Decimal("0.10"),
        line_tax=Decimal("9.00"),
    )
    sale = make_sale(lines=[line])
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/1")
    del app.dependency_overrides[get_get_sale_use_case]
    assert response.status_code == 200
    line_body = response.json()["lines"][0]
    assert line_body["quantity"] == 3
    assert float(line_body["unit_price"]) == 30.00
    assert float(line_body["line_subtotal"]) == 90.00
    assert float(line_body["vat_rate"]) == 0.10
    assert float(line_body["line_tax"]) == 9.00


async def test_get_sale_not_found(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.SALE_NOT_FOUND)
    )
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/999")
    del app.dependency_overrides[get_get_sale_use_case]
    assert response.status_code == 404


async def test_get_sale_includes_cancellation_fields(sales_client: AsyncClient):
    from datetime import UTC, datetime

    sale = make_sale(
        status="Cancelled",
        cancelled_at=datetime(2026, 4, 10, 12, 0, tzinfo=UTC),
        cancelled_by_user_id=2,
        cancelled_by_name="Sales Employee",
    )
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_get_sale_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales/1")
    del app.dependency_overrides[get_get_sale_use_case]

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Cancelled"
    assert body["cancelled_at"].startswith("2026-04-10T12:00:00")
    assert body["cancelled_by_user_id"] == 2
    assert body["cancelled_by_name"] == "Sales Employee"


async def test_get_sale_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.get("/api/v1/sales/1")
    assert response.status_code == 401
