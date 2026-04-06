from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# -- user schemas --
class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "Viewer"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: str



# -- finance record  schemas --
class RecordCreate(BaseModel):
    amount: float
    record_type: str
    category: str
    description: Optional[str] = None

class RecordResponse(RecordCreate):
    id: int
    created_at: datetime
    is_deleted: bool
    owner_id: int

    class Config:
        from_attributes = True


# -- analytics schemas --
class CategorySummary(BaseModel):
    category: str
    total_amount: float

class AnalyticsDashboard(BaseModel):
    total_income: float
    total_expense: float
    net_balance: float
    category_breakdown: List[CategorySummary]