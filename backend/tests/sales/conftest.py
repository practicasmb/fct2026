from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from composition.security import get_current_user, require_sales_department_or_admin
from main import app
from modules.sales.domain.entities.sale import Sale
from modules.sales.domain.entities.sale_line import SaleLine
from shared.domain.dtos.user_session import UserSession


def _sales_user() -> UserSession:
    return UserSession(
        user_id=2,
        email="sales@test.com",
        role="Employee",
        department_id=3,
        firebase_uid="uid-sales",
        name="Sales Employee",
        last_login_at=None,
    )


def make_sale_line(**kwargs) -> MagicMock:
    defaults = {
        "sale_line_id": 1,
        "sale_id": 1,
        "product_id": 10,
        "quantity": 2,
        "unit_price": Decimal("50.00"),
        "line_subtotal": Decimal("100.00"),
        "vat_rate": Decimal("0.21"),
        "line_tax": Decimal("21.00"),
    }
    defaults.update(kwargs)
    line = MagicMock(spec=SaleLine)
    for k, v in defaults.items():
        setattr(line, k, v)
    return line


def make_sale(**kwargs) -> MagicMock:
    line = make_sale_line()
    defaults = {
        "sale_id": 1,
        "sale_number": "VEN-2026-0001",
        "client_id": 5,
        "client_name": "Cliente Test S.L.",
        "delivery_address": "Calle Mayor 1, Madrid, Madrid, 28001",
        "user_id": 2,
        "sale_date": datetime(2026, 4, 6, tzinfo=UTC),
        "status": "Pending",
        "subtotal": Decimal("100.00"),
        "taxes": Decimal("21.00"),
        "total": Decimal("121.00"),
        "created_at": datetime(2026, 4, 6, tzinfo=UTC),
        "updated_at": datetime(2026, 4, 6, tzinfo=UTC),
        "lines": [line],
    }
    defaults.update(kwargs)
    sale = MagicMock(spec=Sale)
    for k, v in defaults.items():
        setattr(sale, k, v)
    return sale


@pytest_asyncio.fixture
async def sales_client():
    """Authenticated client with sales department access."""

    def override_require():
        return _sales_user()

    def override_user():
        return _sales_user()

    app.dependency_overrides[get_current_user] = override_user
    app.dependency_overrides[require_sales_department_or_admin] = override_require

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    del app.dependency_overrides[get_current_user]
    del app.dependency_overrides[require_sales_department_or_admin]


@pytest_asyncio.fixture
async def non_sales_client():
    """Authenticated client without sales access — expects 403."""

    def override_user():
        return UserSession(
            user_id=1,
            email="other@test.com",
            role="Employee",
            department_id=99,
            firebase_uid="uid-other",
            name="Other Employee",
            last_login_at=None,
        )

    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    del app.dependency_overrides[get_current_user]
