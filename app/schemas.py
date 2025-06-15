from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailCheckRequest(BaseModel):
    email: EmailStr
    plan: str = "free"  # free or basic

class EmailCheckResponse(BaseModel):
    valid: bool
    domain: str
    is_disposable: bool
    mx_found: Optional[bool] = None
    domain_score: Optional[int] = None
    plan: str