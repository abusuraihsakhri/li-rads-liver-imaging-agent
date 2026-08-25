"""
LI-RADS Liver Imaging Agent: ACR LI-RADS v2018 liver observation categorization.
"""
__version__ = "2.0.0-PRO"

from .models import LiverObservation, LIRADSCategory, LIRADSResult, Modality
from .engine import categorize, CATEGORY_INFO
