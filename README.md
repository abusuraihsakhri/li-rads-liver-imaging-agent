# LI-RADS Liver Imaging Agent

> **ACR LI-RADS v2018** liver observation categorization tool.

## Overview

Implements LI-RADS (Liver Imaging Reporting and Data System) for categorizing liver observations in patients at risk for hepatocellular carcinoma (HCC). Applies major features (arterial hyperenhancement, washout, enhancing capsule, threshold growth) and size thresholds to assign categories LR-1 through LR-5, LR-M, and LR-TIV.

## LI-RADS Categories

| Category | Label | Description |
|----------|-------|-------------|
| **LR-NC** | Not categorizable | Inadequate imaging |
| **LR-1** | Definitely benign | Cyst, hemangioma, etc. |
| **LR-2** | Probably benign | <10mm without features |
| **LR-3** | Intermediate | Equivocal probability |
| **LR-4** | Probably HCC | AHE without washout/capsule/growth |
| **LR-5** | Definitely HCC | >=10mm + AHE + (washout OR growth OR capsule) |
| **LR-M** | Malignancy, not HCC-specific | Features suggest cholangiocarcinoma |
| **LR-TIV** | Tumor in vein | Enhancing soft tissue in vein |

## LR-5 Criteria

For observations >=10mm in at-risk liver:
- **Required**: Arterial hyperenhancement (AHE)
- **Plus one or more**: Non-peripheral washout, threshold growth (>=50% in <=6 months), enhancing capsule

## Treatment Eligibility

- **LR-5**: Eligible for HCC treatment without biopsy
- **LR-TIV**: Eligible for HCC treatment
- **LR-4**: Consider biopsy or short-interval follow-up

## CLI Usage

```bash
# Categorize a typical LR-5 observation
python cli.py categorize --size 20 --ahe --washout --capsule

# Categorize with growth
python cli.py categorize --size 15 --ahe --growth --prior-size 8 --prior-months 4

# Categorize a benign observation
python cli.py categorize --size 8 --definitely-benign

# Categorize LR-M
python cli.py categorize --size 25 --ahe --malignancy-not-hcc

# JSON output
python cli.py categorize --size 20 --ahe --washout --json

# Show category info
python cli.py info
python cli.py info 5
```

## Python API

```python
from li_rads_liver_imaging_agent import LiverObservation, Modality, categorize

obs = LiverObservation(
    observation_id="obs_1",
    size_mm=20,
    modality=Modality.CT,
    arterial_hyperenhancement=True,
    non_peripheral_washout=True,
    enhancing_capsule=True,
)

result = categorize(obs)
print(f"Category: {result.category.value}")
print(f"Treatment eligible: {result.treatment_eligible}")
```

## Testing

```bash
python -m pytest tests/ -v
```

## License

MIT License. See [LICENSE](LICENSE).
