"""Shared presentation components and optional authorized team-database controls."""

import hmac
import json
import os
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from .config import TICKERS
from .database import active_store, research_version, release_table
from .portfolio import validate_weights
from .risk import risk_table, filtered_forecast
from .evt import fit, estimate

COLORS=["#55CCB0","#D8B76E","#91B8D3","#CE846B","#B4A4CE","#6EABB4","#B5C6A2"]
px.defaults.color_discrete_sequence=COLORS


def open_workspace(page):
    st.session_state["page"]=page


def read(name):
    return release_table(name)


def pct(value):
    return "N/A" if value is None or not np.isfinite(float(value)) else f"{value:.2%}"


def chart(fig):
    title=fig.layout.title.text or ""
    title="<br>".join(textwrap.wrap(title,35))
    fig.update_layout(template="plotly_dark",paper_bgcolor="#0E1C21",plot_bgcolor="#0E1C21",
        font=dict(family="Segoe UI",color="#DCE9EF",size=12),
        title=dict(text=title,font=dict(family="Georgia",size=20,color="#EDF3F1"),x=.02),
        colorway=COLORS,margin=dict(l=18,r=24,t=77 if "<br>" in title else 58,b=35),
        legend=dict(orientation="h",y=-.22),height=395,
        hoverlabel=dict(bgcolor="#162A30",font_color="#EDF3F1"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#243B42",zerolinecolor="#3A565E")
    if fig.layout.yaxis.tickformat:
        fig.update_yaxes(hoverformat=fig.layout.yaxis.tickformat)
    st.plotly_chart(fig,use_container_width=True,config={"displaylogo":False,"toImageButtonOptions":{"scale":2}})


def lede(text):
    st.markdown(f'<div class="lede">{text}</div>',unsafe_allow_html=True)


def table(frame):
    configs={}
    for column in frame.select_dtypes(include=["number"]).columns:
        if pd.api.types.is_integer_dtype(frame[column]):
            configs[column]=st.column_config.NumberColumn(str(column),format="%d")
        else:
            configs[column]=st.column_config.NumberColumn(str(column),format="%.5g")
    st.dataframe(frame,width="stretch",hide_index=True,column_config=configs)


@st.cache_data(show_spinner=False,max_entries=60)
def current_risk(r,weights,alpha):
    w=np.array(weights)
    out=risk_table(r,w,[alpha])
    past=r.to_numpy()@w
    try:
        model=fit(-past)
        evt=dict(model="EVT",confidence=alpha,**estimate(model,alpha))
        out=pd.concat([out,pd.DataFrame([evt])],ignore_index=True)
    except ValueError:
        # Callers expose the unavailable fit rather than fabricating a substitute.
        pass
    state=dict(model="Volatility state",confidence=alpha,**filtered_forecast(past,alpha))
    return pd.concat([out,pd.DataFrame([state])],ignore_index=True)


def saved_allocations_panel(weights):
    store=active_store()
    if store is None:
        return
    with st.expander("Saved research allocations"):
        if os.environ.get("AEGIS_READONLY_DATABASE")=="1":
            st.info("Shared database saving is unavailable on this deployment. Use My saved allocations to name, reload and export your session library.")
            return
        st.caption("These optional shared research records are protected by the configured team administrator key. They never replace the fixed reference.")
        version=research_version()
        records=store.list_allocations(version)
        if records:
            lookup={row["id"]:row for row in records}
            selected=st.selectbox("Saved team allocation",list(lookup),format_func=lambda key:lookup[key]["name"]+" · "+lookup[key]["created_at"][:10],key="saved_allocation")
            if st.button("Load team allocation",key="load_saved"):
                values=json.loads(lookup[selected]["weights_json"])
                st.session_state["custom"]=validate_weights(np.array([values[t] for t in TICKERS])).tolist()
                st.session_state["custom_label"]=lookup[selected]["name"]
                st.session_state["_use_custom"]=True
                st.rerun()
        else:
            st.info("No team allocations have been saved for this research release.")
        admin_key=os.environ.get("AEGIS_ADMIN_KEY","")
        if admin_key:
            with st.form("persist_allocation"):
                label=st.text_input("Allocation name",max_chars=80,key="saved_name")
                token=st.text_input("Team administrator key",type="password",key="saved_admin_key")
                submitted=st.form_submit_button("Save current allocation to database")
            if submitted:
                if not hmac.compare_digest(token.encode(),admin_key.encode()):
                    st.error("The administrator key is not valid.")
                else:
                    identity=store.save_allocation(version,label,weights)
                    st.success("Team allocation saved. Record "+identity[:8]+".")
        else:
            st.caption("Team saving is disabled until an administrator key is configured.")


def render(*args):
    from .workspaces import render as render_selected
    return render_selected(*args)
