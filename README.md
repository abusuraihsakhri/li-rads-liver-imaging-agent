# Li Rads Liver Imaging Agent

> **Domain:** Diagnostic Radiology & Medical Imaging AI  
> **Reference Guidelines & Standards:** `American College of Radiology (ACR) RADS & Fleischner Society`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Li Rads Liver Imaging Agent** is an advanced analytical and computational platform implementing Cirrhotic Liver Nodule LI-RADS v2018 Enhancement Kinetics.

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Algorithmic & Evaluation Engines

- **`Severity`** — dedicated module for severity evaluation and state verification.
- **`DomainKnowledgeRegistry`**: Enterprise domain rules, guideline matrices, and evidence benchmarks.
- **`AgentAlert`** — dedicated module for agent alert evaluation and state verification.
- **`EnhancementKineticsAgent`**: Specialized Sub-Agent 1 for li-rads-liver-imaging-agent
- **`MajorFeatureCounterAgent`**: Specialized Sub-Agent 2 for li-rads-liver-imaging-agent
- **`LIRADSCategoryMatcherAgent`**: Specialized Sub-Agent 3 for li-rads-liver-imaging-agent

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --size <value> --modality <value> --ahe <value> --washout <value>
```

### Parameter Reference
- `--size`: Specifies input measurement or parameter value.
- `--modality`: Specifies input measurement or parameter value.
- `--ahe`: Specifies input measurement or parameter value.
- `--washout`: Specifies input measurement or parameter value.
- `--capsule`: Specifies input measurement or parameter value.
- `--growth`: Specifies input measurement or parameter value.
- `--prior-size`: Specifies input measurement or parameter value.
- `--prior-months`: Specifies input measurement or parameter value.
- `--tumor-in-vein`: Specifies input measurement or parameter value.
- `--definitely-benign`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `case_id` | Parameter / observation metric | Required |
| `patient_synthetic_id` | Parameter / observation metric | Required |
| `metric_primary` | Parameter / observation metric | Required |
| `metric_secondary` | Parameter / observation metric | Required |
| `is_stat` | Parameter / observation metric | Required |
| `status_flag` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t li-rads-liver-imaging-agent .
docker run -p 8000:8000 li-rads-liver-imaging-agent
```
