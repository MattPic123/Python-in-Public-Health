""" Author: Matt Picaroni | Date: 2026-11-22
Shared project paths and survey-weighted helpers."""
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
DATA, FIGURES, RESULTS = (ROOT / name for name in ("data", "figures", "results"))
for folder in (DATA, FIGURES, RESULTS):
    folder.mkdir(parents=True, exist_ok=True)

def weighted_mean(values, weights) -> float:
    """Return weighted mean, ignoring missing observations."""
    x = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    valid = np.isfinite(x) & np.isfinite(w) & (w > 0)
    return float(np.average(x[valid], weights=w[valid])) if valid.any() else float("nan")
