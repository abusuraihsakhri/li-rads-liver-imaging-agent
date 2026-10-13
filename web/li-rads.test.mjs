import test from "node:test";
import assert from "node:assert/strict";
import { categorize } from "./li-rads.mjs";

const scenarios = [
  [{ sizeMm: 5 }, "LR-3"],
  [{ sizeMm: 8, arterialHyperenhancement: true }, "LR-3"],
  [{ sizeMm: 8, arterialHyperenhancement: true, washout: true }, "LR-4"],
  [{ sizeMm: 10, arterialHyperenhancement: true }, "LR-3"],
  [{ sizeMm: 15, arterialHyperenhancement: true, capsule: true }, "LR-4"],
  [{ sizeMm: 15, arterialHyperenhancement: true, washout: true }, "LR-5"],
  [{ sizeMm: 15, arterialHyperenhancement: true, thresholdGrowth: true }, "LR-5"],
  [{ sizeMm: 20, arterialHyperenhancement: true }, "LR-4"],
  [{ sizeMm: 20, arterialHyperenhancement: true, capsule: true }, "LR-5"],
  [{ sizeMm: 20, capsule: true }, "LR-4"],
  [{ sizeMm: 15, capsule: true, washout: true }, "LR-4"],
  [{ sizeMm: 15, washout: true }, "LR-3"],
  [{ sizeMm: 15, imagingAdequate: false }, "LR-NC"],
  [{ sizeMm: 15, tumorInVein: true }, "LR-TIV"],
  [{ sizeMm: 15, definitelyBenign: true }, "LR-1"],
  [{ sizeMm: 15, probablyBenign: true }, "LR-2"],
  [{ sizeMm: 15, nonHccSpecific: true }, "LR-M"],
  [{ sizeMm: 14, priorSizeMm: 8, priorMonths: 4, arterialHyperenhancement: true }, "LR-5"],
  [{ sizeMm: 14, priorSizeMm: 8, priorMonths: 7, arterialHyperenhancement: true }, "LR-3"],
  [{ sizeMm: 15, arterialHyperenhancement: true, capsule: true, afMalignancy: true }, "LR-4"],
  [{ sizeMm: 15, arterialHyperenhancement: true, afMalignancy: true }, "LR-4"],
  [{ sizeMm: 15, arterialHyperenhancement: true, washout: true, afBenignity: true }, "LR-4"],
];
for (const [observation, expected] of scenarios) {
  test("v2018 scenario: " + JSON.stringify(observation), () => {
    const result = categorize(observation);
    assert.equal(result.category, expected);
    assert.ok(result.label);
    assert.ok(result.reason);
    assert.match(result.treatmentNote, /does not/);
  });
}
for (const observation of [
  { sizeMm: 0 }, { sizeMm: NaN }, { sizeMm: Infinity },
  { sizeMm: 15, atRisk: false }, { sizeMm: 15, modality: "US" },
  { sizeMm: 15, priorSizeMm: 5 },
  { sizeMm: 15, priorSizeMm: 5, priorMonths: -1 },
  { sizeMm: 15, definitelyBenign: true, tumorInVein: true },
]) {
  test("reject invalid input: " + JSON.stringify(observation), () => {
    assert.throws(() => categorize(observation), Error);
  });
}
