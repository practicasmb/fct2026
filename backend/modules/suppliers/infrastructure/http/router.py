from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from composition.dependencies import (
    get_download_supplier_template_use_case,
    get_import_suppliers_use_case,
)
from composition.security import get_current_user
from modules.suppliers.domain.interfaces.use_cases.i_download_supplier_template_use_case import (
    IDownloadSupplierTemplateUseCase,
)
from modules.suppliers.domain.interfaces.use_cases.i_import_suppliers_use_case import (
    IImportSuppliersUseCase,
)
from modules.suppliers.infrastructure.http.schemas import ImportErrorDTO, ImportResultDTO
from shared.domain.entities.user_session import UserSession

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

ALLOWED_ROLES = {"Administrator", "Manager"}


@router.get("/template")
async def download_template(
    current_user: UserSession = Depends(get_current_user),
    use_case: IDownloadSupplierTemplateUseCase = Depends(
        get_download_supplier_template_use_case
    ),
):
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    content = use_case.execute()
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=suppliers_template.xlsx"
        },
    )


@router.post("/import", response_model=ImportResultDTO)
async def import_suppliers(
    file: UploadFile,
    current_user: UserSession = Depends(get_current_user),
    use_case: IImportSuppliersUseCase = Depends(get_import_suppliers_use_case),
):
    if current_user.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    content = await file.read()
    result = await use_case.execute(content)
    return ImportResultDTO(
        total=result.total,
        created=result.created,
        errors=len(result.errors),
        error_detail=[
            ImportErrorDTO(row=e.row, reason=e.reason) for e in result.errors
        ],
    )
