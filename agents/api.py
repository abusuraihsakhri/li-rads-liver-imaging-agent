"""
FastAPI REST API Server for Li Rads Liver Imaging Agent.
"""
import os
import hmac
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
from li_rads_liver_imaging_agent.models import LiverObservation
from li_rads_liver_imaging_agent.engine import categorize

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Li Rads Liver Imaging Agent API",
    description="Rule-based CT/MRI LI-RADS v2018 categorization and optional illustrative audit API",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


class ObservationRequest(BaseModel):
    observation_id: str = "OBS-1"
    size_mm: float
    modality: str = "CT"
    arterial_hyperenhancement: bool = False
    non_peripheral_washout: bool = False
    enhancing_capsule: bool = False
    threshold_growth: bool = False
    prior_size_mm: Optional[float] = None
    prior_months: Optional[float] = None
    has_at_risk_liver: bool = True
    is_imaging_adequate: bool = True
    has_tumor_in_vein: bool = False
    is_definitely_benign: bool = False
    is_probably_benign: bool = False
    has_malignancy_not_hcc: bool = False
    ancillary_favoring_malignancy: List[str] = Field(default_factory=list)
    ancillary_favoring_benignity: List[str] = Field(default_factory=list)


_WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(_WEB_DIR / "index.html")


@app.get("/li-rads.mjs", include_in_schema=False)
def browser_engine():
    return FileResponse(_WEB_DIR / "li-rads.mjs", media_type="text/javascript")


@app.post("/api/categorize")
def api_categorize(payload: ObservationRequest):
    try:
        return categorize(LiverObservation(**payload.model_dump())).to_dict()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "li-rads-liver-imaging-agent", "domain": "LI-RADS categorization and illustrative audit", "standard": "CT/MRI LI-RADS v2018 for /api/categorize", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "RUNNING"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail="Sensitive identifier detected; use de-identified input.") from exc
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as exc:
        raise HTTPException(status_code=400, detail="Sensitive identifier detected; use de-identified input.") from exc


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None)):
    """Audit records are inaccessible until a separate read token is configured."""
    configured = os.getenv("AUDIT_READ_TOKEN", "")
    if not configured or not x_audit_token or not hmac.compare_digest(configured, x_audit_token):
        raise HTTPException(status_code=403, detail="Audit-log access denied")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
