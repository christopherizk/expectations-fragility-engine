"""Expectations Fragility Lab | compact institutional research terminal.

The overview contains fixed, aggregated research snapshots; the interactive
research workspace and earlier experiments remain accessible separately.
"""
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="EFL | Expectations Fragility Lab", page_icon="E", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
/* EFL 1.3 | institutional editorial system */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Libre+Baskerville:wght@400;700&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#080c13!important;color:#eaf0f7!important}
[data-testid="stSidebar"]{background:#0d1520!important;border-right:1px solid #28364a!important}
[data-testid="stMainBlockContainer"]{max-width:1370px!important;padding-top:2.2rem!important;padding-bottom:4rem!important}
html,body,[class*="st-"]{font-family:'DM Sans',sans-serif!important}
h1,h2,h3{letter-spacing:-.045em!important}h1{font-size:clamp(2.1rem,3.3vw,3.2rem)!important;font-weight:600!important;line-height:1.14!important}h2{font-size:1.45rem!important}
[data-testid="stMetric"]{background:transparent!important;border:0!important;border-top:1px solid #31435a!important;border-radius:0!important;padding:16px 8px 6px!important}
[data-testid="stMetricLabel"]{color:#94a9c0!important;font-size:.84rem!important}
[data-testid="stMetricValue"]{font-family:'DM Sans',sans-serif!important;color:#f0f5fa!important;font-size:2rem!important;font-weight:500!important;letter-spacing:-.055em!important}
[data-testid="stDataFrame"],[data-testid="stExpander"],[data-testid="stFileUploader"]{border-color:#30435a!important;border-radius:3px!important}
[data-testid="stSelectbox"]>div>div{background:#111d2b!important;border:1px solid #344963!important;border-radius:3px!important}
[data-testid="stRadio"] label{font-size:.91rem!important}
.stButton>button{border-radius:3px!important;background:#152c42!important;border:1px solid #466b8e!important;color:#eaf2fb!important}
.efl-kicker,.efl-sect{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.18em;color:#94b4d1;margin:16px 0 12px}
.efl-hero{border-top:1px solid #56728f;border-bottom:1px solid #2c3e52;padding:24px 0;margin:12px 0 28px}
.efl-hero h1{font-family:'Libre Baskerville',Georgia,serif!important;font-weight:400!important;font-size:clamp(2rem,3.1vw,3.2rem)!important;max-width:850px;line-height:1.26!important}
.efl-deck{font-size:1rem;line-height:1.65;color:#a7b8c9;max-width:820px}
.efl-panel{background:#101b29;border:1px solid #293b50;border-left:2px solid #89aaca;padding:20px 24px;margin:18px 0}
.efl-panel .eyebrow{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.15em;color:#9cb9d4}
.efl-panel .big{font-size:1.35rem;line-height:1.35;font-weight:600;margin:8px 0}
.efl-panel .small{color:#a9b9cb;font-size:.92rem;line-height:1.55}
.efl-tiny{font:400 11px 'IBM Plex Mono',monospace;color:#8297ad;letter-spacing:.06em}
.efl-brand{font-family:Georgia,serif;letter-spacing:.16em;color:#edf3f9;font-size:1.45rem}
.efl-brand span{color:#8daecb}
.efl-profile{border-top:1px solid #5d7e9e;border-bottom:1px solid #2c3d50;padding:24px 0 21px;margin:8px 0 18px}
.efl-profile .tag{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.18em;color:#92b1d0;margin-bottom:12px}
.efl-profile .name{font:400 clamp(2rem,3vw,3.1rem) 'Libre Baskerville',Georgia,serif;color:#edf3fa;line-height:1.24;letter-spacing:-.04em}
.efl-profile .desc{color:#a6b7c9;font-size:.95rem;line-height:1.55;margin-top:12px;max-width:850px}
.efl-insight{border-left:2px solid #8faecc;background:#101b29;padding:15px 19px;margin:12px 0 20px;color:#c3d1df;font-size:.95rem;line-height:1.6}
.efl-insight strong{color:#f2f6fa}
.efl-note{color:#90a3b8;font-size:.81rem;line-height:1.6}
.efl-rule{border:0;border-top:1px solid #2c3d50;margin:15px 0 25px}
/* keep Streamlit upload and disclosure labels readable */
[data-testid="stExpander"] summary{min-height:44px!important;padding:12px 15px!important}
[data-testid="stExpander"] summary p{white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.5!important}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="efl-brand">E<span>|</span>F<span>|</span>L</div>',unsafe_allow_html=True)
    st.caption("EXPECTATIONS FRAGILITY LAB")
    st.divider()
    page=st.radio("RESEARCH TERMINAL",["Overview","Company explorer","Model validation","Methodology","Advanced workbench"],label_visibility="visible")
    st.divider()
    st.caption("INDEPENDENT EQUITY RESEARCH")
    st.caption("US equities · 5 companies · Fixed research snapshot")
    st.caption("Exploratory analysis · Not investment advice")


# Aggregated per-company figures computed from the existing 196-event v0.8 research export.
# No event-level provider data is distributed with this app.
COMPANY_SNAPSHOT = {'AAPL': {'beat_events': 37,
          'beat_negative_rate': float(37.8),
          'events': 39,
          'mean_return': float(1.21),
          'median_return': float(1.95),
          'negative_rate': float(38.5)},
 'AMZN': {'beat_events': 29,
          'beat_negative_rate': float(41.4),
          'events': 39,
          'mean_return': float(0.66),
          'median_return': float(-0.1),
          'negative_rate': float(51.3)},
 'MSFT': {'beat_events': 36,
          'beat_negative_rate': float(41.7),
          'events': 39,
          'mean_return': float(0.79),
          'median_return': float(1.06),
          'negative_rate': float(43.6)},
 'NVDA': {'beat_events': 35,
          'beat_negative_rate': float(45.7),
          'events': 39,
          'mean_return': float(1.15),
          'median_return': float(0.75),
          'negative_rate': float(48.7)},
 'TSLA': {'beat_events': 22,
          'beat_negative_rate': float(54.5),
          'events': 40,
          'mean_return': float(-0.77),
          'median_return': float(-2.12),
          'negative_rate': float(57.5)}}

if page=="Overview":
    st.markdown('<div class="efl-kicker">RESEARCH NOTE 001  /  OCTOBER 2026</div>',unsafe_allow_html=True)
    st.markdown('<div class="efl-hero"><h1>When earnings beats fail to impress the market.</h1><div class="efl-deck">An independent study of earnings surprises, market-adjusted returns and whether pre-event market conditions help explain negative reactions.</div></div>',unsafe_allow_html=True)
    a,b,c=st.columns([1,1,1])
    a.metric("Matched earnings events","198")
    b.metric("EPS beats with negative returns","42.9%")
    c.metric("Companies studied","5")
    st.markdown('<div class="efl-panel"><div class="eyebrow">THE CENTRAL FINDING</div><div class="big">A positive EPS surprise does not guarantee a positive market reaction.</div><div class="small">69 of 161 positive EPS surprises in the historical event-study sample coincided with negative SPY-adjusted event-window returns. This is an association, not an explanation of why prices fell.</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.15,1],gap="large")
    with left:
        st.markdown('<div class="efl-sect">01 / WHAT WE TESTED</div>',unsafe_allow_html=True)
        st.write("We tested whether a provisional pre-earnings fragility score—combining 20-session momentum and 60-session downside volatility—identified more frequent negative earnings-window returns.")
        st.markdown('<div class="efl-sect">02 / THE RESULT</div>',unsafe_allow_html=True)
        st.write("**It did not.** In the later chronological holdout, higher-scoring events had fewer negative reactions than lower-scoring events. The initial score is not a validated predictor.")
    with right:
        st.markdown('<div class="efl-sect">HOLDOUT / NEGATIVE REACTION RATE</div>',unsafe_allow_html=True)
        rates=pd.DataFrame({"Group":["Higher score","Lower score"],"Negative reactions (%)":[50.0,59.46]}).set_index("Group")
        st.bar_chart(rates,horizontal=True,color="#81A8D1")
        st.caption("59 later-period events · 22 higher-score, 37 lower-score")
    st.markdown('<div class="efl-tiny">SNAPSHOT: 198 event-study observations; 196 usable pre-event observations. Earnings timing and event windows remain provisional.</div>',unsafe_allow_html=True)
    st.info("Open **Company explorer** to compare five equities using historical research results, or **Model validation** to examine the holdout test. No upload required.")

elif page=="Company explorer":
    st.markdown('<div class="efl-kicker">EQUITY INTELLIGENCE  /  COMPANY EXPLORER</div>',unsafe_allow_html=True)
    company_names={"AAPL":"Apple Inc.","NVDA":"NVIDIA Corporation","MSFT":"Microsoft Corporation","TSLA":"Tesla, Inc.","AMZN":"Amazon.com, Inc."}
    selected=st.selectbox("SELECT COVERAGE",list(company_names),format_func=lambda t:f"{t}  —  {company_names[t]}")
    r=COMPANY_SNAPSHOT[selected]
    st.markdown(f'<div class="efl-profile"><div class="tag">US EQUITIES  /  {selected}  /  HISTORICAL RESEARCH</div><div class="name">{company_names[selected]}</div><div class="desc">An empirical view of earnings surprises and market-adjusted price reactions. Historical observations only; not a price forecast or investment recommendation.</div></div>',unsafe_allow_html=True)
    a,b,c,dcol=st.columns(4,gap="large")
    a.metric("Earnings events",r["events"])
    b.metric("Negative reactions",f'{r["negative_rate"]:.1f}%')
    c.metric("Positive EPS surprises",r["beat_events"])
    dcol.metric("Beats with negative returns",f'{r["beat_negative_rate"]:.1f}%')
    st.markdown(f'<div class="efl-insight"><strong>Research observation.</strong> For {company_names[selected]}, {r["beat_negative_rate"]:.1f}% of positive EPS surprises coincided with negative SPY-adjusted event-window returns across {r["beat_events"]} positive-surprise observations. This does not establish causality.</div>',unsafe_allow_html=True)
    left,right=st.columns([1.4,1],gap="large")
    with left:
        st.markdown('<div class="efl-sect">01  /  PEER COMPARISON</div>',unsafe_allow_html=True)
        metric=st.radio("COMPARE BY",["EPS beats with negative returns","All negative reactions"],horizontal=True)
        field="beat_negative_rate" if metric=="EPS beats with negative returns" else "negative_rate"
        chart=pd.DataFrame([{"Ticker":t,"Negative reaction rate (%)":v[field]} for t,v in COMPANY_SNAPSHOT.items()]).set_index("Ticker")
        st.bar_chart(chart,horizontal=True,color="#8faecc",height=270)
        st.markdown('<div class="efl-note">Percent of events with negative abnormal returns. The five company samples differ in composition; this comparison is descriptive.</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="efl-sect">02  /  RETURN DISTRIBUTION SUMMARY</div>',unsafe_allow_html=True)
        a2,b2=st.columns(2)
        a2.metric("Mean abnormal return",f'{r["mean_return"]:+.2f}%')
        b2.metric("Median abnormal return",f'{r["median_return"]:+.2f}%')
        st.markdown('<div class="efl-sect">READING THE DATA</div>',unsafe_allow_html=True)
        st.write("An abnormal return measures stock performance relative to SPY across a provisional earnings event window. A negative result means relative underperformance, not necessarily a negative absolute stock return.")
        st.markdown('<div class="efl-note">The 196-event v0.8 snapshot is distinct from the initial 198-event study. Earnings timestamps have not been independently verified.</div>',unsafe_allow_html=True)
    st.markdown('<hr class="efl-rule">',unsafe_allow_html=True)
    with st.expander("ADVANCED  /  Inspect individual events using your research CSV",expanded=False):
        st.caption("Optional: upload your own v0.8 export to explore individual observations. The public application does not bundle provider-derived event records.")
        uploaded=st.file_uploader("Upload v0.8 research CSV",type="csv",key="explorer_csv")
        if uploaded is not None:
            from efi_v1_showcase import _load
            try:
                data=_load(uploaded)
                view=data[data["ticker"]==selected]
                if view.empty:
                    st.warning("No observations for this ticker in the uploaded file.")
                else:
                    st.scatter_chart(view,x="earnings_surprise_pct",y="abnormal_return_pct",height=350)
                    cols=[c for c in ["announcement_date","earnings_surprise_pct","abnormal_return_pct","prototype_fragility_score","split"] if c in view.columns]
                    st.dataframe(view[cols],hide_index=True,use_container_width=True)
            except Exception as exc:
                st.error(f"Unable to read CSV: {exc}")
    st.markdown('<div class="efl-tiny">RESEARCH SNAPSHOT  /  V0.8  /  196 USABLE EVENTS  /  FIVE US EQUITIES</div>',unsafe_allow_html=True)

elif page=="Model validation":
    st.markdown('<div class="efl-kicker">RESEARCH TERMINAL / MODEL VALIDATION</div>',unsafe_allow_html=True)
    st.title("Did the prototype identify fragility?")
    st.write("The first score used two price-based pre-event features with provisional 50/50 weights. We separated earlier training observations from a later chronological holdout.")
    a,b,c=st.columns(3)
    a.metric("Usable observations","196")
    b.metric("Training observations","137")
    c.metric("Later holdout","59")
    result=pd.DataFrame({"Score group":["Higher","Lower"],"Events":[22,37],"Negative reactions (%)":[50.0,59.46],"Mean abnormal return (%)":[-0.05,-0.22],"Median abnormal return (%)":[0.0,-1.26]})
    st.markdown('<div class="efl-sect">OUT-OF-SAMPLE COMPARISON</div>',unsafe_allow_html=True)
    st.dataframe(result,hide_index=True,use_container_width=True)
    st.bar_chart(result.set_index("Score group")[["Negative reactions (%)"]],horizontal=True,color="#81A8D1")
    st.markdown('<div class="efl-panel"><div class="eyebrow">INTERPRETATION</div><div class="big">The first model did not support the hypothesized direction.</div><div class="small">50.0% of higher-score events had negative abnormal returns, compared with 59.46% of lower-score events. This is a small, selected sample, not evidence of a tradable signal or proof against the broader hypothesis.</div></div>',unsafe_allow_html=True)
    with st.expander("Features and limitations"):
        st.write("**20-session momentum:** a pre-event price trend, not a direct measure of investor expectations.")
        st.write("**60-session downside RMS volatility:** a historical measure of negative daily price fluctuations.")
        st.write("**Caveats:** exact earnings announcement timestamps were not verified; event windows may contain unrelated information; repeated firms and common market regimes reduce independence; weights are unvalidated.")

elif page=="Methodology":
    st.markdown('<div class="efl-kicker">RESEARCH NOTE 001 / METHODS</div>',unsafe_allow_html=True)
    st.title("Methodology & limitations")
    st.markdown("### Data and event returns")
    st.write("Five US equities: AAPL, NVDA, MSFT, TSLA and AMZN. Quarterly EPS surprises were sourced from Alpha Vantage; historical adjusted stock and SPY closes from Yahoo Finance. The published event-study snapshot includes 198 matched observations; 196 have usable pre-event features.")
    st.write("Provisional abnormal return = stock event-window return minus SPY return over the same window. Before-open versus after-close earnings announcement times were not verified. Returns cannot be attributed causally to earnings alone.")
    st.markdown("### Prototype score and validation")
    st.write("The prototype combines percentile-scaled 20-session momentum and 60-session downside RMS volatility with provisional equal weights. Score scaling and the high/low threshold use the training period; later observations are held out chronologically.")
    st.markdown("### Research boundaries")
    st.write("No statistical significance, predictive ability, investable alpha or causal relationship has been established. The five-stock universe is selected, event observations are dependent, and the score does not directly measure analyst expectations. Earnings surprise itself is not a valid pre-announcement feature.")
    st.caption("The public overview displays fixed aggregate results; historical provider-derived event records are not bundled with this application.")

else:
    st.markdown('<div class="efl-kicker">RESEARCH TERMINAL / ADVANCED WORKBENCH</div>',unsafe_allow_html=True)
    st.title("Advanced research tools")
    st.caption("Legacy experiments and live provider-backed analysis. These tools are retained for reproducibility, not presented as validated investment signals.")
    from legacy_workbench import render_legacy_workbench
    render_legacy_workbench()
