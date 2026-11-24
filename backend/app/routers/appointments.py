"""Appointment endpoints: the day's schedule and one appointment."""

from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from ..database import get_db
from ..models import Appointment
from ..schemas import AppointmentList, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])


def to_out(appt: Appointment) -> AppointmentOut:
    latest = appt.predictions[0] if appt.predictions else None
    return AppointmentOut(
        id=appt.id,
        patient_id=appt.patient_id,
        patient_name=appt.patient.display_name,
        preferred_language=appt.patient.preferred_language,
        appointment_at=appt.appointment_at,
        booked_at=appt.booked_at,
        lead_days=(appt.appointment_at.date() - appt.booked_at.date()).days,
        visit_type=appt.visit_type,
        provider=appt.provider,
        status=appt.status,
        risk_score=latest.risk_score if latest else None,
        risk_band=latest.risk_band if latest else None,
        top_reasons=latest.top_reasons if latest else [],
    )


@router.get("", response_model=AppointmentList)
def list_appointments(
    day: date | None = Query(
        None, alias="date", description="Day to show, YYYY-MM-DD. Defaults to tomorrow."
    ),
    min_risk: float | None = Query(
        None, ge=0, le=1, description="Only appointments with risk score at or above this (0 to 1)."
    ),
    db: Session = Depends(get_db),
):
    day = day or (date.today() + timedelta(days=1))
    start = datetime.combine(day, time.min)
    end = start + timedelta(days=1)

    stmt = (
        select(Appointment)
        .options(joinedload(Appointment.patient), selectinload(Appointment.predictions))
        .where(Appointment.appointment_at >= start, Appointment.appointment_at < end)
        .order_by(Appointment.appointment_at)
    )
    items = [to_out(a) for a in db.scalars(stmt).unique()]

    if min_risk is not None:
        items = [a for a in items if a.risk_score is not None and a.risk_score >= min_risk]

    # Highest risk first; unscored appointments keep time order at the end.
    items.sort(key=lambda a: (a.risk_score is None, -(a.risk_score or 0), a.appointment_at))
    return AppointmentList(date=day, count=len(items), appointments=items)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appt = db.get(
        Appointment,
        appointment_id,
        options=[joinedload(Appointment.patient), selectinload(Appointment.predictions)],
    )
    if appt is None:
        raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    return to_out(appt)
