"""Peaks over threshold GPD. Threshold is frozen at training 90th loss percentile."""

import warnings
import numpy as np
import pandas as pd
from scipy.stats import genpareto
from .risk import empirical
from .config import SEED


def fit(loss: np.ndarray, threshold_q: float = 0.90, min_exceed: int = 40) -> dict:
    x = np.asarray(loss, dtype=float)
    if not 0.7 <= threshold_q < 0.99 or len(x) < 100 or not np.isfinite(x).all():
        raise ValueError("Invalid EVT input")
    u = float(np.quantile(x, threshold_q))
    exc = x[x > u] - u
    if len(exc) < min_exceed:
        raise ValueError(f"Insufficient EVT exceedances: {len(exc)} < {min_exceed}")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        shape, _, scale = genpareto.fit(exc, floc=0)
    if (
        scale <= 0
        or not np.isfinite([shape, scale]).all()
        or np.any(1 + shape * exc / scale <= 0)
    ):
        raise ValueError("Invalid GPD support/fit")
    return dict(
        threshold=u,
        threshold_q=threshold_q,
        shape=float(shape),
        scale=float(scale),
        n=len(x),
        exceedances=len(exc),
        p_exceed=len(exc) / len(x),
        finite_ES=bool(shape < 1),
        warning="Serial tail clustering and threshold uncertainty remain; no iid precision claim",
    )


def estimate(model: dict, alpha: float) -> dict:
    p = 1 - alpha
    xi, beta, u = model["shape"], model["scale"], model["threshold"]
    pu = model["p_exceed"]
    if p >= pu - 1e-12 or alpha <= model.get("threshold_q", 1 - pu) + 1e-12:
        raise ValueError(
            "Requested quantile is at/below POT threshold; EVT estimate not applicable"
        )
    q = (
        u + beta * np.log(pu / p)
        if abs(xi) < 1e-7
        else u + beta / xi * ((pu / p) ** xi - 1)
    )
    es = (q + beta - xi * u) / (1 - xi) if xi < 1 else None
    return dict(VaR=float(q), ES=float(es) if es is not None else None)


def sensitivity(loss: np.ndarray) -> pd.DataFrame:
    rows = []
    for tq in [0.85, 0.875, 0.90, 0.925, 0.95]:
        try:
            m = fit(loss, tq)
            rows.append(dict(**m, **estimate(m, 0.99), status="estimated"))
        except ValueError as e:
            rows.append(dict(threshold_q=tq, status=str(e)))
    return pd.DataFrame(rows)


def bootstrap(
    loss: np.ndarray, tq: float = 0.90, reps: int = 150, block: int = 20
) -> dict:
    x = np.asarray(loss)
    rng = np.random.default_rng(SEED)
    values = []
    for _ in range(reps):
        starts = rng.integers(len(x), size=int(np.ceil(len(x) / block)))
        sample = x[((starts[:, None] + np.arange(block)) % len(x)).ravel()[: len(x)]]
        try:
            m = fit(sample, tq)
            v = estimate(m, 0.99)
            if v["ES"] is not None:
                values.append([m["shape"], v["VaR"], v["ES"]])
        except ValueError:
            pass
    if len(values) < 30:
        raise ValueError("Too few valid bootstrap fits")
    a = np.asarray(values)
    return dict(
        repetitions=reps,
        valid=len(a),
        block=block,
        shape_CI=np.quantile(a[:, 0], [0.025, 0.975]).tolist(),
        VaR99_CI=np.quantile(a[:, 1], [0.025, 0.975]).tolist(),
        ES99_CI=np.quantile(a[:, 2], [0.025, 0.975]).tolist(),
        note="Circular block percentile interval refits threshold and GPD; not a guarantee of coverage",
    )
