from pydantic import BaseModel, field_validator
from datetime import date
from typing import ClassVar
from datetime import datetime

# ---------- Request Models ----------
class VisitRecord(BaseModel):
    date_format: ClassVar[str] = "%Y-%m-%d"
    
    mrn: str
    first_name: str
    last_name: str
    birth_date: date
    visit_account_number: str
    visit_date: date
    reason: str
    
    @field_validator('birth_date')
    @classmethod
    def validate_birth(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, cls.date_format).date()
        return v
    
    @field_validator('visit_date')
    @classmethod
    def validate_visit(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, cls.date_format).date()
        return v