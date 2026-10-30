"""Regression checks for cleared percentage fields in the real Streamlit form."""

import os
import unittest
from unittest.mock import patch

import numpy as np
from streamlit.testing.v1 import AppTest

from src.config import ROOT, TICKERS


SUBMIT = "FormSubmitter:allocation_form-Apply allocation to portfolio and risk views"


class AllocationFormTests(unittest.TestCase):
    def setUp(self):
        deployment_environment = patch.dict(os.environ)
        deployment_environment.start()
        self.addCleanup(deployment_environment.stop)
        self.app = AppTest.from_file(str(ROOT / "hosted_app.py"), default_timeout=120).run()
        self.app.selectbox(key="page").set_value("Portfolio Construction").run()
        self.assertFalse(self.app.exception)

    def test_blank_fields_preserve_selected_portfolio_and_allow_correction(self):
        app = self.app
        selected = app.selectbox(key="portfolio").value
        original = [app.number_input(key="weight_" + t).value for t in TICKERS]
        for missing in [(t,) for t in TICKERS] + [tuple(TICKERS)]:
            with self.subTest(missing=missing):
                for ticker, value in zip(TICKERS, original):
                    app.number_input(key="weight_" + ticker).set_value(None if ticker in missing else value)
                app.button(key=SUBMIT).click().run()
                self.assertFalse(app.exception, [e.message for e in app.exception])
                self.assertTrue(any("Enter a weight for every ETF" in e.value for e in app.error))
                self.assertEqual(app.selectbox(key="portfolio").value, selected)
                self.assertNotIn("custom", app.session_state.filtered_state)
        for ticker, value in zip(TICKERS, original):
            app.number_input(key="weight_" + ticker).set_value(value)
        app.button(key=SUBMIT).click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        np.testing.assert_allclose(app.session_state["custom"], np.array(original) / 100)

    def test_zero_weights_and_navigation_remain_valid(self):
        app = self.app
        weights = [20.0, 0.0, 0.0, 60.0, 20.0, 0.0, 0.0]
        for ticker, value in zip(TICKERS, weights):
            app.number_input(key="weight_" + ticker).set_value(value)
        app.button(key=SUBMIT).click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertEqual(app.selectbox(key="portfolio").value, "Custom allocation")
        np.testing.assert_allclose(app.session_state["custom"], np.array(weights) / 100)
        app.selectbox(key="page").set_value("Risk Analytics").run()
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox(key="portfolio").value, "Custom allocation")
        np.testing.assert_allclose(app.session_state["custom"], np.array(weights) / 100)
        app.selectbox(key="page").set_value("Portfolio Construction").run()
        self.assertEqual(app.selectbox(key="portfolio").value, "Custom allocation")
        self.assertEqual([app.number_input(key="weight_" + t).value for t in TICKERS], weights)
        app.button(key=SUBMIT).click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        np.testing.assert_allclose(app.session_state["custom"], np.array(weights) / 100)


if __name__ == "__main__":
    unittest.main()
