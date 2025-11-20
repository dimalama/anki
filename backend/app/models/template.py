"""Template models"""

from pydantic import BaseModel, Field
from typing import Optional


class TemplateBase(BaseModel):
    """Base template model"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    type: str = Field(..., description="Template type: basic or cloze")
    qfmt: str = Field(..., description="Question format (front of card)")
    afmt: str = Field(..., description="Answer format (back of card)")
    css: Optional[str] = Field(None, description="Custom CSS styling")


class TemplateCreate(TemplateBase):
    """Model for creating a new template"""
    pass


class Template(TemplateBase):
    """Complete template model"""
    id: str = Field(..., description="Template identifier")
    is_default: bool = Field(default=False, description="Whether this is a default template")

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    """API response model for template operations"""
    success: bool
    message: str
    template: Optional[Template] = None


class TemplateListResponse(BaseModel):
    """API response model for listing templates"""
    success: bool
    count: int
    templates: list[Template]
