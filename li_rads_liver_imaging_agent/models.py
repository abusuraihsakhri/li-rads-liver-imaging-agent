"""
Data models for LI-RADS (Liver Imaging Reporting and Data System).
Standard: ACR LI-RADS v2018
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any


class LIRADSCategory(str, Enum):
    LR_NC = "LR-NC"
    LR_1 = "LR-1"
    LR_2 = "LR-2"
    LR_3 = "LR-3"
    LR_4 = "LR-4"
    LR_5 = "LR-5"
    LR_M = "LR-M"
    LR_TIV = "LR-TIV"


class Modality(str, Enum):
    CT = "CT"
    MRI = "MRI"
    US = "US"


@dataclass
class LiverObservation:
    """A liver observation (lesion/nodule) on imaging."""
    observation_id: str
    size_mm: float  # largest diameter in mm
    modality: Modality = Modality.CT

    # Major features (LI-RADS v2018)
    arterial_hyperenhancement: bool = False
    non_peripheral_washout: bool = False
    enhancing_capsule: bool = False
    threshold_growth: bool = False  # >=50% size increase in <=6 months

    # Ancillary features
    ancillary_favoring_malignancy: List[str] = field(default_factory=list)
    ancillary_favoring_benignity: List[str] = field(default_factory=list)

    # Special features
    has_tumor_in_vein: bool = False
    is_definitely_benign: bool = False  # e.g., cyst, hemangioma with classic features
    has_malignancy_not_hcc: bool = False  # features suggesting cholangiocarcinoma, etc.

    # Prior imaging
    prior_size_mm: Optional[float] = None
    prior_months: Optional[float] = None  # months since prior scan

    # At-risk liver
    has_at_risk_liver: bool = True  # cirrhosis, chronic HBV, etc.

    location: str = ""
    notes: str = ""

    def validate(self) -> List[str]:
        errors = []
        if self.size_mm <= 0:
            errors.append(f"Size must be positive, got {self.size_mm}")
        if self.prior_size_mm is not None and self.prior_size_mm <= 0:
            errors.append(f"Prior size must be positive, got {self.prior_size_mm}")
        return errors


@dataclass
class LIRADSResult:
    """Result of a LI-RADS assessment."""
    observation_id: str
    category: LIRADSCategory
    category_label: str
    description: str
    size_mm: float
    major_features: Dict[str, bool] = field(default_factory=dict)
    ancillary_malignancy: List[str] = field(default_factory=list)
    ancillary_benignity: List[str] = field(default_factory=list)
    treatment_eligible: bool = False
    treatment_note: str = ""
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "category": self.category.value,
            "category_label": self.category_label,
            "description": self.description,
            "size_mm": self.size_mm,
            "major_features": self.major_features,
            "ancillary_malignancy": self.ancillary_malignancy,
            "ancillary_benignity": self.ancillary_benignity,
            "treatment_eligible": self.treatment_eligible,
            "treatment_note": self.treatment_note,
            "notes": self.notes,
        }
