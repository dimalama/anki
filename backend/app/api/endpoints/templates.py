"""Template API endpoints"""

from fastapi import APIRouter, HTTPException, status

from app.models.template import Template, TemplateCreate, TemplateResponse, TemplateListResponse
from app.services.template_service import TemplateService

router = APIRouter()
template_service = TemplateService()


@router.get("", response_model=TemplateListResponse)
async def list_templates():
    """List all available templates"""
    try:
        templates = template_service.list_templates()
        return TemplateListResponse(
            success=True,
            count=len(templates),
            templates=templates
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template"""
    try:
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template '{template_id}' not found"
            )
        return TemplateResponse(
            success=True,
            message="Template retrieved successfully",
            template=template
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template: {str(e)}"
        )


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(template_data: TemplateCreate):
    """Create a custom template"""
    try:
        template = template_service.create_template(template_data)
        return TemplateResponse(
            success=True,
            message="Template created successfully",
            template=template
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating template: {str(e)}"
        )
