"""
LI-RADS Engine: ACR LI-RADS v2018 categorization for liver observations.

Implements LI-RADS for categorizing liver observations in patients at risk
for hepatocellular carcinoma (HCC).

Categories:
  LR-NC: Not categorizable
  LR-1: Definitely benign
  LR-2: Probably benign
  LR-3: Intermediate probability of malignancy
  LR-4: Probably HCC
  LR-5: Definitely HCC
  LR-M: Probably malignancy, not necessarily HCC
  LR-TIV: Tumor in vein

LR-5 criteria and all other category decisions follow the ACR CT/MRI diagnostic table.
These results are for decision support and do not establish treatment eligibility.

Reference: ACR CT/MRI LI-RADS v2018, diagnostic algorithm page 8.
"""
from typing import List, Dict, Any
from .models import LiverObservation, LIRADSCategory, LIRADSResult, Modality


# Category metadata
CATEGORY_INFO: Dict[LIRADSCategory, Dict[str, str]] = {
    LIRADSCategory.LR_NC: {
        "label": "Not categorizable",
        "description": "Observation not categorizable due to inadequate imaging or omission of required sequences.",
    },
    LIRADSCategory.LR_1: {
        "label": "Definitely benign",
        "description": "Definitely benign observation (e.g., cyst, hemangioma with classic features).",
    },
    LIRADSCategory.LR_2: {
        "label": "Probably benign",
        "description": "Probably benign observation.",
    },
    LIRADSCategory.LR_3: {
        "label": "Intermediate probability for malignancy",
        "description": "Observation with intermediate probability for malignancy.",
    },
    LIRADSCategory.LR_4: {
        "label": "Probably HCC",
        "description": "Observation probably representing HCC.",
    },
    LIRADSCategory.LR_5: {
        "label": "Definitely HCC",
        "description": "Observation definitely representing HCC.",
    },
    LIRADSCategory.LR_M: {
        "label": "Probably malignancy, not necessarily HCC",
        "description": "Observation probably malignant but with features not specific for HCC (e.g., cholangiocarcinoma, mixed HCC-CC).",
    },
    LIRADSCategory.LR_TIV: {
        "label": "Tumor in vein",
        "description": "Definite tumor in vein (enhancing soft tissue in vein).",
    },
}


def _check_threshold_growth(obs: LiverObservation) -> bool:
    """Check if threshold growth is present (>=50% increase in <=6 months)."""
    if obs.threshold_growth:
        return True
    if obs.prior_size_mm is not None and obs.prior_months is not None:
        if obs.prior_months <= 6 and obs.prior_size_mm > 0:
            growth_pct = ((obs.size_mm - obs.prior_size_mm) / obs.prior_size_mm) * 100
            if growth_pct >= 50:
                return True
    return False


