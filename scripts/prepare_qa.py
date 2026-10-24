"""Generate defence questions from executed results, not remembered market values."""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    s = json.loads((ROOT / "outputs/results/summary.json").read_text())
    k = s["out_of_sample"]
    bt = pd.read_csv(ROOT / "outputs/tables/backtesting_test.csv")
    h = bt[(bt.model == "Historical") & (bt.confidence == 0.99)].iloc[0]
    questions = [
        (
            "Why this allocation?",
            "It minimizes pre-2019 variance under proposed asset limits, without selecting on later returns. Weights: "
            + ", ".join(f"{t} {v:.2%}" for t, v in s["weights"].items() if v > 1e-6)
            + ".",
        ),
        (
            "Why call it conservative?",
            f'Equity exposure is capped and bonds dominate. Test volatility is {k["volatility"]:.2%}, but rate and crisis risks remain. This is relative risk restraint, not guaranteed capital protection.',
        ),
        (
            "What is the actual decision?",
            "ADJUST before funding. Resolve crisis tolerance, spending and rebalancing. If the candidate breaches a binding limit, substantiate another eligible allocation or reject it.",
        ),
        (
            "What return objective is assumed?",
            "4% nominal total return before spending against assumed 2.5% inflation, about 1.46% real growth. A sustainable payout rate has not been supplied.",
        ),
        (
            "Why not choose the highest return?",
            "Higher later returns can involve more exposure than the conservative budget permits. Selecting on test returns would contaminate the held-out comparison.",
        ),
        (
            "Which data sources are used?",
            "Yahoo Finance through yfinance for the seven ETF adjusted closes and FRED DTB3 for risk-free diagnostics. No substitute vendor or extra portfolio asset is used.",
        ),
        (
            "What do adjusted closes solve?",
            "They incorporate vendor split/distribution adjustments, reducing artificial corporate-action jumps. They can still contain errors and retrospective revisions.",
        ),
        (
            "How are missing dates and outliers handled?",
            "Valid prices are intersected before returns. No price forward-fill or outlier deletion is used. Large, flat and volatility-break observations are flagged and retained.",
        ),
        (
            "Why log and simple returns?",
            "Logs support statistical checks and Gaussian modelling. Exact weighted simple returns drive portfolio wealth. Weighted logs are not substituted for wealth accounting.",
        ),
        (
            "How is future information excluded?",
            "Portfolio fitting ends in 2018. Each risk forecast uses the 756 strictly prior observations. Future-return perturbation tests check earlier forecasts remain unchanged within floating-point tolerance.",
        ),
        (
            "Is this a live track record?",
            "No. It is a retrospective chronological study, not a preregistered strategy or evidence that the allocation existed in 2008.",
        ),
        (
            "How is covariance stabilized?",
            "Construction uses 10% diagonal shrinkage; Monte Carlo uses 5%. These fixed choices improve conditioning but are not claimed to be optimal.",
        ),
        (
            "Why are three ETFs zero?",
            "The variance objective does not force every eligible asset into the portfolio. The team can consider geographic/factor constraints, but should not add them because of test-period performance.",
        ),
        (
            "Why is AGG not risk free?",
            "It has duration, credit and mortgage exposure. The 2022 replay demonstrates that a bond-heavy allocation can lose during inflation/rate shocks.",
        ),
        (
            "What costs are included?",
            "10bp per dollar of absolute daily rebalance turnover, paid before the next return. Initial purchases, taxes and impact are excluded. Net KPIs and gross risk/replay P&L are distinct.",
        ),
        (
            "How are Sharpe and Sortino defined?",
            "Annual excess return over lagged risk-free divided by annual volatility or downside deviation. Downside squared excess returns are averaged over all days for Sortino.",
        ),
        (
            "What does CAPM establish?",
            "A diagnostic relationship to SPY as market proxy. Jensen alpha is not proof of skill, and SPY is not a global market portfolio.",
        ),
        (
            "How do VaR and ES differ?",
            "VaR is the loss quantile. ES is q plus average excess above q divided by tail probability. Neither is a maximum possible loss.",
        ),
        (
            "Why do VaR methods disagree?",
            "Historical risk retains observed tails. Parametric risk assumes Gaussian portfolio log returns. MC assumes correlated Gaussian asset log returns with covariance shrinkage and nonlinear aggregation. Both Gaussian methods can miss heavy tails.",
        ),
        (
            "How many simulations?",
            f'50,000 for the current snapshot, 10,000 per rolling day, seed {s["seed"]}. Convergence and batch uncertainty concern simulation noise, not parameter uncertainty.',
        ),
        (
            "What does EVT add?",
            "POT extrapolates rare tail quantiles from threshold excesses. It also adds threshold and parameter uncertainty; it need not outperform historical simulation.",
        ),
        (
            "Why the 90% threshold?",
            f'The frozen rule retains about 76 excesses in 756 observations; latest actual count {s["evt_fit"]["exceedances"]}. Sensitivity covers 85–95%. The choice is justified, not declared uniquely optimal.',
        ),
        (
            "When is EVT unavailable?",
            "At/below its threshold, with fewer than 40 excesses or an invalid fit. Tail ES is unavailable for shape at least one. Unsupported values are not replaced with plausible numbers.",
        ),
        (
            "Does negative GPD shape imply a safe maximum loss?",
            f'No. Latest shape is {s["evt_fit"]["shape"]:.3f}, but its block interval spans zero and the market process can change. A fitted endpoint is not a loss guarantee.',
        ),
        (
            "What does backtesting show?",
            f"Historical VaR99 has {int(h.exceptions)} exceptions in {int(h.n)} days; Kupiec p={h.kupiec_p:.3f}, independence p={h.independence_p:.3f}. Non-rejection is not proof of correctness and tail-test power is limited.",
        ),
        (
            "When do Basel traffic lights apply?",
            "Exactly 250 one-day 99% forecasts: green 0–4, amber 5–9, red 10+. Full test is N/A; last-250 status is separate. This is a pedagogical legacy classification, not endowment regulation.",
        ),
        (
            "How should crisis replay be interpreted?",
            "As a hindsight exposure test using real daily prices, not a strategy operating at that time. Terminal return can understate interim drawdown. Recovery is nominal regained replay peak.",
        ),
        (
            "How are risk contributions verified?",
            "Historical ES derivatives include interpolated quantile terms. Components sum to ES and match finite differences. Gaussian simple-return VaR is explicitly a separate approximation.",
        ),
        (
            "Does the regime extension improve forecasts?",
            f'No clear improvement: paired mean FZ0 difference is {s["regime_comparison"]["mean_difference"]:+.3f}, with an interval spanning zero and worse conditional coverage. It remains research rather than the default.',
        ),
        (
            "Why use AI and what must the team approve?",
            "Codex materially assisted implementation, interpretation and drafting, with disclosure. No external LLM is needed in the app. The team must independently evaluate, revise and defend the allocation, risk interpretation, stress conclusions and final decision. Human validation is pending.",
        ),
    ]
    text = "# Judges and investment committee Q&A\n\nPreparation answers describe the executed reference design. Human team members must understand and independently validate them.\n\n"
    text += "\n\n".join(f"## {i}. {q}\n\n{a}" for i, (q, a) in enumerate(questions, 1))
    (ROOT / "documentation/Judges_QA.md").write_text(text, encoding="utf-8")
    print("Prepared", len(questions), "questions")


if __name__ == "__main__":
    main()
