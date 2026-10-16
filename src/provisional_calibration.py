"""DEV-077S-I2-I-P2-A: presentation-only, frozen provisional calibration.

No imports from scoring, scenario, optimiser, or army-data services.
The immutable JSON anchors are the sole numerical reference; never refit to users' armies.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Mapping, Any

CALIBRATION_SCHEMA = "palantir-provisional-calibration-v1"
NOT_EVALUATED = "not_evaluated"
EVALUATED = "evaluated"
CONDITIONAL = "conditional"

class CalibrationError(ValueError):
    """Invalid or incompatible display-calibration evidence."""

@dataclass(frozen=True)
class DisplayRating:
    metric_id: str
    status: str
    label: str
    provisional: bool
    rating: float | None
    raw_value: float | None
    unit: str | None
    reference_version: str
    explanation: str
    clipped: bool = False

    def as_dict(self) -> dict[str, Any]:
        return dict(vars(self))


def load_reference(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if payload.get("schema_version") != CALIBRATION_SCHEMA:
        raise CalibrationError("Unsupported provisional reference schema")
    if payload.get("display_only") is not True or payload.get("production_approved") is not False:
        raise CalibrationError("Reference must remain display-only and unapproved")
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict) or not metrics:
        raise CalibrationError("No fixed metrics supplied")
    for key, record in metrics.items():
        if record.get("direction") != "higher_is_better":
            raise CalibrationError(f"Unsupported metric direction: {key}")
        low, high = record.get("minimum"), record.get("maximum")
        if any(type(x) not in (float, int) or not math.isfinite(x) for x in (low, high)) or high <= low:
            raise CalibrationError(f"Invalid fixed endpoints: {key}")
        if not record.get("unit") or not record.get("benchmark_context"):
            raise CalibrationError(f"Missing units/benchmark: {key}")
        if record.get("mapping_method", "cohort_minmax") == "zero_to_frozen_maximum":
            if low < 0 or high <= 0 or record.get("display_zero") != 0.0:
                raise CalibrationError(f"Invalid zero-to-maximum reference: {key}")
        elif record.get("mapping_method", "cohort_minmax") != "cohort_minmax":
            raise CalibrationError(f"Unknown mapping: {key}")
    return payload


def rate_display(metric_id: str, raw_value: float | None, reference: Mapping[str, Any], *,
                 evidence_status: str = EVALUATED, explanation: str = "") -> DisplayRating:
    """Return a display DTO, never a scored/optimised army object.

    Missing and conditional evidence are not numerical zero. Real observed zeros
    remain valid measurements, e.g. a genuinely shooting-free roster.
    """
    metrics = reference["metrics"]
    ref_version = str(reference["reference_version"])
    if metric_id not in metrics:
        return DisplayRating(metric_id, NOT_EVALUATED, "Not evaluated", True, None,
                             None, None, ref_version, explanation or "No qualified provisional reference")
    record = metrics[metric_id]
    unit = record["unit"]
    if evidence_status not in (EVALUATED, CONDITIONAL, NOT_EVALUATED):
        raise CalibrationError(f"Unknown evidence status: {evidence_status}")
    if raw_value is not None and (type(raw_value) not in (int, float) or not math.isfinite(raw_value)):
        raise CalibrationError("Raw value must be finite or None")
    if evidence_status != EVALUATED or raw_value is None:
        status = CONDITIONAL if evidence_status == CONDITIONAL else NOT_EVALUATED
        return DisplayRating(metric_id, status,
                             "Conditional — Not evaluated" if status == CONDITIONAL else "Not evaluated",
                             True, None, float(raw_value) if raw_value is not None else None,
                             unit, ref_version, explanation or "Benchmark context not qualified")
    low, high = record["minimum"], record["maximum"]
    raw = float(raw_value)
    method = record.get("mapping_method", "cohort_minmax")
    if method == "zero_to_frozen_maximum":
        if raw < 0:
            raise CalibrationError("Negative capability is invalid for zero-to-maximum calibration")
        rating = min(1.0, raw / high)
        clipped = raw > high
    else:
        rating = max(0.0, min(1.0, (raw - low) / (high - low)))
        clipped = raw < low or raw > high
    detail = explanation or ("Outside frozen six-army endpoints; display clipped" if clipped else "Six-army fixed-reference display")
    return DisplayRating(metric_id, EVALUATED, "Provisional", True, rating, raw, unit,
                         ref_version, detail, clipped)


def rate_capabilities(values: Mapping[str, float | None], reference: Mapping[str, Any], *,
                      evidence_statuses: Mapping[str, str] | None = None) -> dict[str, DisplayRating]:
    """Preserve unavailable and unsupported capabilities as Not evaluated."""
    statuses = evidence_statuses or {}
    names = tuple(dict.fromkeys((*reference["metrics"], *values, *statuses)))
    return {
        name: rate_display(name, values.get(name), reference,
                           evidence_status=statuses.get(name, EVALUATED))
        for name in names
    }
