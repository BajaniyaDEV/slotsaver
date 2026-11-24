"""Request and response shapes (Pydantic)."""

from datetime import date, datetime

from pydantic import BaseModel


class HealthOut(BaseModel):
    status: str
    database: str
    model: str


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    preferred_language: str
    appointment_at: datetime
    booked_at: datetime
    lead_days: int
    visit_type: str
    provider: str
    status: str
    risk_score: float | None = None
    risk_band: str | None = None
    top_reasons: list[str] = []


class AppointmentList(BaseModel):
    date: date
    count: int
    appointments: list[AppointmentOut]


class ErrorOut(BaseModel):
    error: str
    detail: str | list | None = None
