from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional

class PlanEnum(str, Enum):
    basic = "basic"   # free
    pro = "pro"
    ultra = "ultra"

class EmailCheckRequest(BaseModel):
    email: EmailStr
    plan: PlanEnum  # free or basic now

class EmailCheckResponse(BaseModel):
    valid: bool
    domain: str
    is_disposable: bool
    mx_found: Optional[bool] = None
    domain_score: Optional[int] = None
    plan: PlanEnum