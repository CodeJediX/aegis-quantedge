"""Positive-loss daily VaR/ES. Statistical log model, exact simple-return wealth."""

import numpy as np
import pandas as pd
from scipy.stats import norm
from .config import SEED, N_SIM, TICKERS


def empirical(loss: np.ndarray, alpha: float) -> dict:
    x = np.asarray(loss, dtype=float)
    if x.ndim != 1 or len(x) < 20 or not np.isfinite(x).all() or not 0 < alpha < 1:
        raise ValueError("Invalid losses or confidence")
    q = float(np.quantile(x, alpha))
    return {"VaR": q, "ES": float(q + np.maximum(x - q, 0).mean() / (1 - alpha))}


def normal_log(portfolio_returns: np.ndarray, alpha: float) -> dict:
    x = np.asarray(portfolio_returns)
    if (
        x.ndim != 1
        or len(x) < 20
        or not np.isfinite(x).all()
        or (x <= -1).any()
        or not 0 < alpha < 1
    ):
        raise ValueError("Invalid gross-return distribution")
    z = np.log1p(x)
    mu = z.mean()
    sd = z.std(ddof=1)
    p = 1 - alpha
    a = mu + sd * norm.ppf(p)
    return dict(
        VaR=float(1 - np.exp(a)),
        ES=float(1 - np.exp(mu + 0.5 * sd**2) * norm.cdf((a - mu - sd**2) / sd) / p),
    )


def mc_losses(
    log_returns: pd.DataFrame, w: np.ndarray, n: int = N_SIM, seed: int = SEED
) -> np.ndarray:
    x = np.asarray(log_returns)
    if (
        x.ndim != 2
        or x.shape[1] != len(w)
        or len(x) < 20
        or not np.isfinite(x).all()
        or n < 100
    ):
        raise ValueError("Invalid simulation input")
    mu = x.mean(axis=0)
    cov = np.cov(x, rowvar=False)
    cov = 0.95 * cov + 0.05 * np.diag(np.diag(cov))
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((n, len(w))) @ np.linalg.cholesky(cov).T
    return -(np.expm1(mu + z) @ w)


def risk_table(
    r: pd.DataFrame, w: np.ndarray, confidences: list, n: int = N_SIM
) -> pd.DataFrame:
    gross = r.to_numpy() @ w
    sim = mc_losses(np.log1p(r), w, n=n)
    rows = []
    for alpha in confidences:
        for model, values in [
            ("Historical", empirical(-gross, alpha)),
            ("Parametric", normal_log(gross, alpha)),
            ("Monte Carlo", empirical(sim, alpha)),
        ]:
            rows.append(dict(model=model, confidence=alpha, **values))
    return pd.DataFrame(rows)


def contributions(r: pd.DataFrame, w: np.ndarray, alpha: float = 0.99) -> pd.DataFrame:
    loss = -(r.to_numpy() @ w)
    q = np.quantile(loss, alpha)
    # Historical ES subgradient uses fractional boundary mass to exactly sum.
    tail = loss > q
    weights = tail.astype(float) / (len(loss) * (1 - alpha))
    # Differentiate the linearly interpolated quantile, including fractional mass.
    order = np.argsort(loss)
    position = (len(loss) - 1) * alpha
    lo = int(np.floor(position))
    hi = int(np.ceil(position))
    fraction = position - lo
    correction = 1 - weights.sum()
    weights[order[lo]] += correction * (1 - fraction)
    weights[order[hi]] += correction * fraction
    mes = weights @ (-r.to_numpy())
    ces = w * mes
    # Gaussian simple-return VaR has an exact Euler derivative.
    cov = r.cov().to_numpy()
    mu = r.mean().to_numpy()
    sigma = np.sqrt(w @ cov @ w)
    z = norm.ppf(alpha)
    mvar = -mu + z * (cov @ w) / sigma
    cvar = w * mvar
    return pd.DataFrame(
        dict(
            ticker=TICKERS,
            weight=w,
            marginal_ES=mes,
            component_ES=ces,
            marginal_normal_VaR=mvar,
            component_normal_VaR=cvar,
            ES_share=ces / ces.sum(),
        )
    )


def filtered_forecast(history: np.ndarray, alpha: float) -> dict:
    """Interpretable volatility state: 20-day / long-run ratio applied to past shocks."""
    x = np.asarray(history)
    mu = x.mean()
    long = x.std(ddof=1)
    short = x[-20:].std(ddof=1)
    ratio = np.clip(short / long, 0.5, 3)
    return dict(
        **empirical(-(mu + (x - mu) * ratio), alpha), volatility_ratio=float(ratio)
    )
