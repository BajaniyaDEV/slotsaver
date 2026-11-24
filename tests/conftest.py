"""Test setup: every test gets a fresh in-memory SQLite database with a few known rows.

No PostgreSQL, API keys or network are needed, so these run the same in CI and on a laptop.
"""

import os
from datetime import date, datetime, time, timedelta

os.environ.setdefault("DATABASE_URL", "sqlite://")  # before the app is imported
os.environ.setdefault("LOG_DIR", "logs")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from backend.app.database import Base, get_db  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.models import Appointment, Patient, Prediction  # noqa: E402

TOMORROW = date.today() + timedelta(days=1)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()

    session.add_all([
        Patient(id=1, display_name="Test Patient A", age=30, gender="F", preferred_language="French"),
        Patient(id=2, display_name="Test Patient B", age=55, gender="M", preferred_language="English"),
    ])
    at_9 = datetime.combine(TOMORROW, time(9, 0))
    at_14 = datetime.combine(TOMORROW, time(14, 0))
    session.add_all([
        Appointment(id=1, patient_id=1, booked_at=at_9 - timedelta(days=20), appointment_at=at_9,
                    visit_type="Follow-up", provider="Dr. Test"),
        Appointment(id=2, patient_id=2, booked_at=at_14 - timedelta(days=1), appointment_at=at_14,
                    visit_type="Lab review", provider="Dr. Test"),
        Appointment(id=3, patient_id=2, booked_at=at_9 - timedelta(days=5),
                    appointment_at=at_9 + timedelta(days=3), visit_type="Follow-up", provider="Dr. Test"),
    ])
    session.add_all([
        Prediction(appointment_id=1, risk_score=0.15, risk_band="low", top_reasons=[], model_version="test"),
        Prediction(appointment_id=2, risk_score=0.65, risk_band="high",
                   top_reasons=["Missed earlier appointments"], model_version="test"),
    ])
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
