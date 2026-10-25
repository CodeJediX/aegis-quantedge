"""Selected-portfolio analysis, explicit policy checks and training-only optimization.

This layer never changes the locked research artifacts. Fractions are the canonical
unit internally; every dollar conversion multiplies by the same reference capital.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .config import NAV, TICKERS, TRAIN_END, TEST_START, BOUNDS, EQUITY, HYPOTHETICAL, TC
from .portfolio import validate_weights, path, metrics, moments
from .risk import empirical
from .stress import historical


def usd(fraction, capital=NAV):
    if not np.isfinite(fraction) or not np.isfinite(capital) or capital <= 0:
        raise ValueError("Dollar conversion requires a finite fraction and positive reference capital.")
    return float(fraction * capital)


def allocation_id(weights):
    values = validate_weights(weights)
    return hashlib.sha256(json.dumps(values.round(12).tolist(), separators=(",", ":")).encode()).hexdigest()[:12]


@dataclass(frozen=True)
class Limits:
    volatility: float = 0.10
    drawdown: float = 0.15
    daily_ES99: float = 0.025
    scenario_loss: float = 0.15
    objective: float = 0.04
    bond_min: float = 0.35
    equity_cap: float = 0.50

    def __post_init__(self):
        values = np.asarray(list(asdict(self).values()))
        if not np.isfinite(values).all():
            raise ValueError("All proposed risk limits must be finite.")
        if not all(0 < v <= 1 for v in [self.volatility, self.drawdown, self.daily_ES99, self.scenario_loss]):
            raise ValueError("Risk limits must be positive fractions no greater than 100%.")
        if not -0.5 <= self.objective <= 0.5 or not 0.35 <= self.bond_min <= 0.70 or not 0.20 <= self.equity_cap <= 0.50:
            raise ValueError("Proposed objectives and allocation limits are outside the supported mandate ranges.")


def allocation_checks(weights, limits):
    w = validate_weights(weights)
    rows = []
    bounds = list(BOUNDS)
    bounds[3] = (limits.bond_min, 0.70)
    for ticker, value, (lo, hi) in zip(TICKERS, w, bounds):
        rows.append(dict(check=ticker + " weight", value=float(value), minimum=lo, maximum=hi,
                         status="PASS" if lo - 1e-8 <= value <= hi + 1e-8 else "FAIL", category="Asset constraint"))
    eq = float(w[EQUITY].sum())
    rows.append(dict(check="Combined equity", value=eq, minimum=0.20, maximum=limits.equity_cap,
                     status="PASS" if 0.20 - 1e-8 <= eq <= limits.equity_cap + 1e-8 else "FAIL", category="Asset constraint"))
    return pd.DataFrame(rows)


def analyze(r, rf, weights, name, lookback=756, limits=None):
    """Compute all selected-portfolio values from the same prices/weights/capital."""
    limits = limits or Limits()
    w = validate_weights(weights)
    if list(r.columns) != TICKERS or not r.index.is_monotonic_increasing or r.index.has_duplicates:
        raise ValueError("Analysis requires the ordered seven-ETF universe and unique chronological dates.")
    train = r.loc[:TRAIN_END]
    test = r.loc[TEST_START:]
    if len(train) < 100 or len(test) < 2 or lookback < 100 or lookback > len(r):
        raise ValueError("Insufficient training, test or lookback observations.")
    pp = path(r, w)
    benchmark = path(r, np.array([0.6, 0, 0, 0.4, 0, 0, 0])).net
    kpi = metrics(pp.loc[test.index, "net"], test.SPY, benchmark.loc[test.index], rf.loc[test.index])
    kpi["annual_turnover"] = float(pp.loc[test.index,"turnover"].mean()*252)
    mu, covariance = moments(train)
    stress, paths = historical(r, {name: w})
    es = empirical(-(r.iloc[-lookback:].to_numpy() @ w), 0.99)["ES"]
    expected = float(w @ mu)
    values = [
        ("Held-out annual volatility", kpi["volatility"], limits.volatility, "maximum"),
        ("Held-out maximum drawdown", kpi["max_drawdown"], limits.drawdown, "maximum"),
        ("Training maximum net drawdown", float(-pp.loc[:TRAIN_END,"drawdown"].min()), limits.drawdown, "maximum"),
        ("Current daily historical ES99", es, limits.daily_ES99, "maximum"),
        ("Worst scenario terminal loss", max(0.0, float((-stress.return_pct).max())), limits.scenario_loss, "maximum"),
        ("Worst historical replay drawdown", float(stress[stress.n > 1].max_drawdown.max()), limits.drawdown, "maximum"),
        ("Training estimated annual arithmetic return", expected, limits.objective, "minimum"),
    ]
    checks = allocation_checks(w, limits).to_dict("records")
    for label, value, limit, direction in values:
        passed = np.isfinite(value) and (value <= limit + 1e-8 if direction == "maximum" else value >= limit - 1e-8)
        checks.append(dict(check=label, value=value, minimum=limit if direction == "minimum" else None,
                           maximum=limit if direction == "maximum" else None,
                           status="PASS" if passed else "FAIL", category="Risk / objective"))
    return dict(name=name, weights=w, allocation_id=allocation_id(w), capital=NAV,
                kpi=kpi, expected_return=expected, training_volatility=float(np.sqrt(w @ covariance @ w)),
                ES99=es, stress=stress, crisis_paths=paths, path=pp, checks=pd.DataFrame(checks),
                limits=asdict(limits), lookback=lookback, test_start=str(test.index[0].date()),
                test_end=str(test.index[-1].date()), latest_start=str(r.index[-lookback].date()),
                latest_end=str(r.index[-1].date()))


def recommendation(result, validation=None):
    """Automated triage is never recorded as a human investment approval."""
    failed = result["checks"].query("status == 'FAIL'")
    actions = []
    if len(failed):
        actions.extend("Resolve " + str(row.check) + ": observed " + f"{row.value:.2%}" + "." for row in failed.itertuples())
    valid = False
    if validation is not None and len(validation):
        hist = validation[(validation.model == "Historical") & np.isclose(validation.confidence, 0.99)]
        if len(hist):
            row = hist.iloc[0]
            valid = (pd.notna(row.kupiec_p) and row.kupiec_p >= 0.05 and
                     pd.notna(row.independence_p) and row.independence_p >= 0.05 and
                     pd.notna(row.conditional_p) and row.conditional_p >= 0.05 and row.traffic_last250 == "Green")
    if not valid:
        actions.append("Run or review the selected allocation's out-of-sample 99% coverage, independence and latest-250 diagnostics.")
    asset_fail = failed.category.eq("Asset constraint").any()
    status = "REJECT" if asset_fail else "REVISE" if len(failed) or not valid else "APPROVE"
    actions.append("Obtain independent human review, confirm spending needs and agree the final mandate before funding.")
    return dict(status=status, failed_checks=len(failed), validation_pass=bool(valid), actions=actions,
                human_approval="PENDING - no human investment approval recorded",
                scope="Automated historical model assessment; not a funding authorization or capital guarantee")


def compare(r, rf, allocations, lookback=756, limits=None):
    rows = []
    for name, weights in allocations.items():
        result = analyze(r, rf, weights, name, lookback, limits)
        rows.append(dict(portfolio=name, allocation_id=result["allocation_id"],
                         expected_return=result["expected_return"], **result["kpi"],
                         ES99=result["ES99"], ES99_USD=usd(result["ES99"]),
                         worst_scenario_loss=max(0.0, float((-result["stress"].return_pct).max())),
                         worst_replay_drawdown=float(result["stress"].query("n > 1").max_drawdown.max()),
                         failed_checks=int(result["checks"].status.eq("FAIL").sum())))
    return pd.DataFrame(rows)


def optimize(training_returns, limits=None, priority="Capital preservation"):
    """Only pre-2019 observations enter the objective or hard constraints.

    Full-history crises are subsequently assessed, never used to select weights.
    Failure means no feasible solution was found, not a proof of global infeasibility.
    """
    limits = limits or Limits()
    r = training_returns
    if len(r) < 100 or r.index.max() > pd.Timestamp(TRAIN_END) or list(r.columns) != TICKERS:
        raise ValueError("Optimizer requires the seven ETFs and training observations ending by 2018-12-31.")
    if priority not in {"Capital preservation", "Balanced growth", "Improved returns"}:
        raise ValueError("Unknown investment priority.")
    mu, cov = moments(r)
    x = r.to_numpy()
    shock = np.array([HYPOTHETICAL[t] for t in TICKERS])

    def drawdown(w):
        gross = x @ w
        drift = w * (1+x)/(1+gross[:,None])
        turnover = np.r_[0,np.abs(drift[:-1]-w).sum(axis=1)]
        net = (1-TC*turnover)*(1+gross)-1
        wealth = np.cumprod(1 + net)
        return float(np.max(1 - wealth / np.maximum.accumulate(np.r_[1, wealth])[1:]))

    def conditions(w):
        return np.array([w[EQUITY].sum() - 0.20, limits.equity_cap - w[EQUITY].sum(),
                         limits.volatility ** 2 - w @ cov @ w, w @ mu - limits.objective,
                         limits.drawdown - drawdown(w), limits.scenario_loss + w @ shock,
                         limits.daily_ES99 - empirical(-(x @ w), 0.99)["ES"]])

    aversion = {"Capital preservation": 0.0, "Balanced growth": 0.15, "Improved returns": 0.50}[priority]
    objective = lambda w: 100 * (w @ cov @ w - aversion * (w @ mu))
    bounds = list(BOUNDS)
    bounds[3] = (limits.bond_min, 0.70)
    candidates = []
    for initial in [np.array([0.15, 0, 0, 0.65, 0.15, 0, 0.05]), np.array([0.20, 0, 0, 0.60, 0.20, 0, 0])]:
        opt = minimize(objective, initial, method="SLSQP", bounds=bounds,
                       constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1},
                                    {"type": "ineq", "fun": conditions}],
                       options={"maxiter": 400, "ftol": 1e-10})
        if opt.success and np.min(conditions(opt.x)) >= -1e-7 and allocation_checks(opt.x, limits).status.eq("PASS").all():
            candidates.append(opt)
    if not candidates:
        raise ValueError("No allocation satisfying all training-period limits was found. Review the return target and proposed limits, or reject the mandate; no failed constraint has been marked as passed.")
    best = min(candidates, key=lambda candidate: candidate.fun)
    return validate_weights(best.x)


def library_json(library, dataset_version):
    records = {}
    if len(library) > 25:
        raise ValueError("Keep at most 25 saved allocations in one library.")
    for name, weights in library.items():
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 80:
            raise ValueError("Allocation names must contain 1-80 characters.")
        records[name.strip()] = dict(zip(TICKERS, validate_weights(weights).tolist()))
    return json.dumps(dict(schema_version=1, dataset_version=dataset_version, generated_utc=datetime.now(timezone.utc).isoformat(), portfolios=records), indent=2, allow_nan=False)


def parse_library(raw):
    if len(raw) > 1_000_000:
        raise ValueError("Allocation library must be smaller than 1 MB.")
    try:
        data = json.loads(raw)
        if data["schema_version"] != 1 or not isinstance(data["portfolios"], dict) or not 1 <= len(data["portfolios"]) <= 25:
            raise ValueError("Unsupported or empty allocation library.")
        result = {}
        for name, weights in data["portfolios"].items():
            if not isinstance(weights, dict) or set(weights) != set(TICKERS):
                raise ValueError("Each saved allocation must specify exactly the seven permitted ETFs.")
            result[name] = validate_weights(np.array([weights[t] for t in TICKERS])).tolist()
        library_json(result, data.get("dataset_version", "unknown"))
        return result
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid allocation-library structure. Import an AEGIS JSON library.") from exc


def what_if(weights, equity_shock, rate_bps, bond_duration, gold_shock):
    w = validate_weights(weights)
    vals = np.array([equity_shock, rate_bps, bond_duration, gold_shock], dtype=float)
    if not np.isfinite(vals).all() or not -0.8 <= equity_shock <= 0.8 or not -0.8 <= gold_shock <= 0.8 or not -500 <= rate_bps <= 500 or not 0 <= bond_duration <= 15:
        raise ValueError("What-if assumptions are outside supported ranges.")
    shocks = np.full(7, equity_shock)
    shocks[3] = -bond_duration * rate_bps / 10000
    shocks[4] = gold_shock
    return pd.DataFrame(dict(ticker=TICKERS, weight=w, assumed_return=shocks,
                             contribution=w * shocks, contribution_USD=[usd(v) for v in w * shocks]))
