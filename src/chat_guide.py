"""Local conversational website guide. No LLM, network calls or trade authority."""
import re
import streamlit as st
from .config import NAV, ROOT


def answer(question, result, decision, validation_available=False):
    text=re.sub(r"[^a-z0-9% ]"," ",question.lower())
    has=lambda *words:any(re.search(r"\b"+re.escape(word.strip())+r"\b",text) for word in words)
    context=f'{result["name"]} / {result["allocation_id"]} / data through {result["latest_end"]}'
    route="Executive Command Center"
    if has("revise","reject","approve","failed","policy","decision","breach"):
        failed=result["checks"].query("status == 'FAIL'")
        details="; ".join(f'{row.check}: {row.value:.2%}' for row in failed.itertuples())
        reply=f'The automated assessment is **{decision["status"]}** with **{len(failed)} failed policy checks**. '
        reply+=details+". " if details else "No numerical policy checks fail. "
        reply+=("Selected rolling validation is available; its result also enters the decision. " if validation_available else
                "Selected rolling validation has not been run, so an automated approval is unavailable. ")
        reply+="Human investment approval is separately pending. Inspect the limits and corrective actions before drawing a conclusion."
        route="Portfolio Decision Lab"
    elif has("save","download","export","report","pdf","library","reload","import"):
        reply="Use **Build a portfolio → My saved allocations** to name and reload a session allocation. Export the JSON library to retain it after the session ends, then import it later. In **Reports & downloads**, prepare selected reports for a technical PDF, tear sheet, memorandum and CSV/ZIP calculations. Fixed research files are labelled separately."
        route="Investment Committee Reports" if has("report","pdf","download","export") else "Portfolio Construction"
    elif has("weight","allocat","build","edit","holding","portfolio"):
        holdings=" · ".join(f'{t} {w:.2%}' for t,w in zip(["SPY","EFA","EEM","AGG","GLD","XLE","XLK"],result["weights"]) if w>1e-10)
        reply=f'Your selected allocation is **{result["name"]}**: {holdings}. Open **Build a portfolio**, enter all seven weights so they total 100%, then choose **Apply allocation to portfolio and risk views**. Comparisons, risk, stress and selected reports follow those weights. Run its own rolling validation when needed.'
        route="Portfolio Construction"
    elif has("backtest","validation","exception","kupiec","christoffersen","basel","traffic"):
        reply="Open **Model validation**. Full-window exception counts and the latest 250 observations are separate. Basel-style lights apply only to 250 one-day 99% forecasts: 0–4 Green, 5–9 Amber, 10+ Red. Custom weights/lookbacks need their own backtest; the reference is never substituted. A passing diagnostic does not establish investment safety."
        route="Backtesting & Validation"
    elif has("evt","tail","threshold","pareto","confidence interval"):
        reply="Open **Tail-risk lab** for selected-portfolio EVT estimates, reliability warnings, threshold sensitivity and block-resampled intervals. Requested confidence must exceed the fitting threshold. At least 40 exceedances are required; shape ≥1 makes finite ES unavailable. Intervals expose uncertainty and are not a guarantee."
        route="EVT & Tail-Risk Laboratory"
    elif has("stress","scenario","crisis","rate","rates","what if","whatif","shock","protect","protected","protection","capital guarantee"):
        reply="Open **Stress testing** to compare observed crisis replays with the assumed funding shock. **What-if assumptions** lets you change equity/gold returns, interest-rate basis points, assumed bond duration and volatility. Historical paths use hindsight weights; assumed shocks have no assigned probability. Neither bounds future loss."
        route="Crisis Simulation Studio"
    elif has("var","shortfall","risk","monte carlo","volatility","es ") or text.strip()=="es":
        reply=f'VaR is a one-day loss cutoff; ES averages loss beyond that tail cutoff. All dollar figures use **USD {NAV:,.0f}**. Your selected recent historical ES99 is **{result["ES99"]:.2%} / USD {result["ES99"]*NAV:,.0f}**. Open **Risk comparison** for matched methods and percent/USD displays. VaR is not a maximum loss.'
        route="Risk Analytics"
    elif has("source","data","live","update","timestamp","seed","method","reproduc") and not has("ai","chat","bot","llm"):
        reply=f'This is a fixed historical research dataset through **{result["latest_end"]}**, not a live price feed. Markets contains source/provenance and quality checks; Methods & disclosures explains processing, versions, seeds and AI use. Yahoo adjusted ETF prices and the lagged FRED rate proxy are the approved inputs.'
        route="Methodology, Sources & AI Disclosure"
    elif has("ai","chat","bot","human","privacy","llm"):
        reply="I am a **deterministic website guide**, not a live generative AI model. I route typed questions to verified explanations and selected calculations. No API key is required, and this chat is kept only in the current session. AI-assisted development is disclosed; no independent human investment approval is recorded."
        route="Methodology, Sources & AI Disclosure"
    else:
        reply="Start with **Overview** for the decision and failed checks, then **Build a portfolio → Risk comparison → Model validation → Stress testing → Reports & downloads**. You can ask me how to edit weights, explain VaR/ES, read the REVISE status, run validation or export a report. I answer navigation and research questions; I cannot execute trades or verify facts outside this app."
    return dict(text=reply,route=route,context=context)


