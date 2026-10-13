# CT/MRI LI-RADS v2018 Liver Imaging Decision Aid

An educational decision aid for categorizing **untreated hepatic observations** using the American College of Radiology (ACR) CT/MRI LI-RADS v2018 diagnostic table. Rules are implemented in Python and in a standalone JavaScript browser application.

> **Clinical scope:** Use CT/MRI LI-RADS only for eligible HCC high-risk populations with adequate multiphase CT/MRI. This is not a validated medical device. Treated or path-proven observations need a different pathway. Diagnosis, treatment, and transplant eligibility require clinical and radiologist assessment.

**Reference:** [ACR CT/MRI LI-RADS v2018 Core](https://cs.acr.org/-/media/ACR/NOINDEX/RADS/LI-RADS-2018-Core.pdf), diagnostic algorithm and ancillary features (pages 8–10).

## Features

- LR-NC, LR-1, LR-2, LR-3, LR-4, LR-5, LR-M and LR-TIV categories.
- Size, nonrim arterial enhancement, nonperipheral washout, enhancing capsule, and threshold growth (≥50% in ≤6 months).
- Optional one-level ancillary adjustments, never upgrading to LR-5.
- Validations for measurements, modality, risk population, and prior imaging.
- Browser-based categorization and JSON export without a backend, external API or persistent browser storage.
- Python CLI, optional FastAPI service, and a separate illustrative audit subsystem.

## Use in the browser

Open **web/index.html** in a modern browser or run:

~~~bash
python -m http.server 8080 --directory web
~~~

Visit http://127.0.0.1:8080/, enter observation features, and select **Categorize observation**. Data stay in the browser. Python, Pyodide, and server-side processing are not required.

## Python CLI

Requires Python 3.9 or later.

~~~bash
python cli.py categorize --size 15 --modality CT --ahe --capsule
python cli.py categorize --size 15 --ahe --washout --json
python cli.py categorize --size 12 --inadequate-imaging
python cli.py info 5
~~~

The first example assigns **LR-4** (15 mm, APHE and capsule alone); the second assigns **LR-5** (15 mm, APHE and washout). Invalid or noneligible observations result in errors instead of a category.

~~~python
from li_rads_liver_imaging_agent import LiverObservation, categorize

observation = LiverObservation(
    observation_id="OBS-1",
    size_mm=15,
    arterial_hyperenhancement=True,
    enhancing_capsule=True,
)
print(categorize(observation).to_dict()["category"])  # LR-4
~~~

## Optional Python API

~~~bash
python -m pip install -e ".[server,test]"
uvicorn agents.api:app --host 127.0.0.1 --port 8000
~~~

The browser UI is served at http://127.0.0.1:8000/. REST routes:

| Endpoint | Description |
| --- | --- |
| GET /health | Basic service health |
| POST /api/categorize | LI-RADS v2018 categorization from JSON |
| POST /api/audit | Demonstration-only multi-worker threshold audit |
| POST /api/chat | Deterministic mock response, not a medical language model |
| GET /metrics | In-memory audit metrics |
| GET /api/audit/logs | HMAC audit chain; requires AUDIT_READ_TOKEN and X-Audit-Token header |

~~~bash
curl -fsS http://127.0.0.1:8000/api/categorize \
  -H 'Content-Type: application/json' \
  -d '{"observation_id":"OBS-1","size_mm":15,"arterial_hyperenhancement":true,"enhancing_capsule":true}'
~~~

**The separate generic audit workers are illustrative**, not validated clinical LI-RADS assessment rules or laboratory thresholds.

## Docker and privacy

~~~bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
~~~

Docker Compose binds port 8000 to localhost. Configure HTTPS and authentication before exposing the API publicly.

**Privacy:** The standalone browser app does not transmit or persist observation inputs. The Python audit service stores dossiers and an HMAC-signed log in process memory only. The audit chain does not survive restarts or constitute regulatory validation. Its regex-based identifier screening cannot guarantee removal of all PHI. Use only synthetic or de-identified inputs. The default mock subsystem makes no external LLM requests.

## Tests

~~~bash
python -m pip install -e ".[test]"
python -m pytest -q
node --test web/li-rads.test.mjs
~~~

CI covers Python 3.10–3.12 and Node.js 22. The browser app uses standard JavaScript ES modules.

## License

[MIT](LICENSE).
