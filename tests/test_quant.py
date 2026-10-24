import unittest
import numpy as np
import pandas as pd
from scipy.stats import norm
from src.risk import empirical, normal_log, contributions, mc_losses
from src.evt import fit, estimate
from src.portfolio import validate_weights, solve, path
from src.backtesting import coverage, traffic, forecasts


class QuantTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(8)
        self.r = pd.DataFrame(
            self.rng.normal(0.0002, 0.01, (850, 7)),
            columns=["SPY", "EFA", "EEM", "AGG", "GLD", "XLE", "XLK"],
            index=pd.bdate_range("2015-01-01", periods=850),
        )
        self.w = np.array([0.1, 0.05, 0.05, 0.6, 0.15, 0.02, 0.03])

    def test_empirical_reference(self):
        v = empirical(np.arange(100.0), 0.975)
        self.assertAlmostEqual(v["VaR"], 96.525)
        self.assertAlmostEqual(v["ES"], 98.295)
        self.assertGreater(empirical(np.arange(100.0), 0.99)["VaR"], v["VaR"])

    def test_normal_log_analytical(self):
        q = norm.ppf((np.arange(200000) + 0.5) / 200000) * 0.01 + 0.0001
        r = np.expm1(q)
        calc = normal_log(r, 0.99)
        self.assertAlmostEqual(
            calc["VaR"], 1 - np.exp(0.0001 + 0.01 * norm.ppf(0.01)), places=6
        )
        self.assertAlmostEqual(calc["ES"], empirical(-r, 0.99)["ES"], places=6)

    def test_evt_exponential_reference(self):
        m = dict(shape=0, scale=0.01, threshold=0.02, p_exceed=0.1)
        v = estimate(m, 0.99)
        self.assertAlmostEqual(v["VaR"], 0.02 + 0.01 * np.log(10))
        self.assertAlmostEqual(v["ES"], v["VaR"] + 0.01)
        with self.assertRaises(ValueError):
            estimate(m, 0.90)

    def test_evt_fit_and_failure(self):
        x = self.rng.exponential(0.01, 4000)
        m = fit(x)
        self.assertTrue(abs(m["shape"]) < 0.2)
        with self.assertRaises(ValueError):
            fit(np.ones(80))
        bad = dict(shape=1.1, scale=0.01, threshold=0.02, p_exceed=0.1)
        self.assertIsNone(estimate(bad, 0.99)["ES"])

    def test_kupiec_reference(self):
        h = np.r_[np.ones(5), np.zeros(245)]
        b = coverage(h, 0.99)
        expected = 2 * (5 * np.log(0.02 / 0.01) + 245 * np.log(0.98 / 0.99))
        self.assertAlmostEqual(b["kupiec_LR"], expected)
        self.assertEqual(traffic(h, 0.99), "Amber")
        self.assertTrue(traffic(h, 0.95).startswith("N/A"))
        self.assertIsNone(coverage(np.zeros(250), 0.99)["independence_p"])

    def test_christoffersen_transition_reference(self):
        h = np.array([0, 0, 1, 1, 0, 0, 0, 1, 0, 0])
        b = coverage(h, 0.95)
        self.assertEqual([b["n00"], b["n01"], b["n10"], b["n11"]], [4, 2, 2, 1])
        self.assertAlmostEqual(b["independence_LR"], 0)

    def test_constraints_and_malformed_weights(self):
        w = solve(self.r)
        self.assertAlmostEqual(w.sum(), 1)
        self.assertTrue(0.35 - 1e-8 <= w[3] <= 0.7 + 1e-8)
        self.assertTrue(0.2 - 1e-8 <= w[[0, 1, 2, 5, 6]].sum() <= 0.5 + 1e-8)
        for x in [np.zeros(7), np.ones(6) / 6, np.array([np.nan] * 7)]:
            with self.assertRaises(ValueError):
                validate_weights(x)

    def test_risk_contribution_euler(self):
        c = contributions(self.r.iloc[:751], self.w, 0.99)
        self.assertAlmostEqual(
            c.component_ES.sum(),
            empirical(-(self.r.iloc[:751].to_numpy() @ self.w), 0.99)["ES"],
            places=12,
        )
        e = 0.000001
        w2 = self.w.copy()
        w2[0] += e
        fd = (
            empirical(-(self.r.iloc[:751].to_numpy() @ w2), 0.99)["ES"]
            - empirical(-(self.r.iloc[:751].to_numpy() @ self.w), 0.99)["ES"]
        ) / e
        self.assertAlmostEqual(fd, c.marginal_ES.iloc[0], places=6)

    def test_portfolio_wealth_and_cost(self):
        p = path(self.r, self.w)
        gross = self.r.to_numpy() @ self.w
        np.testing.assert_allclose(p.gross, gross)
        self.assertTrue((p.net <= p.gross + 1e-12).all())
        np.testing.assert_allclose(p.wealth, np.cumprod(1 + p.net))
        self.assertTrue((p.drawdown <= 0).all())

    def test_no_future_leakage(self):
        small = self.r.iloc[:765]
        before = forecasts(small, self.w, start="2000", window=756, n_mc=1000)
        changed = small.copy()
        changed.iloc[-1] = 0.5
        after = forecasts(changed, self.w, start="2000", window=756, n_mc=1000)
        np.testing.assert_allclose(before.VaR, after.VaR, atol=1e-14, rtol=0)
        self.assertTrue((before.estimate_end < before.date).all())

    def test_mc_seed(self):
        a = mc_losses(np.log1p(self.r), self.w, n=2000)
        b = mc_losses(np.log1p(self.r), self.w, n=2000)
        np.testing.assert_array_equal(a, b)
        self.assertTrue(np.isfinite(a).all())

    def test_malformed_distribution_inputs(self):
        for x in [np.array([]), np.array([np.nan] * 100), np.array([-1.2] * 100)]:
            with self.assertRaises(ValueError):
                normal_log(x, 0.99)
        with self.assertRaises(ValueError):
            empirical(np.ones(30), 1.1)
        with self.assertRaises(ValueError):
            path(self.r.iloc[:0], self.w)
        with self.assertRaises(ValueError):
            mc_losses(np.ones((30, 3)), self.w)


if __name__ == "__main__":
    unittest.main()
