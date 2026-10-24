"""Historical replay uses genuine daily return paths; shocks are labelled assumptions."""

import numpy as np
import pandas as pd
from .config import SCENARIOS, HYPOTHETICAL, NAV, TICKERS


def historical(r: pd.DataFrame, allocations: dict) -> tuple:
    rows = []
    paths = []
    for scenario, (start, end) in SCENARIOS.items():
        event = r.loc[start:end]
        if len(event) < 15 or len(event.columns) != 7:
            raise ValueError("Incomplete crisis coverage")
        for name, w in allocations.items():
            p = event.to_numpy() @ w
            wealth = np.cumprod(1 + p)
            prior = np.maximum.accumulate(np.r_[1, wealth])[:-1]
            draw = wealth / np.maximum.accumulate(np.r_[1, wealth])[1:] - 1
            trough = int(np.argmin(draw))
            reference = np.maximum.accumulate(np.r_[1, wealth])[trough + 1]
            # Full continuation uses the same fixed hindsight allocation, labelled replay.
            continuation = r.loc[start:].to_numpy() @ w
            full = np.cumprod(1 + continuation)
            recover = np.flatnonzero(
                (np.arange(len(full)) > trough) & (full >= reference)
            )
            date = (
                str(r.loc[start:].index[recover[0]].date())
                if len(recover)
                else "Not recovered by sample end"
            )
            # Self-financing daily rebalanced P&L contributions include changing NAV.
            previous = np.r_[1, wealth[:-1]]
            contributions = (previous[:, None] * event.to_numpy() * w).sum(axis=0)
            rows.append(
                dict(
                    scenario=scenario,
                    portfolio=name,
                    start=str(event.index[0].date()),
                    end=str(event.index[-1].date()),
                    n=len(event),
                    return_pct=float(wealth[-1] - 1),
                    USD=float(NAV * (wealth[-1] - 1)),
                    max_drawdown=float(-draw.min()),
                    trough=str(event.index[trough].date()),
                    recovery_date=date,
                    **{t: float(v) for t, v in zip(TICKERS, contributions)}
                )
            )
            paths.extend(
                dict(
                    scenario=scenario,
                    portfolio=name,
                    date=date_,
                    wealth=float(v),
                    drawdown=float(dd),
                )
                for date_, v, dd in zip(event.index, wealth, draw)
            )
    for name, w in allocations.items():
        shock = np.array([HYPOTHETICAL[t] for t in TICKERS])
        v = float(w @ shock)
        rows.append(
            dict(
                scenario="Hypothetical funding squeeze",
                portfolio=name,
                start="Assumed simultaneous shock",
                end="One scenario event",
                n=1,
                return_pct=v,
                USD=NAV * v,
                max_drawdown=-v,
                trough="N/A",
                recovery_date="N/A: no invented recovery path",
                **{t: float(ww * xx) for t, ww, xx in zip(TICKERS, w, shock)}
            )
        )
    return pd.DataFrame(rows), pd.DataFrame(paths)
