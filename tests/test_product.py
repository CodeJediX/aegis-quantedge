"""Cross-workspace policy persistence and safe reference restoration."""

import unittest
from dataclasses import asdict
from src.interactive import Limits
from src.product import policy_parameters, remember_policy, restore_policy, restore_reference


class ProductStateTests(unittest.TestCase):
    def test_limits_survive_widget_cleanup(self):
        state={"limit_dd":20.0,"limit_scenario":18.0}
        remember_policy(state,"limit_dd")
        remember_policy(state,"limit_scenario")
        del state["limit_dd"]
        del state["limit_scenario"]
        self.assertEqual(policy_parameters(state).drawdown,.20)
        self.assertEqual(policy_parameters(state).scenario_loss,.18)
        self.assertEqual(policy_parameters(state).daily_ES99,.025)

    def test_original_limits_are_restored(self):
        state={"_policy_settings":{"limit_dd":30.0},"limit_bond":.65}
        restore_policy(state)
        self.assertEqual(asdict(policy_parameters(state)),asdict(Limits()))

    def test_invalid_durable_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            policy_parameters({"_policy_settings":{"limit_equity":.80}})

    def test_reference_restore_retains_saved_profiles(self):
        library={"My research":[.2,0,0,.6,.2,0,0]}
        state={"portfolio_library":library,"portfolio":"Custom allocation","confidence":.90,
               "lookback":252,"method":"EVT","_reference_dates":("start","end"),"dates":("changed",),
               "_policy_settings":{"limit_dd":20.0},"_editor_signature":"custom"}
        restore_reference(state)
        self.assertEqual(state["portfolio"],"AEGIS minimum variance")
        self.assertEqual((state["confidence"],state["method"],state["lookback"]),(.99,"Historical",756))
        self.assertNotIn("dates",state)
        self.assertIs(state["portfolio_library"],library)
        self.assertNotIn("_editor_signature",state)
        self.assertEqual(policy_parameters(state),Limits())
