from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class EmployeeBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    seniority: Optional[str] = None

    years_experience: Optional[float] = Field(
        default=None,
        ge=0
    )

    performance_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    current_workload_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    availability_pct: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    available_from: Optional[str] = None

    critical_project_experience: Optional[int] = Field(
        default=None,
        ge=0
    )


class EmployeeCreate(EmployeeBase):
    # Optional: the API generates one (EMP000123) when omitted.
    employee_id: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    # employees.employee_id is String(100) in the database ("EMP001"),
    # so this must be str. It was previously typed int, which made
    # every /employees/ response fail Pydantic validation with a 500.
    employee_id: str

    model_config = ConfigDict(from_attributes=True)
