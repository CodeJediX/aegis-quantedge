"""Rolling estimates use only rows strictly preceding each forecast date."""

import numpy as np
import pandas as pd
from scipy.special import xlogy
from scipy.stats import chi2
from .risk import empirical, normal_log, mc_losses, filtered_forecast
from .evt import fit, estimate
from .config import WINDOW, CONFIDENCES, SEED


def coverage(hits: np.ndarray, alpha: float) -> dict:
    h = np.asarray(hits)
    if len(h) < 2 or not np.isin(h, [0, 1]).all() or not 0 < alpha < 1:
        raise ValueError("At least two binary hits required")
    h = h.astype(int)
    n = len(h)
    k = int(h.sum())
    p = 1 - alpha

    def logbin(a, b, prob):
        return float(xlogy(a, prob) + xlogy(b, 1 - prob))

    lruc = max(0, 2 * (logbin(k, n - k, k / n) - logbin(k, n - k, p)))
    counts = np.array(
        [[np.sum((h[:-1] == i) & (h[1:] == j)) for j in [0, 1]] for i in [0, 1]]
    )
    if (counts.sum(axis=1) == 0).any():
        lrind = pind = lrcc = pcc = None
    else:
        p01 = counts[0, 1] / counts[0].sum()
        p11 = counts[1, 1] / counts[1].sum()
        pi = counts[:, 1].sum() / counts.sum()
        alt = logbin(counts[0, 1], counts[0, 0], p01) + logbin(
            counts[1, 1], counts[1, 0], p11
        )
        null = logbin(counts[:, 1].sum(), counts[:, 0].sum(), pi)
        lrind = float(max(0, 2 * (alt - null)))
        pind = float(chi2.sf(lrind, 1))
        lrcc = float(lruc + lrind)
        pcc = float(chi2.sf(lrcc, 2))
    return dict(
        n=n,
        exceptions=k,
        expected=n * p,
        exception_rate=k / n,
        kupiec_LR=float(lruc),
        kupiec_p=float(chi2.sf(lruc, 1)),
        independence_LR=lrind,
        independence_p=pind,
        conditional_LR=lrcc,
        conditional_p=pcc,
        n00=int(counts[0, 0]),
        n01=int(counts[0, 1]),
        n10=int(counts[1, 0]),
        n11=int(counts[1, 1]),
    )


def traffic(hits: np.ndarray, alpha: float) -> str:
    if abs(alpha - 0.99) > 1e-8 or len(hits) != 250:
        return "N/A: requires 250 one-day 99% forecasts"
    k = np.sum(hits)
    return "Green" if k <= 4 else "Amber" if k <= 9 else "Red"


def forecasts(
    r: pd.DataFrame,
    w: np.ndarray,
    start: str = "2019-01-01",
    window: int = WINDOW,
    n_mc: int = 10000,
) -> pd.DataFrame:
    from .portfolio import validate_weights
    from .config import TICKERS
    validate_weights(w)
    if (list(r.columns) != TICKERS or r.index.has_duplicates or not r.index.is_monotonic_increasing
            or window < 100 or len(r) <= window or not np.isfinite(r.to_numpy()).all() or (r <= -1).any().any()):
        raise ValueError("Rolling forecasts require complete chronological seven-ETF returns and an adequate prior window.")
    portfolio = r.to_numpy() @ w
    rows = []
    for i in range(window, len(r)):
        if r.index[i] < pd.Timestamp(start):
            continue
        past = portfolio[i - window : i]
        frame = r.iloc[i - window : i]
        sim = mc_losses(np.log1p(frame), w, n=n_mc, seed=SEED)
        try:
            ev = fit(-past)
        except ValueError:
            ev = None
        for a in CONFIDENCES:
            risks = {
                "Historical": empirical(-past, a),
                "Parametric": normal_log(past, a),
                "Monte Carlo": empirical(sim, a),
                "Volatility state": filtered_forecast(past, a),
            }
            if ev is not None:
                try:
                    risks["EVT"] = estimate(ev, a)
                except ValueError:
                    pass
            for name, value in risks.items():
                rows.append(
                    dict(
                        date=r.index[i],
                        estimate_end=r.index[i - 1],
                        estimate_start=r.index[i - window],
                        model=name,
                        confidence=a,
                        VaR=value["VaR"],
                        ES=value["ES"],
                        loss=-portfolio[i],
                        volatility_ratio=value.get("volatility_ratio", np.nan),
                    )
                )
    result = pd.DataFrame(rows)
    if not (result.estimate_end < result.date).all():
        raise AssertionError("Future data detected")
    return result


def summarize(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, a), g in f.groupby(["model", "confidence"]):
        g = g.sort_values("date")
        if g.date.duplicated().any():
            raise ValueError("Duplicate forecast dates within a model/confidence series.")
        hits = g.loss.to_numpy() > g.VaR.to_numpy()
        q = g.VaR.to_numpy()
        e = g.ES.to_numpy()
        loss = g.loss.to_numpy()
        residual = q + np.maximum(loss - q, 0) / (1 - a) - e
        valid = np.isfinite(e) & (e > 0)
        score = (
            np.mean(
                np.maximum(loss[valid] - q[valid], 0) / ((1 - a) * e[valid])
                + q[valid] / e[valid]
                + np.log(e[valid])
                - 1
            )
            if valid.any()
            else None
        )
        rows.append(
            dict(
                model=model,
                confidence=a,
                **coverage(hits, a),
                observed_exceedance_mean=(
                    float(loss[hits].mean()) if hits.any() else None
                ),
                mean_predicted_ES=float(np.nanmean(e)),
                ES_residual=float(np.nanmean(residual)),
                quantile_score=float(np.mean((a - (loss < q)) * (loss - q))),
                FZ0=score,
                traffic_full=traffic(hits, a),
                traffic_last250=(
                    traffic(hits[-250:], a) if len(hits) >= 250 else traffic(hits, a)
                ),
                last250_n=min(250, len(hits)),
                last250_exceptions=int(hits[-250:].sum()),
                last250_expected=min(250, len(hits)) * (1 - a),
                full_start=str(pd.Timestamp(g.date.iloc[0]).date()),
                full_end=str(pd.Timestamp(g.date.iloc[-1]).date()),
                last250_start=str(pd.Timestamp(g.date.iloc[-min(250, len(hits))]).date()),
            )
        )
    return pd.DataFrame(rows)


def paired_score_ci(f: pd.DataFrame, a: float = 0.99, reps: int = 1000) -> dict:
    scores = {}
    for name in ["Historical", "Volatility state"]:
        g = f[(f.model == name) & (f.confidence == a)].set_index("date")
        p = 1 - a
        scores[name] = (
            np.maximum(g.loss - g.VaR, 0) / (p * g.ES) + g.VaR / g.ES + np.log(g.ES) - 1
        )
    diff = (scores["Volatility state"] - scores["Historical"]).dropna().to_numpy()
    rng = np.random.default_rng(SEED)
    starts = rng.integers(len(diff), size=(reps, int(np.ceil(len(diff) / 20))))
    indices = ((starts[:, :, None] + np.arange(20)) % len(diff)).reshape(reps, -1)[
        :, : len(diff)
    ]
    return dict(
        mean_difference=float(diff.mean()),
        CI=np.quantile(diff[indices].mean(axis=1), [0.025, 0.975]).tolist(),
        block=20,
        n=len(diff),
        meaning="Negative favours volatility-state model; paired conditional block diagnostic",
    )
