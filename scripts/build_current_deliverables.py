"""Create the requested current technical report, one-page tear and AI-use PDF.

The 13-page locked study is preserved verbatim, with two current software pages.
"""
from pathlib import Path
from io import BytesIO
from datetime import datetime,timezone
from html import escape
import json
import sys
import pandas as pd
from pypdf import PdfReader,PdfWriter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.config import ROOT
from src.interactive import analyze,recommendation
from src.backtesting import summarize
from src.exports import provenance,make_report
from src.database import research_version


def software_document(kind):
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="BodyA",fontSize=9,leading=13,spaceAfter=9,textColor=colors.HexColor("#18383b")))
    styles.add(ParagraphStyle(name="HeadA",fontName="Times-Roman",fontSize=25,leading=28,spaceAfter=15,textColor=colors.HexColor("#123d3d")))
    styles.add(ParagraphStyle(name="SubA",fontName="Helvetica-Bold",fontSize=11,leading=15,spaceBefore=10,spaceAfter=6,textColor=colors.HexColor("#163f3b")))
    story=[]
    def p(t):story.append(Paragraph(escape(t),styles["BodyA"]))
    def h(t):story.append(Paragraph(escape(t),styles["SubA"]))
    def title(t):
        logo=Image(str(ROOT/"assets/quantumx_logo.png"),width=78,height=78)
        table=Table([[Paragraph(escape(t),styles["HeadA"]),logo]],colWidths=[386,89]);table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP")]));story.append(table);story.append(Spacer(1,10))
    def table(headers,rows,widths):
        cells=[[Paragraph(escape(str(x)),styles["BodyA"]) for x in row] for row in [headers]+rows]
        t=Table(cells,colWidths=widths,repeatRows=1);t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dbeee8")),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f0f5f4")]),("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),4)]));story.append(t)
    native_file=ROOT/"outputs/results/mobile_runtime_checks.json"
    runtime="Completed emulator checks are recorded in mobile_runtime_checks.json." if native_file.exists() else "Native build/runtime checks are pending in this draft; consult the final release validation record."
    if kind=="appendix":
        title("14 | Current website and native mobile delivery")
        p("Release context: 26 October 2026. The preceding 13 pages are the unchanged locked research study. Its ADJUST language corresponds to the current automated REVISE label; the software now also checks training net drawdown explicitly. No human investment approval is recorded.")
        h("One decision context across the website")
        p("A selected allocation consistently drives net performance, current risk, stress replays, policy checks, comparisons, the guide and selected exports. Fixed-reference frontier/reports are labelled. Custom rolling validation must be run for the selected weights and lookback; reference forecasts are reused only when weights and the original window match.")
        table(["Delivery","Implementation"],[
            ["Website", "Python/Streamlit; verified frozen inputs and real read-only SQLite research storage. Free Community Cloud; no paid APIs or payment details."],
            ["Identity and loading", "User-provided QuantumX AEGIS logo; actual data-verification loading state and a short, reduced-motion-aware welcome transition."],
            ["Website guide chat", "Typed, session-scoped deterministic conversation. Answers use selected results and link to the appropriate workspace. No external generative model or trade authority."],
            ["Native Android", "Independent Java/Android views and local numerical engine. No WebView or internet permission. Offline data, touch-inspection charts, local portfolio library, scenarios and guide."],
            ["Native research scope", "Historical and Gaussian-log VaR/ES at 90/95/99%; net performance; four stress events; rate/equity/gold what-if; selected rolling Historical99 validation. Website retains additional MC/EVT/state methods."]],[105,370])
        p("Delivery website: https://quantumx-aegis.streamlit.app/ | Full source, including mobile: https://github.com/CodeJediX/aegis-quantedge. The APK is directly installable and signed for local distribution; Play Store publication is not claimed.")
        story.append(PageBreak());title("15 | Verification, limits and responsibility")
        h("Reference result remains REVISE")
        table(["Failed original-limit check","Observed","Limit"],[["Training maximum net drawdown","16.71%","15.00%"],["Worst terminal scenario loss","15.23%","15.00%"],["Worst historical crisis drawdown","17.52%","15.00%"]],[275,100,100])
        p("The funding squeeze is approximately USD -1,522,670 on USD10m. A good historical coverage result does not override policy failures. Strict training-only optimization did not find a feasible allocation at the original limits; that is not a proof of global infeasibility. Edited research limits are not client-approved mandate amendments.")
        h("Executed numerical and software checks")
        p("The independently implemented native Java engine passed 222 comparisons with Python: performance ratios, historical/Gaussian risk at all confidence levels, stress returns/drawdowns, contributions and actual rolling Historical99 diagnostics. Maximum observed absolute difference was 3.06e-13. Zero-active-risk diagnostics remain unavailable rather than invented.")
        p("Website numerical/integration tests, typed-chat/evidence-navigation checks and all-route controls are recorded in the accompanying test results. The native app verifies bundled asset SHA256 values before showing results; it rejects invalid weights, preserves the original risk limits, and stores user allocations only in private device storage. "+runtime)
        h("Reproduction and practical limits")
        p("Website: pip install -r requirements.txt; streamlit run hosted_app.py. Research: python run.py --reproduce. Native: python scripts/check_mobile_engine.py, then python scripts/build_mobile.py with Java and the free Android API35 platform/build tools installed. Native PDF export uses Android's document picker. Preserve the external signing key for future APK updates; it is intentionally excluded from source archives.")
        p("The mobile dataset is frozen through 2026-09-30 and does not fetch live prices. No claim is made of native MC/EVT parity, universal device certification, or a pre-registered strategy. Backtests are retrospective, daily rebalancing can be impractical, and tax, liquidity, spending and implementation limitations remain material.")
        p("AI-assisted implementation and interpretation are disclosed separately. Automated agent checks are not independent human review. The team must understand, validate and defend the allocation, assumptions and final decision. Human approval remains PENDING.")
    else:
        title("AI usage details | QuantumX AEGIS")
        p("Disclosure date: 26 October 2026. This document identifies material AI assistance and separates executed automated checks from the independent human investment review that is still pending.")
        h("Tool and role")
        p("OpenAI Codex assisted this project in the development conversation. The host's exact underlying model identifier has not been independently verified. Ordinary execution tools included Python numerical libraries, ReportLab/pypdf/Poppler, Java and Android SDK build tools/emulator, Git/GitHub and browser automation.")
        table(["Component","Material AI assistance"],[
            ["Quantitative research", "Requirements interpretation; proposed constraints; portfolio/risk/EVT/backtest/stress implementation; numerical tests; interpretation and evidence-based draft recommendation."],
            ["Website", "Streamlit interface, responsive styling, selected-portfolio consistency, SQL integration, free hosting setup, logo integration, loading transition and local conversational guide."],
            ["Native Android", "Java calculation engine, native mobile views/charts, local saved profiles, offline what-if/backtesting, guide, signing/build scripts and automated reference/runtime checks."],
            ["Documents", "Technical report, investment tear sheet, committee memorandum, pitch materials, sources/governance records and this AI disclosure."],
            ["User contribution", "The logo was supplied by the user and preserved as provided. Requirements and requested changes came from the user. No completed independent human investment validation has been recorded."]],[105,370])
        h("AI is not running as the portfolio decision maker")
        p("The website and native app require no external LLM key or paid inference. Both guide chats use deterministic intent rules and actual selected context. They provide navigation and explanations, cannot place trades, and do not invent market facts or record human approval. The statistical risk models are not trained generative AI systems.")
        story.append(PageBreak());title("Validation, privacy and human responsibility")
        h("What was checked")
        p("The assistant executed independent mathematical references, chronological leakage/window checks, input validation, application interactions, document rendering and deployment checks where recorded in Testing_and_Validation.md. The separate native engine passed 222 comparisons against Python outputs, including real rolling validation. "+runtime)
        p("Failures were retained and repaired in code or test fixtures, not concealed by editing financial output. The original portfolio still receives REVISE because training/crisis/scenario losses breach proposed limits. Native and website numerical assessments never imply a completed human sign-off.")
        h("Chat handling and application scope")
        p("Website chat text is processed by the Streamlit hosting server and retained by the app only in the current session; it is not sent to an external generative AI provider. Native guide text and saved allocations remain on the device; the APK requests no internet permission. Hosting/provider metadata logging is outside a promise of app-level chat persistence.")
        p("The native app uses verified bundled data through 2026-09-30. It is an independent offline companion with explicitly limited model scope, not a live price terminal or a website wrapper. Public source contains no live credentials; private APK signing material is excluded.")
        h("Required independent human review - PENDING")
        p("Named team reviewers must inspect and substantiate the code, data provenance, financial formulas, portfolio constraints, uncertainty, stress conclusions, spending assumptions and final investment recommendation. They must be able to defend these conclusions themselves under the competition's AI-assistance rules. Agent-performed checks do not satisfy or substitute for that review.")
        table(["Review record","Status"],[["Independent reviewer name/date","Not recorded"],["Financial assumptions and findings approved","Pending"],["Final human investment decision","Pending"],["AI detector/plagiarism database clearance","Not performed or claimed"]],[300,175])
        p("Reference documentation: documentation/AI_Disclosure.md, Testing_and_Validation.md, Team_Approval_Checklist.md and Website_Improvements_Audit.md. Approved market inputs remain Yahoo adjusted ETF prices via yfinance and FRED DTB3. Primary SDK references: docs.streamlit.io and developer.android.com/tools.")
    def footer(c,doc):
        c.setFont("Helvetica",7);c.setFillColor(colors.HexColor("#536e74"));c.drawString(60,26,"QuantumX AEGIS | Historical research | Human approval pending");c.drawRightString(535,26,str(doc.page+13 if kind=="appendix" else doc.page))
    out=BytesIO();SimpleDocTemplate(out,pagesize=(595.28,841.89),leftMargin=60,rightMargin=60,topMargin=38,bottomMargin=48,title="AEGIS current software appendix" if kind=="appendix" else "AEGIS AI usage details",author="QuantumX; AI-assisted").build(story,onFirstPage=footer,onLaterPages=footer)
    assert len(PdfReader(BytesIO(out.getvalue())).pages)==2,"Unexpected appendix/disclosure pagination"
    return out.getvalue()


def main():
    prices=pd.read_csv(ROOT/"data/snapshots/adjusted_prices.csv",index_col=0,parse_dates=True);r=prices.pct_change(fill_method=None).dropna();rf=pd.read_csv(ROOT/"outputs/tables/risk_free.csv",index_col=0,parse_dates=True).iloc[:,0];alloc=pd.read_csv(ROOT/"outputs/tables/allocations.csv",index_col=0)
    a=analyze(r,rf,alloc.iloc[:,0].to_numpy(),"AEGIS minimum variance");forecasts=pd.read_csv(ROOT/"outputs/tables/forecasts.csv",parse_dates=["date"]);validation=summarize(forecasts[forecasts.date>=pd.Timestamp(a["test_start"])])
    decision=recommendation(a,validation);risk=pd.read_csv(ROOT/"outputs/tables/risk_snapshot.csv").query("confidence == .99");meta=provenance(a,research_version(),.99,"Historical")
    tear=ROOT/"reports/Current_Investment_Tear_Sheet.pdf";tear.write_bytes(make_report(a,risk,decision,meta,validation,"tear_sheet"))
    writer=PdfWriter();writer.append(str(ROOT/"reports/Technical_Report.pdf"));writer.append(BytesIO(software_document("appendix")));writer.add_metadata({"/Title":"QuantumX AEGIS - Current technical report","/Author":"QuantumX; AI-assisted research"})
    technical=ROOT/"reports/Current_Technical_Report.pdf";writer.write(technical)
    ai=ROOT/"reports/AI_Usage_Details.pdf";ai.write_bytes(software_document("ai"))
    pages={p.name:len(PdfReader(p).pages) for p in [technical,tear,ai]};assert pages[technical.name]==15 and pages[tear.name]==1 and pages[ai.name]==2
    (ROOT/"outputs/results/current_deliverables.json").write_text(json.dumps(dict(generated_utc=datetime.now(timezone.utc).isoformat(),pages=pages,allocation_id=a["allocation_id"],dataset_version=research_version(),recommendation=decision["status"],human_approval="PENDING",technical_structure="13 unchanged research pages plus 2 current software/validation pages"),indent=2)+"\n",encoding="utf-8")
    print(json.dumps(pages,indent=2))


if __name__=="__main__":main()
