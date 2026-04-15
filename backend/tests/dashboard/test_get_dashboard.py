from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from composition.security import get_current_user
from main import app
from modules.admin.domain.entities.department import Department
from modules.catalog.domain.entities.category import Category
from modules.catalog.domain.entities.product import Product
from modules.clients.domain.entities.client import Client
from modules.purchases.domain.entities.purchase import Purchase
from modules.sales.domain.entities.sale import Sale
from modules.suppliers.domain.entities.supplier import Supplier
from shared.config import settings
from shared.domain.dtos.address import Address
from shared.domain.dtos.user_session import UserSession
from shared.domain.entities.user import User
from shared.infrastructure.database.connection import get_db


def _month_start(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, 1, tzinfo=UTC)


def _prev_month_start(dt: datetime) -> datetime:
    if dt.month == 1:
        return datetime(dt.year - 1, 12, 1, tzinfo=UTC)
    return datetime(dt.year, dt.month - 1, 1, tzinfo=UTC)


@pytest.fixture
def dashboard_settings():
    original_stale_days = settings.dashboard_stale_days
    original_recent_limit = settings.dashboard_recent_limit
    settings.dashboard_stale_days = 7
    settings.dashboard_recent_limit = 5
    yield
    settings.dashboard_stale_days = original_stale_days
    settings.dashboard_recent_limit = original_recent_limit


