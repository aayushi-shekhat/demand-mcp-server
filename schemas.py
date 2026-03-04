from pydantic import BaseModel, validator
from datetime import date
from typing import Optional


class CreateDemand(BaseModel):

    project_name: str
    crm_id: str
    probability: Optional[int] = None
    grade: Optional[str] = None
    start_date: date
    end_date: date
    fte: int
    platform_type: str                        # MUST be exactly "EBS" or "Fusion"
    competency_track: Optional[str] = None
    primary_mandatory_skill: str
    good_to_have_skill: Optional[str] = None
    monthly_billing_rate_usd: float
    minimum_gm_percent: float
    specific_certification_required: Optional[bool] = False
    client_interview_flag: Optional[bool] = False
    job_description: Optional[str] = None
    required_count: Optional[int] = 1

    @validator("platform_type")
    def validate_platform_type(cls, v):
        allowed = ["EBS", "Fusion"]
        if v not in allowed:
            raise ValueError(f"platform_type must be one of {allowed} (exact case)")
        return v


class UpdateDemand(BaseModel):

    status: str    # Must be: Draft | Internal | External | Partial | Fulfilled | Closed

    @validator("status")
    def validate_status(cls, v):
        allowed = ["Draft", "Internal", "External", "Partial", "Fulfilled", "Closed"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v