"""Publication figures use genuine pipeline tables, with explicit units."""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .config import ROOT, TEST_START


def build_figures(r, kpis, alloc, risk, sens, f, stress, paths) -> None:
    plt.rcParams.update(
        {
            "font.size": 10,
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#18334B",
            "text.color": "#18334B",
            "figure.constrained_layout.use": True,
        }
    )
    out = ROOT / "outputs/figures"

    def save(fig, name):
        fig.savefig(
            out / f"{name}.png", dpi=165, bbox_inches="tight", facecolor="white"
        )
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.8, 2.6))
    w = alloc["AEGIS minimum variance"]
    ax.bar(
        r.columns,
        w * 100,
        color=["#007E86" if t != "AGG" else "#18334B" for t in r.columns],
    )
    ax.set(
        ylabel="Portfolio allocation (%)",
        title="A bond anchor with capped equity and gold exposure",
    )
    save(fig, "allocation")
    fig, (ax, bx) = plt.subplots(
        2, 1, figsize=(8.8, 4), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    for name in [
        "AEGIS minimum variance",
        "Mean variance",
        "Equal weight",
        "60/40 benchmark",
    ]:
        p = r.loc[TEST_START:].to_numpy() @ alloc[name]
        ww = np.cumprod(1 + p)
        ax.plot(r.loc[TEST_START:].index, ww, label=name, lw=1.5)
        bx.plot(
            r.loc[TEST_START:].index,
            100 * (ww / np.maximum.accumulate(np.r_[1, ww])[1:] - 1),
            lw=1,
        )
    ax.set(
        ylabel="Growth of $1, gross",
        title="Held-out performance is not an allocation-selection sample",
    )
    ax.legend(frameon=False, ncol=2, fontsize=8)
    bx.set(ylabel="Drawdown (%)")
    save(fig, "performance")
    fig, ax = plt.subplots(figsize=(8.8, 3.3))
    sel = risk[risk.confidence == 0.99]
    x = np.arange(len(sel))
    ax.bar(x - 0.16, 100 * sel.VaR, 0.32, label="VaR", color="#007E86")
    ax.bar(x + 0.16, 100 * sel.ES, 0.32, label="ES", color="#18334B")
    ax.set_xticks(x, sel.model)
    ax.set(
        ylabel="One-day loss (% NAV)",
        title="99% risk estimates on the latest 756-return window",
    )
    ax.legend(frameon=False)
    save(fig, "risk")
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(8.8, 3.1))
    ax.plot(sens.threshold_q, 100 * sens.VaR, "o-", label="VaR99")
    ax.plot(sens.threshold_q, 100 * sens.ES, "o-", label="ES99")
    ax.set(
        xlabel="Threshold quantile",
        ylabel="One-day loss (% NAV)",
        title="Threshold sensitivity",
    )
    ax.legend(frameon=False)
    bx.plot(sens.threshold_q, sens["shape"], "o-", color="#007E86")
    bx.axhline(0, color="grey", lw=0.7)
    bx.set(
        xlabel="Threshold quantile", ylabel="GPD shape", title="Tail shape is not fixed"
    )
    save(fig, "evt")
    fig, ax = plt.subplots(figsize=(8.8, 3.2))
    h = f[(f.model == "Historical") & (f.confidence == 0.99)]
    ax.plot(h.date, h.loss * 100, color="#91A2B1", lw=0.7, label="Realized loss")
    ax.plot(h.date, h.VaR * 100, color="#007E86", lw=1, label="Prior-window VaR99")
    hit = h.loss > h.VaR
    ax.scatter(
        h.loc[hit, "date"],
        h.loc[hit, "loss"] * 100,
        color="#BD6338",
        s=15,
        label="Exceptions",
        zorder=3,
    )
    ax.set(
        ylabel="One-day loss (% NAV)",
        title="Every risk forecast precedes its realized loss",
    )
    ax.legend(frameon=False, ncol=3, fontsize=8)
    save(fig, "backtest")
    fig, ax = plt.subplots(figsize=(8.8, 3.1))
    ss = stress[stress.portfolio == "AEGIS minimum variance"]
    ax.barh(
        ss.scenario,
        100 * ss.return_pct,
        color=["#007E86", "#007E86", "#007E86", "#BD6338"],
    )
    ax.axvline(0, color="grey")
    ax.set(
        xlabel="Cumulative / scenario return (%)",
        title="Historical paths and an explicitly assumed funding squeeze",
    )
    save(fig, "stress")
    from .portfolio import frontier

    ff = frontier(r.loc[:"2018-12-31"])
    fig, ax = plt.subplots(figsize=(8.8, 3))
    ax.plot(ff.volatility * 100, ff.expected_return * 100, color="#007E86")
    ks = kpis[kpis.period == "Training"]
    ax.scatter(ks.volatility * 100, ks.arithmetic_return * 100, color="#BD6338")
    for rr in ks.itertuples():
        ax.annotate(
            rr.portfolio,
            (rr.volatility * 100, rr.arithmetic_return * 100),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points",
        )
    ax.set(
        xlabel="Annual volatility (%)",
        ylabel="Annual arithmetic return (%)",
        title="Frontier uses shrunk training moments; dots show net realized training KPIs",
    )
    save(fig, "frontier")
