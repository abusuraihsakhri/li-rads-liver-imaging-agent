"""
Tests for LI-RADS v2018 liver observation categorization engine.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from li_rads_liver_imaging_agent.models import LiverObservation, LIRADSCategory, Modality
from li_rads_liver_imaging_agent.engine import categorize, CATEGORY_INFO
from cli import main as cli_main


# ── LR-5 (Definitely HCC) Tests ────────────────────────────────────

class TestLR5:
    def test_lr5_10mm_ahe_washout(self):
        """10mm + AHE + washout = LR-5."""
        obs = LiverObservation("O1", size_mm=10, arterial_hyperenhancement=True,
                               non_peripheral_washout=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5
        assert r.treatment_eligible is True

    def test_lr5_15mm_ahe_capsule(self):
        """15mm + AHE + capsule = LR-5."""
        obs = LiverObservation("O1", size_mm=15, arterial_hyperenhancement=True,
                               enhancing_capsule=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5

    def test_lr5_20mm_ahe_growth(self):
        """20mm + AHE + threshold growth = LR-5."""
        obs = LiverObservation("O1", size_mm=20, arterial_hyperenhancement=True,
                               threshold_growth=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5

    def test_lr5_30mm_ahe_washout_capsule(self):
        """30mm + AHE + washout + capsule = LR-5."""
        obs = LiverObservation("O1", size_mm=30, arterial_hyperenhancement=True,
                               non_peripheral_washout=True, enhancing_capsule=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5

    def test_lr5_calculated_growth(self):
        """Growth calculated from prior: 8mm -> 14mm in 4 months = 75% growth."""
        obs = LiverObservation("O1", size_mm=14, arterial_hyperenhancement=True,
                               prior_size_mm=8, prior_months=4)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5

    def test_lr5_all_features(self):
        obs = LiverObservation("O1", size_mm=25, arterial_hyperenhancement=True,
                               non_peripheral_washout=True, enhancing_capsule=True,
                               threshold_growth=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_5
        assert r.treatment_eligible is True


# ── LR-4 (Probably HCC) Tests ──────────────────────────────────────

class TestLR4:
    def test_lr4_15mm_ahe_only(self):
        """15mm + AHE only (no washout/capsule/growth) = LR-4."""
        obs = LiverObservation("O1", size_mm=15, arterial_hyperenhancement=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_4
        assert r.treatment_eligible is False

    def test_lr4_25mm_ahe_only(self):
        """25mm + AHE only = LR-4."""
        obs = LiverObservation("O1", size_mm=25, arterial_hyperenhancement=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_4

    def test_lr4_10mm_ahe_only(self):
        """10mm + AHE only = LR-4."""
        obs = LiverObservation("O1", size_mm=10, arterial_hyperenhancement=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_4


# ── LR-3 (Intermediate) Tests ──────────────────────────────────────

class TestLR3:
    def test_lr3_12mm_no_features(self):
        """12mm without any features = LR-3."""
        obs = LiverObservation("O1", size_mm=12)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_3

    def test_lr3_15mm_washout_no_ahe(self):
        """15mm with washout but no AHE = LR-3."""
        obs = LiverObservation("O1", size_mm=15, non_peripheral_washout=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_3

    def test_lr3_8mm_with_ahe(self):
        """<10mm with AHE = LR-3."""
        obs = LiverObservation("O1", size_mm=8, arterial_hyperenhancement=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_3

    def test_lr3_5mm_with_washout(self):
        """<10mm with washout = LR-3."""
        obs = LiverObservation("O1", size_mm=5, non_peripheral_washout=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_3


# ── LR-2 (Probably Benign) Tests ───────────────────────────────────

class TestLR2:
    def test_lr2_small_no_features(self):
        """<10mm without features = LR-2."""
        obs = LiverObservation("O1", size_mm=7)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_2

    def test_lr2_5mm_no_features(self):
        obs = LiverObservation("O1", size_mm=5)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_2

    def test_lr2_9mm_no_features(self):
        obs = LiverObservation("O1", size_mm=9)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_2


# ── LR-1 (Definitely Benign) Tests ─────────────────────────────────

class TestLR1:
    def test_lr1_cyst(self):
        obs = LiverObservation("O1", size_mm=15, is_definitely_benign=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_1
        assert r.treatment_eligible is False

    def test_lr1_hemangioma(self):
        obs = LiverObservation("O1", size_mm=30, is_definitely_benign=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_1


# ── LR-M Tests ─────────────────────────────────────────────────────

class TestLRM:
    def test_lr_m_cholangiocarcinoma(self):
        obs = LiverObservation("O1", size_mm=30, arterial_hyperenhancement=True,
                               has_malignancy_not_hcc=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_M
        assert r.treatment_eligible is False

    def test_lr_m_no_ahe(self):
        obs = LiverObservation("O1", size_mm=20, has_malignancy_not_hcc=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_M


# ── LR-TIV Tests ───────────────────────────────────────────────────

class TestLRTIV:
    def test_lr_tiv(self):
        obs = LiverObservation("O1", size_mm=40, has_tumor_in_vein=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_TIV
        assert r.treatment_eligible is True

    def test_lr_tiv_with_ahe(self):
        obs = LiverObservation("O1", size_mm=35, arterial_hyperenhancement=True,
                               has_tumor_in_vein=True)
        r = categorize(obs)
        assert r.category == LIRADSCategory.LR_TIV


# ── Validation Tests ────────────────────────────────────────────────

class TestValidation:
    def test_invalid_size(self):
        obs = LiverObservation("O1", size_mm=-5)
        with pytest.raises(ValueError):
            categorize(obs)

    def test_zero_size(self):
        obs = LiverObservation("O1", size_mm=0)
        with pytest.raises(ValueError):
            categorize(obs)


# ── Result Model Tests ──────────────────────────────────────────────

class TestResultModel:
    def test_to_dict(self):
        obs = LiverObservation("O1", size_mm=20, arterial_hyperenhancement=True,
                               non_peripheral_washout=True)
        r = categorize(obs)
        d = r.to_dict()
        assert d["category"] == "LR-5"
        assert d["size_mm"] == 20
        assert "major_features" in d

    def test_major_features_populated(self):
        obs = LiverObservation("O1", size_mm=20, arterial_hyperenhancement=True,
                               non_peripheral_washout=True, enhancing_capsule=True)
        r = categorize(obs)
        assert r.major_features["arterial_hyperenhancement"] is True
        assert r.major_features["non_peripheral_washout"] is True
        assert r.major_features["enhancing_capsule"] is True

    def test_category_info_complete(self):
        for cat in LIRADSCategory:
            assert cat in CATEGORY_INFO
            assert "label" in CATEGORY_INFO[cat]
            assert "description" in CATEGORY_INFO[cat]


# ── CLI Tests ───────────────────────────────────────────────────────

class TestCLI:
    def test_categorize_lr5(self, capsys):
        ret = cli_main(["categorize", "--size", "20", "--ahe", "--washout"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "LR-5" in out

    def test_categorize_json(self, capsys):
        ret = cli_main(["categorize", "--size", "20", "--ahe", "--washout", "--json"])
        assert ret == 0
        import json
        data = json.loads(capsys.readouterr().out)
        assert data["category"] == "LR-5"

    def test_categorize_benign(self, capsys):
        ret = cli_main(["categorize", "--size", "10", "--definitely-benign"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "LR-1" in out

    def test_info_command(self, capsys):
        ret = cli_main(["info"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "LR-5" in out

    def test_info_specific(self, capsys):
        ret = cli_main(["info", "5"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "Definitely HCC" in out
