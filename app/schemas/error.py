
from typing import Annotated, Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
