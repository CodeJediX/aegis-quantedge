"""Reproduce the AEGIS research, documents and presentation from approved snapshots."""

import argparse
import json
import logging
import time
import importlib.metadata as md
import numpy as np
import pandas as pd
from src.config import (
    ROOT,
    TICKERS,
    NAV,
    SEED,
    WINDOW,
    N_SIM,
    CONFIDENCES,
    TRAIN_END,
    DEV_END,
    TEST_START,
    folders,
)
from src.data import download, load
from src.portfolio import candidates, path, metrics, capm, frontier, moments
from src.risk import risk_table, contributions, mc_losses, empirical
from src.evt import fit, estimate, sensitivity, bootstrap
from src.backtesting import forecasts, summarize, paired_score_ci
from src.stress import historical
from src.decision import scorecard, evidence_ledger

LOG = logging.getLogger("AEGIS")


def save(name: str, frame: pd.DataFrame, index: bool = False) -> None:
    frame.to_csv(ROOT / f"outputs/tables/{name}.csv", index=index, float_format="%.12g")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reproduce", action="store_true")
    parser.add_argument("--refresh-data", action="store_true")
    parser.add_argument("--skip-documents", action="store_true")
    args = parser.parse_args()
    folders()
    start = time.perf_counter()
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    download(args.refresh_data)
    prices, r, logs, rf, audit = load()
    train = r.loc[:TRAIN_END]
    test = r.loc[TEST_START:]
    alloc = candidates(train)
    selected = "AEGIS minimum variance"
    w = alloc[selected]
    mu, cov = moments(train)
    save("allocations", pd.DataFrame(alloc, index=TICKERS), True)
    div = []
    for name, ww in alloc.items():
        hhi = float(ww @ ww)
        div.append(
            dict(
                portfolio=name,
                HHI=hhi,
                effective_holdings=1 / hhi,
                diversification_ratio=float(
                    ww @ np.sqrt(np.diag(cov)) / np.sqrt(ww @ cov @ ww)
                ),
                equity_weight=float(ww[[0, 1, 2, 5, 6]].sum()),
            )
        )
    save("diversification", pd.DataFrame(div))
    full = {name: path(r, ww) for name, ww in alloc.items()}
    bench = full["60/40 benchmark"].net
    rows = []
    for period, idx in [
        ("Training", train.index),
        ("Development", r.loc["2019-01-01":DEV_END].index),
        ("Test", test.index),
    ]:
        for name, frame in full.items():
            k = metrics(
                frame.loc[idx, "net"], r.loc[idx, "SPY"], bench.loc[idx], rf.loc[idx]
            )
            rows.append(
                dict(
                    period=period,
                    portfolio=name,
                    **k,
                    annual_turnover=float(frame.loc[idx, "turnover"].mean() * 252),
                )
            )
    kpis = pd.DataFrame(rows)
    save("kpis", kpis)
    save("capm_training", capm(train, rf.loc[train.index]))
    save("frontier", frontier(train))
    save(
        "cost_sensitivity",
        pd.DataFrame(
            [
                dict(
                    cost_bps=cost * 10000,
                    **metrics(
                        path(test, w, tc=cost).net,
                        test.SPY,
                        bench.loc[test.index],
                        rf.loc[test.index],
                    ),
                )
                for cost in [0, 0.001, 0.0025]
            ]
        ),
    )
    wealth = pd.DataFrame({name: frame.net for name, frame in full.items()})
    wealth.index.name = "date"
    save("portfolio_returns", wealth, True)
    latest = r.iloc[-WINDOW:]
    risk = risk_table(latest, w, CONFIDENCES)
    ev = fit(-(latest.to_numpy() @ w))
    evrows = []
    for a in [0.95, 0.99]:
        evrows.append(dict(model="EVT", confidence=a, **estimate(ev, a)))
    risk = pd.concat([risk, pd.DataFrame(evrows)], ignore_index=True)
    risk["VaR_USD"] = risk.VaR * NAV
    risk["ES_USD"] = risk.ES * NAV
    save("risk_snapshot", risk)
    evt_sens = sensitivity(-(latest.to_numpy() @ w))
    save("evt_sensitivity", evt_sens)
    evt_ci = bootstrap(-(latest.to_numpy() @ w))
    save("risk_contributions", contributions(latest, w))
    LOG.info("Rolling one-step forecasts: 756 prior returns per date; 10,000 MC draws")
    f = forecasts(r, w)
    save("forecasts", f)
    dev = f[f.date <= pd.Timestamp(DEV_END)]
    oos = f[f.date >= pd.Timestamp(TEST_START)]
    bt = summarize(oos)
    save("backtesting_test", bt)
    save("backtesting_development", summarize(dev))
    regime = paired_score_ci(oos)
    stress, stresspaths = historical(r, alloc)
    save("stress", stress)
    save("crisis_paths", stresspaths)
    k = kpis[(kpis.period == "Test") & (kpis.portfolio == selected)].iloc[0].to_dict()
    h99 = risk[(risk.model == "Historical") & (risk.confidence == 0.99)].iloc[0]
    card = scorecard(k, float(h99.ES), stress[stress.portfolio == selected], bt, w)
    save("scorecard", card)
    save("evidence_ledger", evidence_ledger())
    sim = mc_losses(np.log1p(latest), w)
    convergence = []
    for n in [5000, 10000, 25000, N_SIM]:
        convergence.append(dict(draws=n, **empirical(sim[:n], 0.99)))
    save("mc_convergence", pd.DataFrame(convergence))
    batches = [empirical(x, 0.99)["ES"] for x in np.array_split(sim, 10)]
    # No weighted composite score: expose how policy conclusions change with risk appetite.
    sensitivity_rows = []
    for mult in [0.8, 1, 1.2]:
        subset = card[card.direction == "maximum"]
        passed = int((subset.value <= subset.proposed_limit * mult).sum())
        sensitivity_rows.append(
            dict(
                limit_multiplier=mult,
                within_limits=passed,
                total=len(subset),
                weighting="No composite weights",
            )
        )
    save("policy_sensitivity", pd.DataFrame(sensitivity_rows))
    summary = dict(
        team="Quantum-X",
        brand="AEGIS",
        data=audit,
        capital=NAV,
        seed=SEED,
        train_end=TRAIN_END,
        development_end=DEV_END,
        test_start=str(test.index[0].date()),
        test_end=str(test.index[-1].date()),
        n_train=len(train),
        n_test=len(test),
        candidate=selected,
        weights=dict(zip(TICKERS, w.tolist())),
        training_expected_arithmetic=float(w @ mu),
        training_volatility=float(np.sqrt(w @ cov @ w)),
        assumed_nominal_objective=0.04,
        assumed_inflation=0.025,
        investment_horizon="10+ years; annual governance review",
        out_of_sample=k,
        latest_window_start=str(latest.index[0].date()),
        latest_window_end=str(latest.index[-1].date()),
        evt_fit=ev,
        evt_bootstrap=evt_ci,
        regime_comparison=regime,
        MC_ES99_standard_error=float(np.std(batches, ddof=1) / np.sqrt(10)),
        proposal_status="ADJUST mandate / pending independent human-team review",
        policy_reviews=card[card.status == "Review"].component.tolist(),
        rejected_alternatives="Equal weight and 60/40 exceed proposed equity budget; mean-variance mean estimates are uncertain",
        versions={
            p: md.version(p)
            for p in [
                "numpy",
                "pandas",
                "scipy",
                "statsmodels",
                "streamlit",
                "plotly",
                "yfinance",
                "reportlab",
            ]
        },
    )
    (ROOT / "outputs/results/summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False)
    )
    from src.figures import build_figures

    build_figures(r, kpis, alloc, risk, evt_sens, oos, stress, stresspaths)
    if not args.skip_documents:
        from src.reporting import build_reports

        build_reports(summary)
        from scripts.prepare_qa import main as prepare_qa
        from scripts.rehearsal import main as prepare_rehearsal

        prepare_qa()
        prepare_rehearsal()
    LOG.info("Completed in %.1fs", time.perf_counter() - start)
    print(
        json.dumps(
            {
                key: summary[key]
                for key in [
                    "candidate",
                    "weights",
                    "test_start",
                    "test_end",
                    "proposal_status",
                    "policy_reviews",
                ]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
