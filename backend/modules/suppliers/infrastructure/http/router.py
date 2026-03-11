from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from composition.dependencies import get_download_supplier_template_use_case
from composition.security import get_current_user
from modules.suppliers.domain.interfaces.use_cases.i_download_supplier_template_use_case import (
    IDownloadSupplierTemplateUseCase,
)
from shared.domain.entities.user_session import UserSession

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

ALLOWED_ROLES = {"Administrator", "Manager"}


@router.get("/template")
def download_template(
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
