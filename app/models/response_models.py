from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from app.models.request_models import VisitRecord

# ---------- Response Models ----------
class GroupedVisits(BaseModel):
    mrn: str
    first_name: str
    last_name: str
    birth_date: str
    visits: List[VisitRecord]


class IngestResponse(BaseModel):
    status: str
    message: str
    local_path: str
    s3_location: str


class VisitResponse(BaseModel):
    visit_account_number: str
    visit_date: date
    reason: Optional[str]

class PersonResponse(BaseModel):
    first_name: str
    last_name: str
    birth_date: date

class PatientResponse(BaseModel):
    id: int
    mrn: str
    created_at: datetime
    person: PersonResponse
    visits: List[VisitResponse]

    class Config:
        orm_mode = True


class PaginatedPatientResponse(BaseModel):
    page: int
    size: int
    total: int
    patients: List[PatientResponse]