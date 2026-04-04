from fastapi import APIRouter

from app.schemas.resume import TemplateSummarySchema
from app.services.templates import TEMPLATES

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateSummarySchema])
def list_templates() -> list[TemplateSummarySchema]:
    return [TemplateSummarySchema.model_validate(template) for template in TEMPLATES]