@pytest_asyncio.fixture
async def dashboard_client(db_session: AsyncSession, dashboard_settings):
    user_box = {
        "value": UserSession(
            user_id=1,
            email="admin@test.com",
            role="Administrator",
            department_id=None,
            firebase_uid="test-uid",
            name="Admin Test",
            last_login_at=None,
        )
    }

    async def override_get_db():
        yield db_session

    def override_get_current_user():
        return user_box["value"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac, user_box

    del app.dependency_overrides[get_db]
    del app.dependency_overrides[get_current_user]


@pytest_asyncio.fixture
async def seeded_dashboard_data(db_session: AsyncSession):
    now = datetime.now(UTC)
    current_month_start = _month_start(now)
    previous_month_start = _prev_month_start(now)

    sales_department = Department(name="Sales")
    purchases_department = Department(name="Purchases")
    db_session.add_all([sales_department, purchases_department])
    await db_session.flush()

    admin_user = User(
        first_name="Admin",
        last_name="User",
        email="admin.dashboard@test.com",
        role="Administrator",
        department_id=None,
        is_active=True,
    )
    purchases_user = User(
        first_name="Purchase",
        last_name="User",
        email="purchase.dashboard@test.com",
        role="Employee",
        department_id=purchases_department.department_id,
        is_active=True,
    )
    sales_user = User(
        first_name="Sales",
        last_name="User",
        email="sales.dashboard@test.com",
        role="Employee",
        department_id=sales_department.department_id,
        is_active=True,
    )
    db_session.add_all([admin_user, purchases_user, sales_user])
    await db_session.flush()

    supplier_a = Supplier(
        name="Supplier A",
        tax_id="SUPA123",
        address_data=Address("Street 1", "Madrid", "Madrid", "28001"),
        phone="600000001",
        email="supplier.a@test.com",
        is_active=True,
    )
    supplier_b = Supplier(
        name="Supplier B",
        tax_id="SUPB123",
        address_data=Address("Street 2", "Madrid", "Madrid", "28002"),
        phone="600000002",
        email="supplier.b@test.com",
        is_active=True,
    )
    db_session.add_all([supplier_a, supplier_b])
    await db_session.flush()

    client_a = Client(
        name="Client A",
        tax_id="CLIA123",
        address_data=Address("Main 1", "Madrid", "Madrid", "28001"),
        phone="700000001",
        email="client.a@test.com",
        is_active=True,
    )
    client_b = Client(
        name="Client B",
        tax_id="CLIB123",
        address_data=Address("Main 2", "Madrid", "Madrid", "28002"),
        phone="700000002",
        email="client.b@test.com",
        is_active=True,
    )
    db_session.add_all([client_a, client_b])
    await db_session.flush()

    category = Category(name="Hardware", description="Hardware category")
    db_session.add(category)
    await db_session.flush()

    product_low_1 = Product(
        product_code="LOW-001",
        name="Low Product 1",
        description="",
        category_id=category.category_id,
        price=Decimal("10.00"),
        vat_rate=Decimal("0.21"),
        stock_current=3,
        stock_min=10,
        is_active=True,
    )
    product_low_2 = Product(
        product_code="LOW-002",
        name="Low Product 2",
        description="",
        category_id=category.category_id,
        price=Decimal("20.00"),
        vat_rate=Decimal("0.21"),
        stock_current=0,
        stock_min=5,
        is_active=True,
    )
    product_ok = Product(
        product_code="OK-001",
        name="Healthy Product",
        description="",
        category_id=category.category_id,
        price=Decimal("30.00"),
        vat_rate=Decimal("0.21"),
        stock_current=20,
        stock_min=5,
        is_active=True,
    )
    db_session.add_all([product_low_1, product_low_2, product_ok])
    await db_session.flush()

    purchases = [
        Purchase(
            purchase_number="COM-2026-9001",
            supplier_id=supplier_a.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=current_month_start + timedelta(days=2),
            status="Received",
            status_changed_at=now - timedelta(days=1),
            subtotal=Decimal("100.00"),
            taxes=Decimal("21.00"),
            total=Decimal("121.00"),
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        ),
        Purchase(
            purchase_number="COM-2026-9002",
            supplier_id=supplier_b.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=previous_month_start + timedelta(days=2),
            status="Received",
            status_changed_at=now - timedelta(days=10),
            subtotal=Decimal("50.00"),
            taxes=Decimal("10.50"),
            total=Decimal("60.50"),
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=2),
        ),
        Purchase(
            purchase_number="COM-2026-9003",
            supplier_id=supplier_a.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=current_month_start + timedelta(days=3),
            status="Pending",
            status_changed_at=now - timedelta(days=8),
            subtotal=Decimal("30.00"),
            taxes=Decimal("6.30"),
            total=Decimal("36.30"),
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3),
        ),
        Purchase(
            purchase_number="COM-2026-9004",
            supplier_id=supplier_b.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=current_month_start + timedelta(days=4),
            status="Approved",
            status_changed_at=now - timedelta(days=2),
            subtotal=Decimal("40.00"),
            taxes=Decimal("8.40"),
            total=Decimal("48.40"),
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=4),
        ),
        Purchase(
            purchase_number="COM-2026-9005",
            supplier_id=supplier_a.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=current_month_start + timedelta(days=5),
            status="Pending",
            status_changed_at=now - timedelta(days=9),
            subtotal=Decimal("20.00"),
            taxes=Decimal("4.20"),
            total=Decimal("24.20"),
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5),
        ),
        Purchase(
            purchase_number="COM-2026-9006",
            supplier_id=supplier_b.supplier_id,
            user_id=purchases_user.user_id,
            warehouse_id=1,
            purchase_date=current_month_start + timedelta(days=6),
            status="Cancelled",
            status_changed_at=now - timedelta(days=20),
            subtotal=Decimal("10.00"),
            taxes=Decimal("2.10"),
            total=Decimal("12.10"),
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=6),
        ),
    ]
    db_session.add_all(purchases)

    sales = [
        Sale(
            sale_number="VEN-2026-9001",
            client_id=client_a.client_id,
            delivery_address="Address 1",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=1),
            status="Pending",
            status_changed_at=now - timedelta(days=1),
            subtotal=Decimal("80.00"),
            taxes=Decimal("16.80"),
            total=Decimal("96.80"),
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        ),
        Sale(
            sale_number="VEN-2026-9002",
            client_id=client_b.client_id,
            delivery_address="Address 2",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=2),
            status="Approved",
            status_changed_at=now - timedelta(days=10),
            subtotal=Decimal("50.00"),
            taxes=Decimal("10.50"),
            total=Decimal("60.50"),
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=2),
        ),
        Sale(
            sale_number="VEN-2026-9003",
            client_id=client_a.client_id,
            delivery_address="Address 3",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=3),
            status="In Process",
            status_changed_at=now - timedelta(days=8),
            subtotal=Decimal("40.00"),
            taxes=Decimal("8.40"),
            total=Decimal("48.40"),
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3),
        ),
        Sale(
            sale_number="VEN-2026-9004",
            client_id=client_b.client_id,
            delivery_address="Address 4",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=4),
            status="Pending",
            status_changed_at=now - timedelta(days=2),
            subtotal=Decimal("30.00"),
            taxes=Decimal("6.30"),
            total=Decimal("36.30"),
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=4),
        ),
        Sale(
            sale_number="VEN-2026-9005",
            client_id=client_a.client_id,
            delivery_address="Address 5",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=5),
            status="Approved",
            status_changed_at=now - timedelta(days=12),
            subtotal=Decimal("20.00"),
            taxes=Decimal("4.20"),
            total=Decimal("24.20"),
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5),
        ),
        Sale(
            sale_number="VEN-2026-9006",
            client_id=client_b.client_id,
            delivery_address="Address 6",
            user_id=sales_user.user_id,
            sale_date=current_month_start + timedelta(days=6),
            status="Cancelled",
            status_changed_at=now - timedelta(days=25),
            subtotal=Decimal("10.00"),
            taxes=Decimal("2.10"),
            total=Decimal("12.10"),
            created_at=now - timedelta(hours=6),
            updated_at=now - timedelta(hours=6),
        ),
    ]
    db_session.add_all(sales)
    await db_session.flush()

    return {
        "sales_department_id": sales_department.department_id,
        "purchases_department_id": purchases_department.department_id,
    }


