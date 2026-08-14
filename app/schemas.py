from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
# Schemas

# Employee

class EmployeeBase(BaseModel):
    username: str = Field(..., min_length=1)

    @field_validator("username")
    def username_must_not_be_blank(cls, v: str):
        if not v or not v.strip():
            raise ValueError("username cannot be empty or blank")
        return v.strip()

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

# Case
class CaseResponse(BaseModel):
    id: int
    patientName: str
    modality: str
    studyDate: date
    status: str
    report: Optional[str] = None
    claimedAt: Optional[datetime] = None
    claimedBy: Optional[str] = None # Returns Username

    class Config:
        from_attributes = True

class ClaimCaseRequest(BaseModel):
    claimedBy: str = Field(...,min_length=1)

class SubmitReportRequest(BaseModel):
    author: str = Field(...,min_length=1)
    report: str = Field(...,min_length=1)
