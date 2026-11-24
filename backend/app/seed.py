"""Fill the database with SYNTHETIC demo data (no real people).

Run from the repo root:
    python -m backend.app.seed                 # fresh data, no risk scores yet
    python -m backend.app.seed --demo-scores   # also add PLACEHOLDER scores so the UI can show risk badges

Placeholder scores are random and labelled model_version="placeholder-v0".
They are only for building the frontend until the real model (ml/) is served.
"""

import argparse
import random
from datetime import date, datetime, time, timedelta

from .database import Base, SessionLocal, engine
from .models import Appointment, Patient, Prediction

FIRST_NAMES = [
    "Aisha", "Ben", "Carmen", "Daniel", "Elena", "Farid", "Grace", "Hiro", "Isabel", "Jun",
    "Karan", "Lina", "Marco", "Nadia", "Omar", "Priya", "Quinn", "Rosa", "Sanjay", "Tara",
    "Uma", "Victor", "Wei", "Ximena", "Yusuf", "Zara",
]
LAST_NAMES = [
    "Ahmed", "Brown", "Chen", "Dubois", "Evans", "Fernandez", "Gill", "Hassan", "Ito", "Joseph",
    "Kaur", "Lopez", "Martin", "Nguyen", "Okafor", "Patel", "Reyes", "Singh", "Tremblay", "Wong",
]
LANGUAGES = (
    ["English"] * 10 + ["French"] * 3 + ["Punjabi"] * 2 + ["Mandarin"] * 2
    + ["Arabic"] * 2 + ["Spanish"] * 2 + ["Tagalog"]
)
VISIT_TYPES = ["Follow-up", "New patient", "Chronic care", "Vaccination", "Lab review", "Prenatal"]
PROVIDERS = ["Dr. Rivera", "Dr. Okoye", "Dr. Lam", "NP Morgan"]
REASONS = [
    "Booked many days ahead",
    "Missed earlier appointments",
    "Younger patient",
    "First visit at this clinic",
    "Monday appointment",
    "No reminder confirmed yet",
]


def make_patients(rng: random.Random, n: int) -> list[Patient]:
    patients = []
    for i in range(n):
        patients.append(
            Patient(
                id=i + 1,
                display_name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
                age=rng.randint(1, 90),
                gender=rng.choice(["F", "M"]),
                preferred_language=rng.choice(LANGUAGES),
                sms_consent=rng.random() > 0.1,
                scholarship=rng.random() < 0.1,
                hypertension=rng.random() < 0.2,
                diabetes=rng.random() < 0.07,
            )
        )
    return patients


def make_appointments(
    rng: random.Random, patients: list[Patient], per_day: dict[date, int]
) -> list[Appointment]:
    appts = []
    next_id = 1
    for day, count in per_day.items():
        for _ in range(count):
            slot = time(hour=rng.randint(8, 16), minute=rng.choice([0, 15, 30, 45]))
            appointment_at = datetime.combine(day, slot)
            lead = rng.choice([0, 1, 2, 3, 7, 10, 14, 21, 30, 45, 60])
            appts.append(
                Appointment(
                    id=next_id,
                    patient_id=rng.choice(patients).id,
                    booked_at=appointment_at - timedelta(days=lead, hours=rng.randint(1, 8)),
                    appointment_at=appointment_at,
                    visit_type=rng.choice(VISIT_TYPES),
                    provider=rng.choice(PROVIDERS),
                    status="booked",
                )
            )
            next_id += 1
    return appts


def make_placeholder_scores(rng: random.Random, appts: list[Appointment]) -> list[Prediction]:
    preds = []
    for a in appts:
        score = round(rng.betavariate(2, 6), 3)  # mostly low, a few high, like real no-show rates
        band = "high" if score >= 0.4 else "medium" if score >= 0.2 else "low"
        preds.append(
            Prediction(
                appointment_id=a.id,
                risk_score=score,
                risk_band=band,
                top_reasons=rng.sample(REASONS, 3),
                model_version="placeholder-v0",
            )
        )
    return preds


def seed(demo_scores: bool = False, seed_value: int = 42) -> dict:
    rng = random.Random(seed_value)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    today = date.today()
    per_day = {
        today - timedelta(days=1): 20,
        today: 30,
        today + timedelta(days=1): 60,  # "tomorrow" = the demo board
        today + timedelta(days=2): 30,
    }
    patients = make_patients(rng, 120)
    appts = make_appointments(rng, patients, per_day)
    preds = make_placeholder_scores(rng, appts) if demo_scores else []

    with SessionLocal() as db:
        db.add_all(patients)
        db.add_all(appts)
        db.add_all(preds)
        db.commit()
    return {"patients": len(patients), "appointments": len(appts), "predictions": len(preds)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the database and load synthetic demo data.")
    parser.add_argument("--demo-scores", action="store_true", help="add placeholder risk scores")
    args = parser.parse_args()
    counts = seed(demo_scores=args.demo_scores)
    print(f"Seeded {counts['patients']} patients, {counts['appointments']} appointments, "
          f"{counts['predictions']} placeholder predictions.")