def _status_map(items: list[dict]) -> dict[str, int]:
    return {item["status"]: item["count"] for item in items}


async def _set_user(user_box: dict, role: str, department_id: int | None) -> None:
    user_box["value"] = UserSession(
        user_id=100,
        email="viewer@test.com",
        role=role,
        department_id=department_id,
        firebase_uid="viewer-uid",
        name="Viewer User",
        last_login_at=None,
    )


@pytest.mark.asyncio
async def test_dashboard_admin_returns_full_payload(
    dashboard_client, seeded_dashboard_data
):
    client, user_box = dashboard_client
    await _set_user(user_box, role="Administrator", department_id=None)

    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200

    body = response.json()
    assert body["meta"]["stale_days"] == 7
    assert body["meta"]["recent_limit"] == 5

    purchase_summary = _status_map(body["purchase_status_summary"])
    assert purchase_summary["Received"] == 2
    assert purchase_summary["Pending"] == 2
    assert purchase_summary["Approved"] == 1
    assert purchase_summary["Cancelled"] == 1

    sales_summary = _status_map(body["sales_status_summary"])
    assert sales_summary["Pending"] == 2
    assert sales_summary["Approved"] == 2
    assert sales_summary["In Process"] == 1
    assert sales_summary["Cancelled"] == 1

    assert len(body["latest_purchases"]) == 5
    assert body["latest_purchases"][0]["number"] == "COM-2026-9001"
    assert body["latest_purchases"][1]["number"] == "COM-2026-9002"
    assert len(body["latest_sales"]) == 5
    assert body["latest_sales"][0]["number"] == "VEN-2026-9001"
    assert body["latest_sales"][1]["number"] == "VEN-2026-9002"

    spend = body["purchase_spend_comparison"]
    assert float(spend["current_month"]) == 121.00
    assert float(spend["previous_month"]) == 60.50
    assert float(spend["difference_amount"]) == 60.50
    assert float(spend["difference_percent"]) == 100.00

    low_stock_codes = {item["product_code"] for item in body["low_stock_products"]}
    assert low_stock_codes == {"LOW-001", "LOW-002"}

    stale_purchase_numbers = {item["number"] for item in body["stale_purchases"]}
    assert "COM-2026-9002" in stale_purchase_numbers
    assert "COM-2026-9003" in stale_purchase_numbers
    assert all(item["days_in_status"] >= 7 for item in body["stale_purchases"])

    stale_sale_numbers = {item["number"] for item in body["stale_sales"]}
    assert "VEN-2026-9002" in stale_sale_numbers
    assert "VEN-2026-9003" in stale_sale_numbers
    assert all(item["days_in_status"] >= 7 for item in body["stale_sales"])


@pytest.mark.asyncio
async def test_dashboard_purchases_department_visibility(
    dashboard_client, seeded_dashboard_data
):
    client, user_box = dashboard_client
    await _set_user(
        user_box,
        role="Employee",
        department_id=seeded_dashboard_data["purchases_department_id"],
    )

    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()

    assert body["purchase_status_summary"] != []
    assert body["latest_purchases"] != []
    assert body["stale_purchases"] != []
    assert body["purchase_spend_comparison"] is not None

    assert body["sales_status_summary"] == []
    assert body["latest_sales"] == []
    assert body["stale_sales"] == []
    assert body["low_stock_products"] != []


@pytest.mark.asyncio
async def test_dashboard_sales_department_visibility(
    dashboard_client, seeded_dashboard_data
):
    client, user_box = dashboard_client
    await _set_user(
        user_box,
        role="Employee",
        department_id=seeded_dashboard_data["sales_department_id"],
    )

    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()

    assert body["sales_status_summary"] != []
    assert body["latest_sales"] != []
    assert body["stale_sales"] != []

    assert body["purchase_status_summary"] == []
    assert body["latest_purchases"] == []
    assert body["stale_purchases"] == []
    assert body["purchase_spend_comparison"] is None
    assert body["low_stock_products"] != []


@pytest.mark.asyncio
async def test_dashboard_difference_percent_null_when_previous_month_is_zero(
    dashboard_client,
    db_session: AsyncSession,
    seeded_dashboard_data,
):
    client, user_box = dashboard_client
    await _set_user(user_box, role="Administrator", department_id=None)

    previous_received = await db_session.execute(
        select(Purchase).where(Purchase.purchase_number == "COM-2026-9002")
    )
    purchase = previous_received.scalar_one()
    purchase.status = "Pending"
    purchase.status_changed_at = datetime.now(UTC) - timedelta(days=1)
    await db_session.flush()

    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    spend = response.json()["purchase_spend_comparison"]
    assert float(spend["previous_month"]) == 0.0
    assert spend["difference_percent"] is None


@pytest.mark.asyncio
async def test_dashboard_unauthenticated_returns_401(
    unauthenticated_client: AsyncClient,
):
    response = await unauthenticated_client.get("/api/v1/dashboard")
    assert response.status_code == 401
