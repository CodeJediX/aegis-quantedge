"""Offline Streamlit navigation and control integration checks (no network)."""

import json
import sys
from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PAGES = [
    "Executive Command Center",
    "Market Intelligence",
    "Portfolio Construction",
    "Risk Analytics",
    "EVT & Tail-Risk Laboratory",
    "Backtesting & Validation",
    "Crisis Simulation Studio",
    "Portfolio Decision Lab",
    "AI Research Assistant",
    "Investment Committee Reports",
    "Assumptions & Limitations",
    "Methodology, Sources & AI Disclosure",
]


def main(entrypoint="app.py"):
    outcomes = []
    app = AppTest.from_file(str(ROOT / entrypoint), default_timeout=60).run()

    def check(label):
        errors = [e.message for e in app.exception]
        outcomes.append(dict(check=label, passed=not errors, exceptions=errors))
        assert not errors, (label, errors)

    check("startup")
    next(button for button in app.button if button.label == "Compare downside risk →").click().run()
    assert app.selectbox(key="page").value == "Risk Analytics"
    check("overview navigation action")
    for page in PAGES:
        app.selectbox(key="page").set_value(page).run()
        check("page: " + page)
    app.selectbox(key="page").set_value("Risk Analytics").run()
    for a in [0.90, 0.95, 0.99]:
        app.selectbox(key="confidence").set_value(a).run()
        check("confidence " + str(a))
    for lookback in [252, 504, 756, 1260]:
        app.selectbox(key="lookback").set_value(lookback).run()
        check("lookback " + str(lookback))
    app.selectbox(key="portfolio").set_value("60/40 benchmark").run()
    check("alternative portfolio")
    app.selectbox(key="method").set_value("EVT").run()
    check("EVT selector")
    app.selectbox(key="confidence").set_value(0.90).run()
    check("unsupported EVT90 handled")
    app.selectbox(key="page").set_value("EVT & Tail-Risk Laboratory").run()
    app.slider(key="threshold").set_value(0.95).run()
    check("threshold .95")
    app.selectbox(key="page").set_value("Portfolio Construction").run()
    app.number_input(key="weight_SPY").set_value(99.0).run()
    app.button[0].click().run()
    check("malformed weight sum handled")
    assert len(app.error) > 0, "Malformed allocation should show an actionable error"
    for ticker in ["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"]:
        app.number_input(key="weight_" + ticker).set_value(50.0 if ticker in ["SPY", "AGG"] else 0.0)
    app.button[0].click().run()
    assert app.selectbox(key="portfolio").value == "Custom allocation"
    assert app.session_state["custom"] == [0.5, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0]
    check("valid allocation automatically applies")
    app.selectbox(key="page").set_value("Backtesting & Validation").run()
    app.selectbox(key="confidence").set_value(0.99).run()
    import datetime

    app.date_input(key="dates").set_value(
        (datetime.date(2025, 1, 2), datetime.date(2025, 12, 31))
    ).run()
    check("backtest date control")
    (ROOT / "outputs/results/app_checks.json").write_text(
        json.dumps(outcomes, indent=2)
    )
    print(f"{len(outcomes)} app checks passed")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "app.py")
