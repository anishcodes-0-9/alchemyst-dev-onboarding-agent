from __future__ import annotations
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
import uuid


class IntegrationState(BaseModel):
    useCase: Optional[str] = None
    stack: Optional[str] = None
    feature: Optional[str] = None          # loosened — match.py sets OpenAI feature names
    architecture: Optional[str] = None
    code: Optional[str] = None
    language: Literal["python", "javascript", "java"] = "python"
    features: List[str] = Field(default_factory=list)
    no_op: bool = False


class SessionState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    stage: Literal["discover", "match", "generate", "done"] = "discover"
    history: List[dict] = Field(default_factory=list)
    integration: IntegrationState = Field(default_factory=IntegrationState)
    memory_active: bool = False