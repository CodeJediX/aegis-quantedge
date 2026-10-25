"""User-supplied identity and honest loading states, with no artificial waits."""
import base64
from functools import lru_cache
import streamlit as st
from .config import ROOT


@lru_cache(maxsize=1)
def logo_uri():
    return "data:image/png;base64," + base64.b64encode((ROOT/"assets/quantumx_logo.png").read_bytes()).decode()


def logo_html(class_name="brand-logo"):
    return f'<img class="{class_name}" src="{logo_uri()}" alt="QuantumX AEGIS logo"/>'


def loading_screen():
    slot=st.empty()
    slot.markdown('<div class="aegis-loader" role="status" aria-live="polite">'
        '<div class="loader-orbit"><div class="loader-logo">'+logo_html()+
        '</div></div><p class="loader-kicker">QUANTUMX / AEGIS</p>'
        '<h2>Preparing your research workspace</h2>'
        '<p>Checking the historical dataset and opening your analytics.</p>'
        '<div class="loader-track"><span></span></div></div>',unsafe_allow_html=True)
    return slot


def welcome_screen():
    slot=st.empty()
    if st.session_state.pop("_replay_welcome",False) or not st.session_state.get("_welcome_shown"):
        st.session_state["_welcome_shown"]=True
        slot.markdown('<div class="aegis-welcome" aria-hidden="true"><div class="welcome-inner">'
            '<div class="welcome-logo">'+logo_html()+'</div><span class="loader-kicker">QUANTUMX / AEGIS</span>'
            '<h2>Clarity before conviction.</h2><p>Your portfolio research workspace is ready.</p>'
            '<div class="welcome-rule"></div></div></div>',unsafe_allow_html=True)
