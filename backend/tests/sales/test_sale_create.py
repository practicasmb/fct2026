from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from composition.dependencies import get_create_sale_use_case
from main import app
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale

VALID_BODY = {
    "client_id": 5,
    "lines": [{"product_id": 10, "quantity": 2}],
}


async def test_create_sale_success(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 201
    body = response.json()
    assert body["sale_id"] == 1
    assert body["sale_number"] == "VEN-2026-0001"
    assert body["status"] == "Pending"
    assert body["client_id"] == 5
    assert body["user_id"] == 2
    assert "delivery_address" in body
    assert len(body["lines"]) == 1


async def test_create_sale_number_format(sales_client: AsyncClient):
    sale = make_sale(sale_number="VEN-2026-0042")
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 201
    assert response.json()["sale_number"].startswith("VEN-")


async def test_create_sale_economic_totals(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 201
    body = response.json()
    assert float(body["subtotal"]) == 100.00
    assert float(body["taxes"]) == 21.00
    assert float(body["total"]) == 121.00


async def test_create_sale_line_details(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 201
    line = response.json()["lines"][0]
    assert line["product_id"] == 10
    assert line["quantity"] == 2
    assert float(line["unit_price"]) == 50.00
    assert float(line["vat_rate"]) == 0.21
    assert float(line["line_tax"]) == 21.00


async def test_create_sale_insufficient_stock(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.INSUFFICIENT_STOCK)
    )
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 422


async def test_create_sale_empty_lines(sales_client: AsyncClient):
    body = {"client_id": 5, "lines": []}
    response = await sales_client.post("/api/v1/sales", json=body)
    assert response.status_code == 422


async def test_create_sale_client_not_found(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.CLIENT_NOT_FOUND)
    )
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 404


async def test_create_sale_client_not_active(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.CLIENT_NOT_ACTIVE)
    )
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 422


async def test_create_sale_product_not_found(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.PRODUCT_NOT_FOUND)
    )
    app.dependency_overrides[get_create_sale_use_case] = lambda: mock
    response = await sales_client.post("/api/v1/sales", json=VALID_BODY)
    del app.dependency_overrides[get_create_sale_use_case]
    assert response.status_code == 404


async def test_create_sale_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.post("/api/v1/sales", json=VALID_BODY)
    assert response.status_code == 401
