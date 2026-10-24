"""Authentic snapshot and generated-output invariants; never access the network."""

import unittest
import json
import numpy as np
import pandas as pd
from src.config import ROOT, TICKERS
from src.portfolio import metrics


class IntegrationTests(unittest.TestCase):
    def test_metric_reference(self):
        p = pd.Series([0.01, -0.005, 0.02, -0.01] * 70)
        rf = pd.Series(np.zeros(len(p)))
        k = metrics(p, p, p, rf)
        self.assertAlmostEqual(k["beta"], 1)
        self.assertAlmostEqual(k["Jensen_alpha"], 0)
        self.assertAlmostEqual(k["Sharpe"], p.mean() / p.std(ddof=1) * np.sqrt(252))
        self.assertIsNone(k["information_ratio"])

    def test_universe_and_coverage(self):
        p = pd.read_csv(
            ROOT / "data/snapshots/adjusted_prices.csv", index_col=0, parse_dates=True
        )
        self.assertEqual(list(p.columns), TICKERS)
        self.assertFalse(p.isna().any().any())
        self.assertTrue((p > 0).all().all())
        self.assertLessEqual(p.index[0], pd.Timestamp("2005-01-04"))
        self.assertEqual(p.index[-1], pd.Timestamp("2026-09-30"))

    def test_forecast_dates(self):
        f = pd.read_csv(
            ROOT / "outputs/tables/forecasts.csv",
            parse_dates=["date", "estimate_end", "estimate_start"],
        )
        self.assertTrue((f.estimate_start < f.estimate_end).all())
        self.assertTrue((f.estimate_end < f.date).all())
        self.assertFalse(((f.model == "EVT") & (f.confidence == 0.90)).any())
        self.assertTrue(np.isfinite(f.VaR).all())

    def test_stress_contributions_and_coverage(self):
        f = pd.read_csv(ROOT / "outputs/tables/stress.csv")
        self.assertEqual(
            set(f.scenario),
            {"2008 GFC", "2020 COVID", "2022 rates", "Hypothetical funding squeeze"},
        )
        np.testing.assert_allclose(f[TICKERS].sum(axis=1), f.return_pct, atol=1e-10)
        np.testing.assert_allclose(f.USD, 1e7 * f.return_pct, atol=0.001)
        self.assertTrue((f.max_drawdown >= 0).all())

    def test_policy_and_gross_net_signs(self):
        s = json.loads((ROOT / "outputs/results/summary.json").read_text())
        self.assertIn("pending", s["proposal_status"])
        self.assertAlmostEqual(sum(s["weights"].values()), 1)
        risk = pd.read_csv(ROOT / "outputs/tables/risk_snapshot.csv")
        self.assertTrue((risk.ES >= risk.VaR - 1e-12).all())
        self.assertTrue((risk.VaR > 0).all())
        for _, g in risk.groupby("model"):
            self.assertTrue(np.all(np.diff(g.sort_values("confidence").VaR) > 0))


if __name__ == "__main__":
    unittest.main()
