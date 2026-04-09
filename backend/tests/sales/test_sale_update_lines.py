from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException, status
from httpx import AsyncClient

from composition.dependencies import get_update_sale_lines_use_case
from composition.security import require_sales_department_or_admin
from main import app
from modules.sales.domain.exceptions import SaleException, SaleExceptionInfo
from tests.sales.conftest import make_sale, make_sale_line

VALID_BODY = {
    "lines": [{"product_id": 10, "quantity": 2}],
}


async def test_update_lines_success(sales_client: AsyncClient):
    sale = make_sale()
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    response = await sales_client.put("/api/v1/sales/1/lines", json=VALID_BODY)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 200
    body = response.json()
    assert body["sale_id"] == 1
    assert len(body["lines"]) == 1


async def test_update_lines_with_discount(sales_client: AsyncClient):
    discounted_line = make_sale_line(
        discount=Decimal("5.00"),
        line_subtotal=Decimal("95.00"),
        line_tax=Decimal("19.95"),
    )
    sale = make_sale(
        subtotal=Decimal("95.00"),
        taxes=Decimal("19.95"),
        total=Decimal("114.95"),
        lines=[discounted_line],
    )
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    body = {"lines": [{"product_id": 10, "quantity": 2, "discount": "5.00"}]}
    response = await sales_client.put("/api/v1/sales/1/lines", json=body)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 200
    line = response.json()["lines"][0]
    assert float(line["discount"]) == 5.00
    assert float(line["line_subtotal"]) == 95.00


async def test_update_lines_recalculates_totals(sales_client: AsyncClient):
    line1 = make_sale_line(
        sale_line_id=1,
        product_id=10,
        quantity=2,
        unit_price=Decimal("50.00"),
        line_subtotal=Decimal("100.00"),
        line_tax=Decimal("21.00"),
    )
    line2 = make_sale_line(
        sale_line_id=2,
        product_id=11,
        quantity=1,
        unit_price=Decimal("30.00"),
        line_subtotal=Decimal("30.00"),
        line_tax=Decimal("6.30"),
    )
    sale = make_sale(
        subtotal=Decimal("130.00"),
        taxes=Decimal("27.30"),
        total=Decimal("157.30"),
        lines=[line1, line2],
    )
    mock = MagicMock()
    mock.execute = AsyncMock(return_value=sale)
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    body = {
        "lines": [{"product_id": 10, "quantity": 2}, {"product_id": 11, "quantity": 1}]
    }
    response = await sales_client.put("/api/v1/sales/1/lines", json=body)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 200
    body_resp = response.json()
    assert float(body_resp["subtotal"]) == 130.00
    assert float(body_resp["taxes"]) == 27.30
    assert float(body_resp["total"]) == 157.30


async def test_update_lines_sale_not_found(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.SALE_NOT_FOUND)
    )
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    response = await sales_client.put("/api/v1/sales/999/lines", json=VALID_BODY)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 404


async def test_update_lines_sale_not_pending(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.SALE_NOT_PENDING)
    )
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    response = await sales_client.put("/api/v1/sales/1/lines", json=VALID_BODY)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 422
    assert response.json()["error_code"] == 8108


async def test_update_lines_empty_lines(sales_client: AsyncClient):
    response = await sales_client.put("/api/v1/sales/1/lines", json={"lines": []})
    assert response.status_code == 422


async def test_update_lines_invalid_discount(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.INVALID_DISCOUNT)
    )
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    body = {"lines": [{"product_id": 10, "quantity": 1, "discount": "999.00"}]}
    response = await sales_client.put("/api/v1/sales/1/lines", json=body)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 422
    assert response.json()["error_code"] == 8109


async def test_update_lines_insufficient_stock(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        side_effect=SaleException(SaleExceptionInfo.INSUFFICIENT_STOCK)
    )
    app.dependency_overrides[get_update_sale_lines_use_case] = lambda: mock
    response = await sales_client.put("/api/v1/sales/1/lines", json=VALID_BODY)
    del app.dependency_overrides[get_update_sale_lines_use_case]
    assert response.status_code == 422


async def test_update_lines_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.put(
        "/api/v1/sales/1/lines", json=VALID_BODY
    )
    assert response.status_code == 401


async def test_update_lines_non_sales_forbidden(sales_client: AsyncClient):
    def raise_forbidden():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    original = app.dependency_overrides[require_sales_department_or_admin]
    app.dependency_overrides[require_sales_department_or_admin] = raise_forbidden
    response = await sales_client.put("/api/v1/sales/1/lines", json=VALID_BODY)
    app.dependency_overrides[require_sales_department_or_admin] = original
    assert response.status_code == 403
