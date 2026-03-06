import re
from io import BytesIO

from openpyxl import load_workbook

from modules.suppliers.domain.entities.import_result import (
    ImportError,
    ImportResult,
)
from modules.suppliers.domain.interfaces.repositories.i_supplier_repository import (
    ISupplierRepository,
)
from modules.suppliers.domain.interfaces.use_cases.i_import_suppliers_use_case import (
    IImportSuppliersUseCase,
)

COLUMN_MAP = {
    "Nombre": "name",
    "CIF": "tax_id",
    "Dirección": "address",
    "Ciudad": "city",
    "Provincia": "province",
    "Código Postal": "postal_code",
    "Teléfono": "phone",
    "Email": "email",
}
EXPECTED_HEADERS = list(COLUMN_MAP.keys())
CIF_REGEX = re.compile(r"^[ABCDEFGHJNPQRSUVW]\d{7}[0-9A-J]$")
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ImportSuppliersUseCase(IImportSuppliersUseCase):
    def __init__(self, repo: ISupplierRepository) -> None:
        self._repo = repo

    async def execute(self, file_content: bytes) -> ImportResult:
        wb = load_workbook(BytesIO(file_content), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(min_row=1, values_only=True))

        if len(rows) < 2:
            return ImportResult(
                total=0,
                created=0,
                errors=[
                    ImportError(row=1, reason="File is empty or has no data rows")
                ],
            )

        headers = [str(h).strip() if h else "" for h in rows[0]]
        if headers != EXPECTED_HEADERS:
            return ImportResult(
                total=0,
                created=0,
                errors=[
                    ImportError(
                        row=1, reason="Invalid headers. Use the provided template"
                    )
                ],
            )

        data_rows = rows[1:]
        errors: list[ImportError] = []
        parsed: list[dict] = []
        seen_tax_ids: set[str] = set()

        for i, row in enumerate(data_rows, start=2):
            row_errors = self._validate_row(row, i, seen_tax_ids)
            if row_errors:
                errors.extend(row_errors)
            else:
                supplier_data = {
                    db_field: str(row[col_idx]).strip()
                    for col_idx, db_field in enumerate(COLUMN_MAP.values())
                }
                parsed.append(supplier_data)
                seen_tax_ids.add(supplier_data["tax_id"].upper())

        if parsed and not errors:
            existing = await self._repo.get_existing_tax_ids(
                [s["tax_id"] for s in parsed]
            )
            for i, row in enumerate(data_rows, start=2):
                tax_id = str(row[1]).strip().upper() if row[1] else ""
                if tax_id in existing:
                    errors.append(
                        ImportError(
                            row=i,
                            reason=f"CIF {tax_id} already exists in database",
                        )
                    )

        total = len(data_rows)
        if errors:
            return ImportResult(total=total, created=0, errors=errors)

        created = await self._repo.bulk_create(parsed)
        return ImportResult(total=total, created=created, errors=[])

    def _validate_row(
        self, row: tuple, row_num: int, seen_tax_ids: set[str]
    ) -> list[ImportError]:
        errors: list[ImportError] = []
        field_names = list(COLUMN_MAP.keys())

        for col_idx, header in enumerate(field_names):
            value = row[col_idx] if col_idx < len(row) else None
            if value is None or str(value).strip() == "":
                errors.append(
                    ImportError(row=row_num, reason=f"Field '{header}' is required")
                )

        if errors:
            return errors

        tax_id = str(row[1]).strip().upper()
        email = str(row[7]).strip()

        if not CIF_REGEX.match(tax_id):
            errors.append(ImportError(row=row_num, reason="Invalid CIF format"))

        if not EMAIL_REGEX.match(email):
            errors.append(ImportError(row=row_num, reason="Invalid email format"))

        if tax_id in seen_tax_ids:
            errors.append(ImportError(row=row_num, reason="Duplicate CIF in file"))

        return errors
