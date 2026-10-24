"""Constrained Markowitz alternatives, CAPM and exact daily rebalance accounting."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from .config import TICKERS, BOUNDS, EQUITY, TC


def validate_weights(w: np.ndarray) -> np.ndarray:
    w = np.asarray(w, dtype=float)
    if (
        w.shape != (7,)
        or not np.isfinite(w).all()
        or (w < 0).any()
        or abs(w.sum() - 1) > 1e-7
    ):
        raise ValueError("Seven finite nonnegative weights summing to one are required")
    return w


def moments(r: pd.DataFrame) -> tuple:
    cov = r.cov().to_numpy() * 252
    cov = 0.9 * cov + 0.1 * np.diag(np.diag(cov))
    mu = r.mean().to_numpy() * 252
    # Equal-prior shrinkage reduces sensitivity to historical mean estimation.
    mu = 0.5 * mu + 0.5 * mu.mean()
    return mu, cov


def solve(
    r: pd.DataFrame,
    kind: str = "Minimum variance",
    target: float | None = None,
    bond_min: float = 0.35,
    equity_cap: float = 0.50,
) -> np.ndarray:
    mu, cov = moments(r)
    cons = [
        {"type": "eq", "fun": lambda w: w.sum() - 1},
        {"type": "ineq", "fun": lambda w: w[EQUITY].sum() - 0.20},
        {"type": "ineq", "fun": lambda w: equity_cap - w[EQUITY].sum()},
    ]
    bounds = list(BOUNDS)
    bounds[3] = (bond_min, 0.70)
    if target is not None:
        cons.append({"type": "ineq", "fun": lambda w: w @ mu - target})
    if kind == "Mean variance":
        objective = lambda w: 6 * (w @ cov @ w) / 2 - w @ mu
    elif kind == "Risk parity":

        def objective(w):
            rc = w * (cov @ w)
            return 1e4 * np.sum((rc / rc.sum() - 1 / 7) ** 2)

    else:
        objective = lambda w: 1e4 * (w @ cov @ w)
    opt = minimize(
        objective,
        np.array([0.10, 0.05, 0.05, 0.60, 0.15, 0.02, 0.03]),
        method="SLSQP",
        bounds=bounds,
        constraints=cons,
        options={"maxiter": 1000, "ftol": 1e-11},
    )
    if not opt.success:
        raise ValueError("Infeasible constraints or optimiser failure: " + opt.message)
    w = np.round(np.maximum(opt.x, 0), 10)
    w[w < 1e-8] = 0
    w[np.argmax(w)] += 1 - w.sum()
    return validate_weights(w)


def candidates(r: pd.DataFrame) -> dict:
    return {
        "AEGIS minimum variance": solve(r),
        "Mean variance": solve(r, "Mean variance"),
        "Constrained risk parity": solve(r, "Risk parity"),
        "Equal weight": np.ones(7) / 7,
        "60/40 benchmark": np.array([0.6, 0, 0, 0.4, 0, 0, 0]),
    }


def path(r: pd.DataFrame, w: np.ndarray, tc: float = TC) -> pd.DataFrame:
    w = validate_weights(w)
    if (
        r.shape[1] != 7
        or len(r) == 0
        or not np.isfinite(r.to_numpy()).all()
        or (r.to_numpy() <= -1).any()
        or tc < 0
    ):
        raise ValueError("Invalid portfolio return input")
    gross = r.to_numpy() @ w
    drift = w * (1 + r.to_numpy()) / (1 + gross[:, None])
    turnover = np.r_[0, np.abs(drift[:-1] - w).sum(axis=1)]
    # Trades paid before the next day's portfolio return; initial establishment excluded.
    net = (1 - tc * turnover) * (1 + gross) - 1
    wealth = np.cumprod(1 + net)
    peak = np.maximum.accumulate(np.r_[1, wealth])[1:]
    return pd.DataFrame(
        {
            "gross": gross,
            "net": net,
            "wealth": wealth,
            "drawdown": wealth / peak - 1,
            "turnover": turnover,
        },
        index=r.index,
    )


def metrics(
    p: pd.Series, market: pd.Series, benchmark: pd.Series, rf: pd.Series
) -> dict:
    p, market, benchmark, rf = [
        np.asarray(x, dtype=float) for x in [p, market, benchmark, rf]
    ]
    n = len(p)
    wealth = np.cumprod(1 + p)
    draw = wealth / np.maximum.accumulate(np.r_[1, wealth])[1:] - 1
    excess = p - rf
    mx = market - rf
    active = p - benchmark
    vol = p.std(ddof=1) * np.sqrt(252)
    down = np.sqrt(np.mean(np.minimum(excess, 0) ** 2)) * np.sqrt(252)
    beta = np.cov(excess, mx, ddof=1)[0, 1] / np.var(mx, ddof=1)
    cagr = wealth[-1] ** (252 / n) - 1
    dd = float(-draw.min())
    div = lambda a, b: float(a / b) if abs(b) > 1e-12 else None
    return dict(
        CAGR=float(cagr),
        arithmetic_return=float(p.mean() * 252),
        volatility=float(vol),
        Sharpe=div(excess.mean() * 252, vol),
        Sortino=div(excess.mean() * 252, down),
        Treynor=div(excess.mean() * 252, beta),
        Jensen_alpha=float((excess.mean() - beta * mx.mean()) * 252),
        information_ratio=div(active.mean() * 252, active.std(ddof=1) * np.sqrt(252)),
        max_drawdown=dd,
        Calmar=div(cagr, dd),
        beta=float(beta),
        cumulative_return=float(wealth[-1] - 1),
    )


def frontier(r: pd.DataFrame) -> pd.DataFrame:
    mu, cov = moments(r)
    rows = []
    for target in np.linspace(mu.min(), mu.max(), 35):
        try:
            w = solve(r, target=float(target))
            rows.append(
                dict(
                    expected_return=w @ mu,
                    volatility=np.sqrt(w @ cov @ w),
                    **dict(zip(TICKERS, w))
                )
            )
        except ValueError:
            continue
    return pd.DataFrame(rows)


def capm(r: pd.DataFrame, rf: pd.Series) -> pd.DataFrame:
    mx = r.SPY - rf
    premium = mx.mean() * 252
    rows = []
    for t in TICKERS:
        ex = r[t] - rf
        beta = np.cov(ex, mx, ddof=1)[0, 1] / mx.var()
        rows.append(
            dict(
                ticker=t,
                beta=beta,
                annual_alpha=(ex.mean() - beta * mx.mean()) * 252,
                capm_implied_return=rf.mean() * 252 + beta * premium,
            )
        )
    return pd.DataFrame(rows)
