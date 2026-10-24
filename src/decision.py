"""Transparent policy checks. No weighted composite score or machine approval."""

import numpy as np
import pandas as pd
from .config import PROPOSED_LIMITS


def scorecard(
    kpi: dict,
    risk99: float,
    stress: pd.DataFrame,
    backtest: pd.DataFrame,
    w: np.ndarray,
) -> pd.DataFrame:
    # Thresholds are proposal assumptions, not known client limits or industry standards.
    tests = [
        (
            "Net OOS annual volatility",
            kpi["volatility"],
            PROPOSED_LIMITS["volatility"],
            "maximum",
        ),
        (
            "Net OOS drawdown",
            kpi["max_drawdown"],
            PROPOSED_LIMITS["drawdown"],
            "maximum",
        ),
        (
            "Current daily historical ES99",
            risk99,
            PROPOSED_LIMITS["daily_ES99"],
            "maximum",
        ),
        (
            "Worst replay/scenario loss",
            float((-stress.return_pct).max()),
            PROPOSED_LIMITS["scenario_loss"],
            "maximum",
        ),
        (
            "Worst historical replay drawdown",
            float(stress[stress.n > 1].max_drawdown.max()),
            PROPOSED_LIMITS["drawdown"],
            "maximum",
        ),
        ("Largest holding", float(w.max()), 0.70, "maximum"),
        ("Net OOS CAGR", kpi["CAGR"], 0.04, "minimum"),
    ]
    rows = [
        dict(
            component=name,
            value=v,
            proposed_limit=lim,
            status=(
                "Within"
                if (v <= lim + 1e-9 if kind == "maximum" else v >= lim - 1e-9)
                else "Review"
            ),
            direction=kind,
        )
        for name, v, lim, kind in tests
    ]
    hist = backtest[
        (backtest.model == "Historical") & (backtest.confidence == 0.99)
    ].iloc[0]
    rows.append(
        dict(
            component="Historical VaR99 conditional coverage p",
            value=hist.conditional_p,
            proposed_limit=0.05,
            status=(
                "Review"
                if pd.isna(hist.conditional_p) or hist.conditional_p < 0.05
                else "No rejection"
            ),
            direction="diagnostic",
        )
    )
    return pd.DataFrame(rows)


def evidence_ledger() -> pd.DataFrame:
    frame = pd.DataFrame(
        [
            [
                "Portfolio KPIs",
                "Daily net simple returns; 252 trading days",
                "2023-2026 held-out path",
                "Fees approximated by 10bp L1 turnover; no spending",
            ],
            [
                "CAPM",
                "OLS-equivalent covariance beta; SPY market proxy",
                "2005-2018 training",
                "Single-factor diagnostic, not an investable alpha forecast",
            ],
            [
                "Historical VaR/ES",
                "Empirical positive-loss quantile and excess mean",
                "Rolling 756 observations",
                "Bounded historical support; volatility clusters",
            ],
            [
                "Parametric VaR/ES",
                "Normal portfolio log gross return, exact lognormal tail",
                "Rolling 756 observations",
                "Thin tails and one-day conditional stationarity",
            ],
            [
                "Monte Carlo VaR/ES",
                "Multivariate Gaussian log shocks; 5% diagonal covariance shrinkage",
                "Rolling 756; 10,000 draws, snapshot 50,000",
                "Normal innovations omit heavy tails; exact asset aggregation differs from portfolio-log model",
            ],
            [
                "EVT",
                "90th-percentile POT; GPD MLE; 40 minimum exceedances",
                "Rolling 756, recent-fit block intervals",
                "Threshold bias, clustering and parameter instability",
            ],
            [
                "Regime extension",
                "20-day to long-run volatility ratio, clipped .5-3",
                "Strict one-step walk-forward",
                "Adaptive scale may overreact; not a trained classifier",
            ],
            [
                "Crisis replay",
                "Daily target-weight historical return path",
                "2008, 2020, 2022",
                "Hindsight allocation replay, no contemporaneous strategy claim",
            ],
            [
                "Policy scorecard",
                "Separate limit checks without weighted total",
                "Proposed limits in config",
                "Illustrative risk appetite; requires client approval",
            ],
            [
                "Hypothetical shock",
                "User-visible assumed simultaneous asset returns",
                "One scenario, not a probability model",
                "No scenario probability or recovery inferred",
            ],
        ],
        columns=["metric", "method", "window", "limitation"],
    )
    frame["source"] = (
        "Yahoo/yfinance adjusted closes; snapshot hashes in data/metadata; FRED DTB3 for performance ratios"
    )
    frame["version_configuration"] = (
        "AEGIS 1.0; src/config.py; installed versions in outputs/results/summary.json"
    )
    frame["validation_evidence"] = [
        "tests: wealth, cost signs, metric references; kpis.csv",
        "SPY covariance identity; capm_training.csv; single-factor limitation",
        "Rolling coverage, exceptions, ES residual/FZ0; backtesting_test.csv",
        "Dense-quantile lognormal reference; rolling coverage",
        "Fixed seed, mc_convergence.csv and batch ES SE in summary",
        "Exponential reference; threshold sensitivity; 150 block fits and intervals in summary",
        "Paired FZ0 block interval; conditional coverage; negative result retained",
        "Actual dates/coverage and asset P&L additivity; stress.csv and crisis_paths.csv",
        "Explicit proposed limits with +/-20% sensitivity; no weighted total",
        "Assumed shocks in config; contribution sum identity; no probability claim",
    ]
    return frame
