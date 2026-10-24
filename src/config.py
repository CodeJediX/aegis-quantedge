"""Locked research design. Test observations never select allocations or tuning."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TICKERS = ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]
START, END = "2005-01-01", "2026-10-01"
TRAIN_END, DEV_END, TEST_START = "2018-12-31", "2022-12-31", "2023-01-01"
NAV, SEED, WINDOW, N_SIM = 10_000_000, 20261024, 756, 50000
CONFIDENCES = [0.90, 0.95, 0.99]
EQUITY = [0, 1, 2, 5, 6]
BOUNDS = [
    (0, 0.25),
    (0, 0.20),
    (0, 0.15),
    (0.35, 0.70),
    (0.05, 0.20),
    (0, 0.10),
    (0, 0.20),
]
TC = 0.001  # 10 basis points per dollar traded, charged to L1 turnover.
PROPOSED_LIMITS = {
    "volatility": 0.10,
    "drawdown": 0.15,
    "daily_ES99": 0.025,
    "scenario_loss": 0.15,
}
SCENARIOS = {
    "2008 GFC": ("2008-01-01", "2009-03-31"),
    "2020 COVID": ("2020-02-19", "2020-03-31"),
    "2022 rates": ("2022-01-01", "2022-12-31"),
}
HYPOTHETICAL = dict(zip(TICKERS, [-0.25, -0.30, -0.35, -0.12, -0.10, -0.25, -0.35]))


def folders() -> None:
    for p in [
        "data/snapshots",
        "data/metadata",
        "outputs/tables",
        "outputs/figures",
        "outputs/results",
        "reports",
        "presentation",
        "documentation",
        "tests",
        "scripts",
        "assets",
        ".streamlit",
    ]:
        (ROOT / p).mkdir(parents=True, exist_ok=True)
