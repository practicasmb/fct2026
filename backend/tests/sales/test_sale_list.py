from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient

from composition.dependencies import get_list_sales_use_case
from main import app
from shared.domain.dtos.paginated_result import PaginatedResult
from tests.sales.conftest import make_sale


async def test_list_sales_empty(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[], total=0, page=1, page_size=20)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["page"] == 1
    assert body["page_size"] == 20


async def test_list_sales_returns_data(sales_client: AsyncClient):
    sale = make_sale()
    row = (sale, "Cliente Test S.L.")
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[row], total=1, page=1, page_size=20)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    item = body["items"][0]
    assert item["sale_id"] == 1
    assert item["sale_number"] == "VEN-2026-0001"
    assert item["client_name"] == "Cliente Test S.L."
    assert item["status"] == "Pending"
    assert float(item["total"]) == 121.00


async def test_list_sales_pagination_params(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[], total=0, page=2, page_size=10)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales?page=2&page_size=10")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    kwargs = mock.execute.call_args[1]
    assert kwargs["page"] == 2
    assert kwargs["page_size"] == 10


async def test_list_sales_filter_by_status(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[], total=0, page=1, page_size=20)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales?status=Pending")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    assert mock.execute.call_args[1]["status"] == "Pending"


async def test_list_sales_filter_by_client(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[], total=0, page=1, page_size=20)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales?client_id=5")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    assert mock.execute.call_args[1]["client_id"] == 5


async def test_list_sales_default_sort(sales_client: AsyncClient):
    mock = MagicMock()
    mock.execute = AsyncMock(
        return_value=PaginatedResult(items=[], total=0, page=1, page_size=20)
    )
    app.dependency_overrides[get_list_sales_use_case] = lambda: mock
    response = await sales_client.get("/api/v1/sales")
    del app.dependency_overrides[get_list_sales_use_case]
    assert response.status_code == 200
    kwargs = mock.execute.call_args[1]
    assert kwargs["sort_field"] == "created_at"
    assert kwargs["sort_order"] == "desc"


async def test_list_sales_unauthenticated(unauthenticated_client: AsyncClient):
    response = await unauthenticated_client.get("/api/v1/sales")
    assert response.status_code == 401
