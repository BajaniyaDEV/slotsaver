"""API tests for the check-in 1 slice: /health and /appointments."""

from .conftest import TOMORROW


def test_health_reports_database_ok(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_appointments_default_to_tomorrow(client):
    res = client.get("/appointments")
    assert res.status_code == 200
    body = res.json()
    assert body["date"] == TOMORROW.isoformat()
    assert body["count"] == 2  # appointment 3 is on another day


def test_appointments_sorted_highest_risk_first(client):
    body = client.get(f"/appointments?date={TOMORROW.isoformat()}").json()
    scores = [a["risk_score"] for a in body["appointments"]]
    assert scores == sorted(scores, reverse=True)
    assert body["appointments"][0]["risk_band"] == "high"


def test_min_risk_filter(client):
    body = client.get(f"/appointments?date={TOMORROW.isoformat()}&min_risk=0.5").json()
    assert body["count"] == 1
    assert body["appointments"][0]["id"] == 2


def test_bad_date_gives_clear_422(client):
    res = client.get("/appointments?date=2026-13-45")
    assert res.status_code == 422
    body = res.json()
    assert body["error"] == "invalid_input"
    assert any("date" in msg for msg in body["detail"])


def test_min_risk_out_of_range_rejected(client):
    res = client.get("/appointments?min_risk=1.5")
    assert res.status_code == 422
    assert res.json()["error"] == "invalid_input"


def test_unknown_appointment_returns_404(client):
    res = client.get("/appointments/9999")
    assert res.status_code == 404
    assert res.json() == {"error": "not_found", "detail": "Appointment 9999 not found"}


def test_appointment_detail_includes_patient_and_lead_time(client):
    body = client.get("/appointments/1").json()
    assert body["patient_name"] == "Test Patient A"
    assert body["preferred_language"] == "French"
    assert body["lead_days"] == 20
