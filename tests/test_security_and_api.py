"""Security and HTTP regression tests for the clinical decision aid."""
import os

from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail

client = TestClient(app)


def test_audit_log_tamper_detection():
    trail = AuditTrail(secret_key="only-for-test")
    trail.log("tester", "worker", "evaluation", {"status": "ok"})
    assert trail.verify_integrity()
    trail.logs[0]["actor"] = "altered"
    assert not trail.verify_integrity()


def test_audit_log_chain_tamper_detection():
    trail = AuditTrail(secret_key="only-for-test")
    trail.log("tester", "worker", "evaluation", {"status": "ok"})
    trail.log("tester", "worker", "evaluation", {"status": "ok"})
    assert trail.verify_integrity()
    trail.logs[1]["prev_hash"] = "altered"
    assert not trail.verify_integrity()


def test_readers_cannot_modify_audit_trail():
    trail = AuditTrail(secret_key="only-for-test")
    trail.log("tester", "worker", "evaluation", {"status": "ok"})
    trail.get_trail()[0]["actor"] = "untrusted"
    assert trail.verify_integrity()


def test_audit_logs_denied_without_read_token(monkeypatch):
    monkeypatch.delenv("AUDIT_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 403


def test_audit_logs_require_correct_token(monkeypatch):
    monkeypatch.setenv("AUDIT_READ_TOKEN", "integration-only-token")
    assert client.get("/api/audit/logs", headers={"x-audit-token": "wrong"}).status_code == 403
    assert client.get("/api/audit/logs", headers={"x-audit-token": "integration-only-token"}).status_code == 200


def test_clinical_endpoint_uses_same_v2018_rules():
    response = client.post("/api/categorize", json={
        "size_mm": 15, "arterial_hyperenhancement": True, "enhancing_capsule": True
    })
    assert response.status_code == 200
    assert response.json()["category"] == "LR-4"
    response = client.post("/api/categorize", json={
        "size_mm": 15, "arterial_hyperenhancement": True,
        "non_peripheral_washout": True
    })
    assert response.json()["category"] == "LR-5"


def test_clinical_endpoint_rejects_noneligible_population():
    response = client.post("/api/categorize", json={"size_mm": 15, "has_at_risk_liver": False})
    assert response.status_code == 422


def test_audit_endpoint_rejects_sensitive_identifiers():
    response = client.post("/api/audit", json={
        "task_id": "CASE-123", "target_identifier": "MRN-123456",
        "primary_metric": 10
    })
    assert response.status_code == 400
    assert "MRN-123456" not in response.text


def test_static_browser_application_is_served():
    home = client.get("/")
    module = client.get("/li-rads.mjs")
    assert home.status_code == 200
    assert 'id="assessment-form"' in home.text
    assert module.status_code == 200
    assert "export function categorize" in module.text
