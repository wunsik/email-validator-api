from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional


class PlanEnum(str, Enum):
    basic = "basic"   # Basic plan: Disposable email check only
    pro = "pro"       # Pro plan: Includes MX record validation
    ultra = "ultra"   # Ultra plan: Includes domain trust scoring


class EmailCheckRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com", description="Email address to validate")


class EmailCheckResponse(BaseModel):
    valid: bool = Field(..., example=True, description="Whether the email format is valid")
    domain: str = Field(..., example="gmail.com", description="Extracted domain from the email address")
    is_disposable: bool = Field(..., example=False, description="True if the domain is a known disposable email provider")
    mx_found: Optional[bool] = Field(None, example=True, description="True if MX records are found (only for pro and ultra plans)")
    domain_score: Optional[int] = Field(None, example=85, description="Trust score of the domain (only for ultra plan)")
    plan: PlanEnum = Field(..., example="basic", description="The plan type associated with the request")
