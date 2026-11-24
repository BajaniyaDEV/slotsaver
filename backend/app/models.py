"""Database tables.

Check-in 1 uses patients, appointments and predictions.
Later tables (waitlist, reminders, action_log, policy_chunks, agent_runs) are added by their owners.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))  # synthetic, never a real person
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(1))  # "F" or "M" (as in the Kaggle data)
    preferred_language: Mapped[str] = mapped_column(String(30), default="English")
    sms_consent: Mapped[bool] = mapped_column(Boolean, default=True)
    scholarship: Mapped[bool] = mapped_column(Boolean, default=False)  # welfare enrolment
    hypertension: Mapped[bool] = mapped_column(Boolean, default=False)
    diabetes: Mapped[bool] = mapped_column(Boolean, default=False)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    booked_at: Mapped[datetime] = mapped_column(DateTime)
    appointment_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    visit_type: Mapped[str] = mapped_column(String(50))
    provider: Mapped[str] = mapped_column(String(100))
    # booked, confirmed, cancelled, attended, no_show
    status: Mapped[str] = mapped_column(String(20), default="booked")

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="appointment", order_by="Prediction.created_at.desc()"
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id"), index=True)
    risk_score: Mapped[float] = mapped_column(Float)  # probability of no-show, 0 to 1
    risk_band: Mapped[str] = mapped_column(String(10))  # low, medium, high
    top_reasons: Mapped[list] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    appointment: Mapped[Appointment] = relationship(back_populates="predictions")
