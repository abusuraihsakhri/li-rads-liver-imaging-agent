/* ACR CT/MRI LI-RADS v2018 major-feature decision table.
   Reference: https://cs.acr.org/-/media/ACR/NOINDEX/RADS/LI-RADS-2018-Core.pdf
   Educational decision support only: not an HCC diagnosis or treatment decision.
*/
const LABELS = {
  "LR-NC": "Not categorizable", "LR-TIV": "Tumor in vein",
  "LR-1": "Definitely benign", "LR-2": "Probably benign",
  "LR-3": "Intermediate probability of malignancy", "LR-4": "Probably HCC",
  "LR-5": "Definitely HCC", "LR-M": "Malignancy, not necessarily HCC"
};

export function categorize(input) {
  const {
    sizeMm, modality = "CT", atRisk = true, imagingAdequate = true,
    arterialHyperenhancement = false, washout = false, capsule = false,
    thresholdGrowth = false, priorSizeMm = null, priorMonths = null,
    tumorInVein = false, definitelyBenign = false, probablyBenign = false,
    nonHccSpecific = false, afMalignancy = false, afBenignity = false
  } = input;
  if (!Number.isFinite(sizeMm) || sizeMm <= 0) throw new Error("Enter a finite, positive observation size.");
  if (modality !== "CT" && modality !== "MRI") throw new Error("The diagnostic table applies to multiphase CT or MRI, not ultrasound.");
  if (!atRisk) throw new Error("CT/MRI LI-RADS requires an eligible HCC high-risk population.");
  if ((priorSizeMm === null) !== (priorMonths === null)) throw new Error("Supply both prior size and interval or leave both blank.");
  if (priorSizeMm !== null && (!Number.isFinite(priorSizeMm) || priorSizeMm <= 0)) throw new Error("Prior size must be positive and finite.");
  if (priorMonths !== null && (!Number.isFinite(priorMonths) || priorMonths <= 0)) throw new Error("Prior interval must be positive and finite.");
  if (definitelyBenign && (probablyBenign || nonHccSpecific || tumorInVein)) throw new Error("Conflicting benign and malignant features.");
  const growth = thresholdGrowth || (priorSizeMm !== null && priorMonths <= 6 && sizeMm >= priorSizeMm * 1.5);
  const count = Number(washout) + Number(capsule) + Number(growth);
  let category, reason, special = true;
  if (!imagingAdequate) {
    category = "LR-NC"; reason = "Essential sequences are missing or degraded.";
  } else if (tumorInVein) {
    category = "LR-TIV"; reason = "Definite enhancing soft tissue in vein; etiology requires clinical assessment.";
  } else if (definitelyBenign) {
    category = "LR-1"; reason = "Features are unequivocally benign.";
  } else if (probablyBenign) {
    category = "LR-2"; reason = "Features are probably benign.";
  } else if (nonHccSpecific) {
    category = "LR-M"; reason = "Malignancy features are not HCC-specific.";
  } else {
    special = false;
    if (!arterialHyperenhancement) {
      category = sizeMm < 20 ? (count >= 2 ? "LR-4" : "LR-3") : (count >= 1 ? "LR-4" : "LR-3");
    } else if (sizeMm < 10) {
      category = count >= 1 ? "LR-4" : "LR-3";
    } else if (sizeMm < 20) {
      category = count === 0 ? "LR-3" : (count >= 2 || washout || growth ? "LR-5" : "LR-4");
    } else {
      category = count >= 1 ? "LR-5" : "LR-4";
    }
    reason = "CT/MRI v2018 diagnostic table: " + (arterialHyperenhancement ? "nonrim APHE" : "no APHE") +
      ", " + count + " additional major feature(s), " + sizeMm + " mm.";
  }
  if (!special) {
    const order = ["LR-1", "LR-2", "LR-3", "LR-4", "LR-5"];
    if (afMalignancy && !afBenignity && (category === "LR-2" || category === "LR-3")) {
      category = order[order.indexOf(category) + 1];
      reason += " Ancillary feature favors malignancy: upgraded by one, capped at LR-4.";
    } else if (afBenignity && !afMalignancy && ["LR-3", "LR-4", "LR-5"].includes(category)) {
      category = order[order.indexOf(category) - 1];
      reason += " Ancillary feature favors benignity: downgraded by one.";
    } else if (afMalignancy && afBenignity) {
      reason += " Opposing ancillary features: no adjustment.";
    }
  }
  return {
    category, label: LABELS[category], reason, sizeMm, modality,
    majorFeatures: { arterialHyperenhancement, washout, capsule, thresholdGrowth: growth },
    treatmentNote: "LI-RADS category alone does not establish treatment or transplant eligibility.",
    disclaimer: "Educational decision support. Confirm exam quality, risk population, feature definitions, and final classification with a radiologist."
  };
}

if (typeof document !== "undefined") {
  const form = document.getElementById("assessment-form");
  const result = document.getElementById("assessment-result");
  const exportButton = document.getElementById("export-json");
  let lastResult = null;
  const checked = (id) => document.getElementById(id).checked;
  const field = (id) => document.getElementById(id).value;
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    lastResult = null;
    exportButton.disabled = true;
    const priorSize = field("prior-size");
    const priorMonths = field("prior-months");
    const observation = {
      sizeMm: Number(field("size")), modality: field("modality"), atRisk: checked("at-risk"),
      imagingAdequate: checked("adequate"), arterialHyperenhancement: checked("aphe"),
      washout: checked("washout"), capsule: checked("capsule"), thresholdGrowth: checked("growth"),
      priorSizeMm: priorSize === "" ? null : Number(priorSize),
      priorMonths: priorMonths === "" ? null : Number(priorMonths),
      tumorInVein: checked("tiv"), definitelyBenign: checked("benign"),
      probablyBenign: checked("probably-benign"), nonHccSpecific: checked("lrm"),
      afMalignancy: checked("af-malignancy"), afBenignity: checked("af-benignity")
    };
    try {
      lastResult = categorize(observation);
      document.getElementById("category").textContent = lastResult.category;
      document.getElementById("category-label").textContent = lastResult.label;
      document.getElementById("category-reason").textContent = lastResult.reason;
      result.dataset.status = "success";
      exportButton.disabled = false;
    } catch (error) {
      document.getElementById("category").textContent = "Not assessed";
      document.getElementById("category-label").textContent = "Check the inputs";
      document.getElementById("category-reason").textContent = error.message;
      result.dataset.status = "error";
    }
  });
  form.addEventListener("reset", () => {
    lastResult = null;
    exportButton.disabled = true;
    document.getElementById("category").textContent = "—";
    document.getElementById("category-label").textContent = "Ready for assessment";
    document.getElementById("category-reason").textContent = "Complete the imaging characteristics and select Categorize.";
    result.dataset.status = "idle";
  });
  exportButton.addEventListener("click", () => {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "li-rads-assessment.json";
    a.click();
    URL.revokeObjectURL(url);
  });
}