def append_reply(query,result,decision,validation_available):
    if not query or not str(query).strip():
        return
    history=st.session_state.setdefault("website_chat_history",[])
    response=answer(str(query)[:600],result,decision,validation_available)
    history.extend([dict(role="user",text=str(query)[:600]),dict(role="assistant",**response)])
    st.session_state["website_chat_history"]=history[-12:]


def submit_typed(result,decision,validation_available):
    append_reply(st.session_state.get("website_chat_input"),result,decision,validation_available)


def submit_quick(result,decision,validation_available):
    append_reply(st.session_state.get("chat_quick"),result,decision,validation_available)


def clear_chat():
    st.session_state["website_chat_history"]=[]


def replay_welcome():
    st.session_state["_replay_welcome"]=True


def chat_widget(result,decision,validation_available):
    from .ui import open_workspace
    history=st.session_state.setdefault("website_chat_history",[])
    with st.container(key="website_guide_dock"):
        with st.popover("Ask AEGIS · website guide",icon=":material/chat:",use_container_width=True):
            st.markdown('<div class="guide-title"><span>AEGIS guide</span><small>LOCAL · EVIDENCE BASED</small></div>',unsafe_allow_html=True)
            st.caption("Ask in your own words. Deterministic guidance, not a live LLM or investment approval. Chat stays in this session.")
            with st.expander("Suggested questions",expanded=False):
                st.selectbox("Quick question",["Where do I start?","Why does it say REVISE?","Explain VaR and ES","How do I edit weights?","How do I save or export?"],key="chat_quick")
                st.button("Ask this question",key="chat_quick_send",on_click=submit_quick,args=(result,decision,validation_available))
            with st.container(height=280,key="website_chat_messages"):
                if not history:
                    with st.chat_message("assistant",avatar=str(ROOT/"assets/quantumx_logo.png")):
                        st.write("Hello. I can help you find tools and understand the selected portfolio's results. What would you like to do?")
                for item in history[-12:]:
                    with st.chat_message(item["role"],avatar=str(ROOT/"assets/quantumx_logo.png") if item["role"]=="assistant" else None):
                        st.write(item["text"])
                        if item["role"]=="assistant":
                            st.caption("Answer context: "+item["context"])
            st.chat_input("Ask AEGIS a question",max_chars=600,key="website_chat_input",on_submit=submit_typed,args=(result,decision,validation_available))
            bot=next((item for item in reversed(history) if item["role"]=="assistant"),None)
            if bot:
                st.button("Open the suggested workspace",key="chat_navigate",on_click=open_workspace,args=(bot["route"],),use_container_width=True)
            c=st.columns(2)
            c[0].button("Clear chat",key="chat_clear",on_click=clear_chat)
            c[1].button("Replay welcome",key="replay_welcome",on_click=replay_welcome)
