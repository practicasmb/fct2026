from io import BytesIO

from openpyxl import Workbook

from modules.suppliers.domain.interfaces.use_cases.i_download_supplier_template_use_case import (
    IDownloadSupplierTemplateUseCase,
)


class DownloadSupplierTemplateUseCase(IDownloadSupplierTemplateUseCase):
    HEADERS = [
        "Nombre",
        "CIF",
        "Dirección",
        "Ciudad",
        "Provincia",
        "Código Postal",
        "Teléfono",
        "Email",
    ]
    EXAMPLE = [
        "Proveedor Ejemplo S.L.",
        "B12345674",
        "Calle Gran Vía 1",
        "Madrid",
        "Madrid",
        "28001",
        "912345678",
        "contacto@ejemplo.com",
    ]

    def execute(self) -> bytes:
        wb = Workbook()
        ws = wb.active
        ws.title = "Proveedores"
        ws.append(self.HEADERS)
        ws.append(self.EXAMPLE)
        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
