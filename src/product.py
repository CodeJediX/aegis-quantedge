"""Product-level analysis state; independent of transient Streamlit widgets."""

from .interactive import Limits


POLICY_CONTROLS = {
    "limit_vol": ("volatility", 10.0, 100.0),
    "limit_dd": ("drawdown", 15.0, 100.0),
    "limit_es": ("daily_ES99", 2.5, 100.0),
    "limit_scenario": ("scenario_loss", 15.0, 100.0),
    "limit_return": ("objective", 4.0, 100.0),
    "limit_bond": ("bond_min", 0.35, 1.0),
    "limit_equity": ("equity_cap", 0.50, 1.0),
}


def policy_parameters(state):
    """Keep edited limits when a workspace's widget keys are cleaned up."""
    saved = state.get("_policy_settings", {})
    values = {
        field: state.get(key, saved.get(key, default)) / scale
        for key, (field, default, scale) in POLICY_CONTROLS.items()
    }
    return Limits(**values)


def remember_policy(state, key):
    values = dict(state.get("_policy_settings", {}))
    values[key] = state[key]
    state["_policy_settings"] = values


def restore_policy(state):
    values = {key: default for key, (_, default, _) in POLICY_CONTROLS.items()}
    state["_policy_settings"] = values
    for key, value in values.items():
        state[key] = value


def restore_reference(state):
    """Restore the reference context without deleting saved research profiles."""
    restore_policy(state)
    state["portfolio"] = "AEGIS minimum variance"
    state["confidence"] = 0.99
    state["method"] = "Historical"
    state["lookback"] = 756
    state.pop("dates",None)
    state.pop("_editor_signature", None)
