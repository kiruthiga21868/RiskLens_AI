"""
Detection schemas - request inputs and the unified six-field response
guaranteed by every AI module.
"""
from pydantic import BaseModel, Field

from typing import Any


class UrlScanRequest(BaseModel):
    url: str = Field(min_length=5, max_length=2048)


class EmailScanRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class CredentialScanRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class FeatureImportance(BaseModel):
    """Model-independent mapping feature -> SHAP contribution."""

    feature: str
    value: float


class DetectionResponse(BaseModel):
    """Unified output shape used by URL, email and credential modules."""

    prediction: str
    confidence: float
    risk_score: float
    feature_importance: dict[str, float]
    explanation: str
    recommendation: str
    raw_score: float
    details: dict[str, Any] | None = None