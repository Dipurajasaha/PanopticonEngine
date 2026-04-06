import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

ALLOWED_ROLES = {
    "viewer": "Viewer",
    "analyst": "Analyst",
    "admin": "Admin",
}

ALLOWED_RECORD_TYPES = {
    "income": "Income",
    "expense": "Expense",
}

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


#############################################################################
# -- User Schemas --
#############################################################################
class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "Viewer"

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized or not EMAIL_REGEX.match(normalized):
            raise ValueError("A valid email is required")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 6:
            raise ValueError("Password must be at least 6 characters")
        return cleaned

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_ROLES:
            raise ValueError("Role must be one of: Viewer, Analyst, Admin")
        return ALLOWED_ROLES[normalized]

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_ROLES:
            raise ValueError("Role must be one of: Viewer, Analyst, Admin")
        return ALLOWED_ROLES[normalized]



#############################################################################
# -- Finance Record Schemas --
#############################################################################
class RecordCreate(BaseModel):
    amount: float = Field(gt=0)
    record_type: str
    category: str
    description: Optional[str] = None

    @field_validator("record_type")
    @classmethod
    def validate_record_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_RECORD_TYPES:
            raise ValueError("record_type must be either 'Income' or 'Expense'")
        return ALLOWED_RECORD_TYPES[normalized]

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("category must be at least 2 characters")
        return cleaned

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

class RecordResponse(BaseModel):
    amount: float
    record_type: str
    category: str
    description: Optional[str] = None
    id: int
    created_at: datetime
    is_deleted: bool
    owner_id: int

    class Config:
        from_attributes = True


#############################################################################
# -- Analytics Schemas --
#############################################################################
class CategorySummary(BaseModel):
    category: str
    total_amount: float

class AnalyticsDashboard(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    category_breakdown: List[CategorySummary]