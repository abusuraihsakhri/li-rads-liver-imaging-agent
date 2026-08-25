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

LR-5 criteria (>=10mm):
  - Arterial hyperenhancement AND
  - One or more: non-peripheral washout, threshold growth, enhancing capsule

Treatment eligibility:
  - LR-5: Eligible for HCC treatment without biopsy
  - LR-TIV: Eligible for HCC treatment
  - LR-4: May be eligible depending on institutional policy

Reference: ACR LI-RADS v2018
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
    """
    Categorize a liver observation using LI-RADS v2018 criteria.

    Decision logic:
    1. Check for special categories first (LR-NC, LR-TIV, LR-M, LR-1)
    2. Apply size-based criteria for LR-5
    3. Apply major feature combinations for LR-4, LR-3, LR-2
    """
    errors = observation.validate()
    if errors:
        raise ValueError(f"Invalid observation: {'; '.join(errors)}")

    notes: List[str] = []
    has_growth = _check_threshold_growth(observation)

    major_features = {
        "arterial_hyperenhancement": observation.arterial_hyperenhancement,
        "non_peripheral_washout": observation.non_peripheral_washout,
        "enhancing_capsule": observation.enhancing_capsule,
        "threshold_growth": has_growth,
    }

    # ── Special categories ──────────────────────────────────────────

    # LR-NC: Not categorizable
    if not observation.has_at_risk_liver:
        notes.append("Observation in liver without known risk factors; LI-RADS may not apply.")
        # Still categorize but note the caveat

    # LR-TIV: Tumor in vein
    if observation.has_tumor_in_vein:
        info = CATEGORY_INFO[LIRADSCategory.LR_TIV]
        return LIRADSResult(
            observation_id=observation.observation_id,
            category=LIRADSCategory.LR_TIV,
            category_label=info["label"],
            description=info["description"],
            size_mm=observation.size_mm,
            major_features=major_features,
            ancillary_malignancy=observation.ancillary_favoring_malignancy,
            ancillary_benignity=observation.ancillary_favoring_benignity,
            treatment_eligible=True,
            treatment_note="Tumor-in-vein: eligible for HCC treatment.",
            notes=notes,
        )

    # LR-1: Definitely benign
    if observation.is_definitely_benign:
        info = CATEGORY_INFO[LIRADSCategory.LR_1]
        return LIRADSResult(
            observation_id=observation.observation_id,
            category=LIRADSCategory.LR_1,
            category_label=info["label"],
            description=info["description"],
            size_mm=observation.size_mm,
            major_features=major_features,
            ancillary_malignancy=observation.ancillary_favoring_malignancy,
            ancillary_benignity=observation.ancillary_favoring_benignity,
            treatment_eligible=False,
            treatment_note="Benign: no treatment needed.",
            notes=notes,
        )

    # LR-M: Probably malignancy, not HCC-specific
    if observation.has_malignancy_not_hcc:
        info = CATEGORY_INFO[LIRADSCategory.LR_M]
        return LIRADSResult(
            observation_id=observation.observation_id,
            category=LIRADSCategory.LR_M,
            category_label=info["label"],
            description=info["description"],
            size_mm=observation.size_mm,
            major_features=major_features,
            ancillary_malignancy=observation.ancillary_favoring_malignancy,
            ancillary_benignity=observation.ancillary_favoring_benignity,
            treatment_eligible=False,
            treatment_note="LR-M: tissue sampling recommended for diagnosis.",
            notes=notes,
        )

    # ── Size-based HCC criteria ─────────────────────────────────────

    ahe = observation.arterial_hyperenhancement
    washout = observation.non_peripheral_washout
    capsule = observation.enhancing_capsule
    size = observation.size_mm

    # Count major features (excluding arterial hyperenhancement which is required)
    ancillary_mal = observation.ancillary_favoring_malignancy
    ancillary_ben = observation.ancillary_favoring_benignity

    # LR-5: >=10mm with AHE AND (washout OR growth OR capsule)
    if size >= 10 and ahe:
        ancillary_features_present = washout or has_growth or capsule
        if ancillary_features_present:
            # LR-5 criteria met
            # Additional conditions for LR-5 depending on size
            if size >= 10 and size < 20:
                # 10-19mm: need AHE + (washout OR growth OR capsule)
                info = CATEGORY_INFO[LIRADSCategory.LR_5]
                return LIRADSResult(
                    observation_id=observation.observation_id,
                    category=LIRADSCategory.LR_5,
                    category_label=info["label"],
                    description=info["description"],
                    size_mm=size,
                    major_features=major_features,
                    ancillary_malignancy=ancillary_mal,
                    ancillary_benignity=ancillary_ben,
                    treatment_eligible=True,
                    treatment_note="LR-5: eligible for HCC treatment without biopsy.",
                    notes=notes,
                )
            elif size >= 20:
                # >=20mm: AHE + (washout OR growth OR capsule) = LR-5
                info = CATEGORY_INFO[LIRADSCategory.LR_5]
                return LIRADSResult(
                    observation_id=observation.observation_id,
                    category=LIRADSCategory.LR_5,
                    category_label=info["label"],
                    description=info["description"],
                    size_mm=size,
                    major_features=major_features,
                    ancillary_malignancy=ancillary_mal,
                    ancillary_benignity=ancillary_ben,
                    treatment_eligible=True,
                    treatment_note="LR-5: eligible for HCC treatment without biopsy.",
                    notes=notes,
                )

    # LR-4: >=10mm with AHE but NO washout/growth/capsule
    # OR 10-19mm with AHE + washout but not meeting LR-5
    # OR >=20mm with AHE only (no washout/growth/capsule)
    if size >= 10 and ahe and not (washout or has_growth or capsule):
        # AHE alone for >=20mm or AHE without other features for 10-19mm
        if size >= 20:
            info = CATEGORY_INFO[LIRADSCategory.LR_4]
            return LIRADSResult(
                observation_id=observation.observation_id,
                category=LIRADSCategory.LR_4,
                category_label=info["label"],
                description=info["description"],
                size_mm=size,
                major_features=major_features,
                ancillary_malignancy=ancillary_mal,
                ancillary_benignity=ancillary_ben,
                treatment_eligible=False,
                treatment_note="LR-4: consider biopsy or short-interval follow-up.",
                notes=notes + ["AHE without washout/capsule/growth in >=20mm observation."],
            )
        else:
            # 10-19mm with AHE only
            info = CATEGORY_INFO[LIRADSCategory.LR_4]
            return LIRADSResult(
                observation_id=observation.observation_id,
                category=LIRADSCategory.LR_4,
                category_label=info["label"],
                description=info["description"],
                size_mm=size,
                major_features=major_features,
                ancillary_malignancy=ancillary_mal,
                ancillary_benignity=ancillary_ben,
                treatment_eligible=False,
                treatment_note="LR-4: consider biopsy or short-interval follow-up.",
                notes=notes,
            )

    # LR-4: 10-19mm with washout but no AHE (per some interpretations)
    # Actually in LI-RADS, AHE is required for LR-4/5. Without AHE:
    # <10mm: LR-2 or LR-3
    # >=10mm without AHE: LR-3

    # Observations with some features but not meeting higher criteria
    if size >= 10:
        if washout or has_growth or capsule:
            # Has some features but missing AHE -> LR-3
            info = CATEGORY_INFO[LIRADSCategory.LR_3]
            return LIRADSResult(
                observation_id=observation.observation_id,
                category=LIRADSCategory.LR_3,
                category_label=info["label"],
                description=info["description"],
                size_mm=size,
                major_features=major_features,
                ancillary_malignancy=ancillary_mal,
                ancillary_benignity=ancillary_ben,
                treatment_eligible=False,
                treatment_note="LR-3: follow-up imaging recommended.",
                notes=notes + ["Features present but AHE absent; does not meet LR-4/5 criteria."],
            )
        else:
            # >=10mm with no features -> LR-3
            info = CATEGORY_INFO[LIRADSCategory.LR_3]
            return LIRADSResult(
                observation_id=observation.observation_id,
                category=LIRADSCategory.LR_3,
                category_label=info["label"],
                description=info["description"],
                size_mm=size,
                major_features=major_features,
                ancillary_malignancy=ancillary_mal,
                ancillary_benignity=ancillary_ben,
                treatment_eligible=False,
                treatment_note="LR-3: follow-up imaging recommended.",
                notes=notes,
            )

    # <10mm observations
    if size >= 10:
        # Should have been caught above
        pass

    # <10mm with features
    if ahe or washout or has_growth or capsule:
        info = CATEGORY_INFO[LIRADSCategory.LR_3]
        return LIRADSResult(
            observation_id=observation.observation_id,
            category=LIRADSCategory.LR_3,
            category_label=info["label"],
            description=info["description"],
            size_mm=size,
            major_features=major_features,
            ancillary_malignancy=ancillary_mal,
            ancillary_benignity=ancillary_ben,
            treatment_eligible=False,
            treatment_note="LR-3: follow-up imaging recommended.",
            notes=notes,
        )

    # <10mm without features -> LR-2
    info = CATEGORY_INFO[LIRADSCategory.LR_2]
    return LIRADSResult(
        observation_id=observation.observation_id,
        category=LIRADSCategory.LR_2,
        category_label=info["label"],
        description=info["description"],
        size_mm=size,
        major_features=major_features,
        ancillary_malignancy=ancillary_mal,
        ancillary_benignity=ancillary_ben,
        treatment_eligible=False,
        treatment_note="LR-2: routine surveillance.",
        notes=notes,
    )
