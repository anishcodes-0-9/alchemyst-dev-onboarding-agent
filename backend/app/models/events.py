from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class TokenEvent(BaseModel):
    type: Literal["token"] = "token"
    text: str


class StageUpdateEvent(BaseModel):
    type: Literal["stage_update"] = "stage_update"
    stage: str
    integration: dict


class CodeEvent(BaseModel):
    type: Literal["code"] = "code"
    snippet: str
    language: str


class DoneEvent(BaseModel):
    type: Literal["done"] = "done"
    sessionId: str


class ErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str