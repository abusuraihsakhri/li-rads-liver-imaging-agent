# Li Rads Liver Imaging Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI
> **Reference Guidelines & Standards:** `American College of Radiology (ACR) LI-RADS v2018 & Fleischner Society`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Li Rads Liver Imaging Agent** is a clinical decision support tool implementing ACR LI-RADS v2018 criteria for categorizing liver observations in patients at risk for hepatocellular carcinoma (HCC). It provides:

- **LI-RADS v2018 Categorization** — Automated scoring of liver observations (LR-NC, LR-1 through LR-5, LR-M, LR-TIV)
- **Multi-Agent Audit System** — Distributed clinical surveillance with PHI protection
- **FastAPI REST API** — OpenAPI endpoints for integration with clinical workflows
- **HMAC-SHA256 Audit Trail** — Tamper-evident cryptographic logging

---

## Quickstart

### Installation

```bash
pip install -e .
```

### CLI Usage

**Categorize a liver observation:**
```bash
python cli.py categorize --size 20 --modality CT --ahe --washout
```

**Get category information:**
```bash
python cli.py info
python cli.py info 5
```

**JSON output:**
```bash
python cli.py categorize --size 15 --ahe --capsule --json
```

### Parameters

| Parameter | Type | Description |
|:----------|:-----|:------------|
| `--size` | float | Observation size in mm (required) |
| `--modality` | CT/MRI/US | Imaging modality (default: CT) |
| `--ahe` | flag | Arterial hyperenhancement present |
| `--washout` | flag | Non-peripheral washout present |
| `--capsule` | flag | Enhancing capsule present |
| `--growth` | flag | Threshold growth (>=50% in <=6 months) |
| `--prior-size` | float | Prior observation size in mm |
| `--prior-months` | float | Months since prior scan |
| `--tumor-in-vein` | flag | Tumor in vein present |
| `--definitely-benign` | flag | Observation is definitely benign |
| `--malignancy-not-hcc` | flag | Features suggest malignancy not HCC |

---

## LI-RADS Categories

| Category | Description | Treatment Eligible |
|:---------|:------------|:-------------------|
| LR-NC | Not categorizable | No |
| LR-1 | Definitely benign | No |
| LR-2 | Probably benign | No |
| LR-3 | Intermediate probability | No |
| LR-4 | Probably HCC | Case-by-case |
| LR-5 | Definitely HCC | Yes |
| LR-M | Probably malignancy (not HCC) | No |
| LR-TIV | Tumor in vein | Yes |

---

## Architecture

### Core Modules

- **`li_rads_liver_imaging_agent/engine.py`** — LI-RADS v2018 categorization algorithm
- **`li_rads_liver_imaging_agent/models.py`** — Data models (LiverObservation, LIRADSResult)
- **`agents/supervisor.py`** — Multi-agent orchestration system
- **`agents/base.py`** — PHI guard, HMAC-SHA256 audit trail, security utilities

### Security Features

- **Zero-PHI Outbound Guard:** AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers
- **HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation
- **Configurable Secret Key:** Set `AUDIT_SECRET_KEY` environment variable for production deployments

### FastAPI Server

```bash
python li_rads_liver_imaging_agent/cli.py serve --host 127.0.0.1 --port 8000
```

Endpoints:
- `GET /health` — Health check
- `POST /api/audit` — Submit case for audit
- `POST /api/chat` — Query clinical assistant

---

## Testing

Run the full test suite:

```bash
pytest -v
```

Run with coverage:

```bash
pytest -v --cov=li_rads_liver_imaging_agent --cov=agents
```

---

## Docker Deployment

```bash
docker build -t li-rads-liver-imaging-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key li-rads-liver-imaging-agent
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