def categorize(observation: LiverObservation) -> LIRADSResult:
    """Categorize an untreated CT/MRI observation using ACR LI-RADS v2018.

    The major-feature lookup follows the ACR diagnostic table; ancillary features
    can adjust the result by one category, but can never upgrade to LR-5.
    This decision aid is not a treatment-eligibility determination.
    """
    errors = observation.validate()
    if errors:
        raise ValueError("Invalid observation: " + "; ".join(errors))

    growth = _check_threshold_growth(observation)
    major_features = {
        "arterial_hyperenhancement": observation.arterial_hyperenhancement,
        "non_peripheral_washout": observation.non_peripheral_washout,
        "enhancing_capsule": observation.enhancing_capsule,
        "threshold_growth": growth,
    }
    notes: List[str] = []
    size = observation.size_mm
    count = sum((observation.non_peripheral_washout, observation.enhancing_capsule, growth))
    ahe = observation.arterial_hyperenhancement

    # Apply special categories before the CT/MRI diagnostic table.
    special = True
    if not observation.is_imaging_adequate:
        category = LIRADSCategory.LR_NC
        notes.append("Required imaging information is inadequate.")
    elif observation.has_tumor_in_vein:
        category = LIRADSCategory.LR_TIV
        notes.append("LR-TIV is not synonymous with HCC; determine etiology clinically.")
    elif observation.is_definitely_benign:
        category = LIRADSCategory.LR_1
    elif observation.is_probably_benign:
        category = LIRADSCategory.LR_2
    elif observation.has_malignancy_not_hcc:
        category = LIRADSCategory.LR_M
        notes.append("LR-M may include non-HCC malignancy or atypical HCC.")
    else:
        special = False
        if not ahe:
            if size < 20:
                category = LIRADSCategory.LR_4 if count >= 2 else LIRADSCategory.LR_3
            else:
                category = LIRADSCategory.LR_4 if count >= 1 else LIRADSCategory.LR_3
        elif size < 10:
            category = LIRADSCategory.LR_4 if count >= 1 else LIRADSCategory.LR_3
        elif size < 20:
            if count == 0:
                category = LIRADSCategory.LR_3
            elif count >= 2 or observation.non_peripheral_washout or growth:
                category = LIRADSCategory.LR_5
            else:
                category = LIRADSCategory.LR_4  # Capsule alone
        else:
            category = LIRADSCategory.LR_5 if count >= 1 else LIRADSCategory.LR_4

    # ACR v2018 optional ancillary adjustment (maximum one category).
    # Special categories are retained rather than being adjusted.
    if not special:
        mal = bool(observation.ancillary_favoring_malignancy)
        ben = bool(observation.ancillary_favoring_benignity)
        order = [LIRADSCategory.LR_1, LIRADSCategory.LR_2,
                 LIRADSCategory.LR_3, LIRADSCategory.LR_4, LIRADSCategory.LR_5]
        if mal and not ben and category in (LIRADSCategory.LR_2, LIRADSCategory.LR_3):
            category = order[order.index(category) + 1]
            notes.append("Upgraded one category using ancillary features; maximum LR-4.")
        elif ben and not mal and category in (LIRADSCategory.LR_3, LIRADSCategory.LR_4,
                                              LIRADSCategory.LR_5):
            category = order[order.index(category) - 1]
            notes.append("Downgraded one category using ancillary features.")
        elif mal and ben:
            notes.append("Opposing ancillary features: no category adjustment.")

    info = CATEGORY_INFO[category]
    notes.append("CT/MRI LI-RADS v2018 classification requires radiologist review and eligible clinical context.")
    return LIRADSResult(
        observation_id=observation.observation_id,
        category=category,
        category_label=info["label"],
        description=info["description"],
        size_mm=size,
        major_features=major_features,
        ancillary_malignancy=observation.ancillary_favoring_malignancy,
        ancillary_benignity=observation.ancillary_favoring_benignity,
        treatment_eligible=None,
        treatment_note="Imaging category does not independently determine treatment or transplant eligibility.",
        notes=notes,
    )


# ── Clinical Domain Engine ──────────────────────────────────────────────

class ClinicalDomainEngine:
    """Clinical evaluation engine for multi-agent audit system."""

    @staticmethod
    def evaluate_primary_index(primary_metric: float):
        """Evaluate primary metric against clinical thresholds."""
        if primary_metric > 20.0:
            return {
                "title": "Primary Metric Threshold Exceeded",
                "finding": f"Primary metric value ({primary_metric:.1f}) exceeded standard clinical baseline (20.0).",
                "recommendation": "Perform secondary cross-check and review calibration profile.",
            }
        return None

    @staticmethod
    def evaluate_secondary_kinetics(secondary_metric: float, is_stat: bool):
        """Evaluate secondary kinetics against safety thresholds."""
        if is_stat or secondary_metric > 12.0:
            return {
                "title": "Secondary Kinetics Alert",
                "finding": f"Secondary parameter index ({secondary_metric:.1f}) triggered automated supervisory escalation (STAT={is_stat}).",
                "recommendation": "Initiate mandatory closed-loop clinical notification protocol.",
            }
        return None

    @staticmethod
    def evaluate_biomarker_concordance(status_flag: str, biomarkers: dict):
        """Evaluate biomarker concordance with clinical standards."""
        status_upper = str(status_flag).upper()
        if any(w in status_upper for w in ["DISCORDANT", "SUSPICIOUS", "ANOMALY", "MUTANT"]):
            return {
                "title": "Biomarker Discordance Detected",
                "finding": f"Phenotypic discordance noted in status flag ({status_flag}).",
                "recommendation": "Reconcile correlative findings with secondary confirmatory testing.",
            }
        return None
