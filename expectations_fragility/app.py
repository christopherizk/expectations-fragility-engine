"""Expectations Fragility Lab | compact institutional research terminal.

The overview contains fixed, aggregated research snapshots; the interactive
research workspace and earlier experiments remain accessible separately.
"""
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="EFL | Expectations Fragility Lab", page_icon="E", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#080B10!important;color:#E9EFF6!important}
[data-testid="stSidebar"]{background:#0C1119!important;border-right:1px solid #243040!important}
[data-testid="stMainBlockContainer"]{max-width:1330px!important;padding-top:1.5rem!important}
html,body,[class*="st-"]{font-family:'DM Sans',sans-serif!important}
h1,h2,h3{letter-spacing:-.035em!important}h1{font-size:2.7rem!important}h2{font-size:1.45rem!important;border:0!important;padding-top:0!important}
[data-testid="stMetric"]{background:#101925;border:1px solid #28394B;border-radius:2px;padding:14px 17px}
[data-testid="stMetricLabel"]{color:#95A7BB!important}
[data-testid="stMetricValue"]{font-family:'IBM Plex Mono',monospace!important;color:#EDF3F9!important}
[data-testid="stDataFrame"],[data-testid="stExpander"],[data-testid="stFileUploader"]{border-color:#28394B!important;border-radius:3px!important}
.stButton>button{border-radius:2px!important;background:#182B3F!important;border:1px solid #416789!important;color:#EAF2FB!important}
.efl-kicker{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.19em;color:#84A8CA;margin-bottom:12px}
.efl-hero{border-top:1px solid #476E91;border-bottom:1px solid #263747;padding:22px 0 24px;margin:10px 0 25px}
.efl-hero h1{font-size:clamp(2rem,3.6vw,3.45rem)!important;line-height:1.1;margin:0 0 14px;font-weight:600;max-width:850px}
.efl-deck{font-size:1rem;line-height:1.6;color:#A6B6C8;max-width:800px}
.efl-panel{background:#111B28;border:1px solid #293B50;border-left:3px solid #86ACD1;padding:21px 24px;margin:18px 0}
.efl-panel .eyebrow{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.13em;color:#90AFCC}
.efl-panel .big{font-size:1.45rem;line-height:1.35;font-weight:600;margin:9px 0}
.efl-panel .small{color:#A4B2C2;font-size:.92rem;line-height:1.55}
.efl-tiny{font:400 11px 'IBM Plex Mono',monospace;color:#8495A8;letter-spacing:.06em}
.efl-brand{font-family:Georgia,serif;letter-spacing:.18em;color:#E7EDF4;font-size:1.5rem}
.efl-brand span{color:#82ABD1}
.efl-sect{font:500 11px 'IBM Plex Mono',monospace;color:#89ACCE;letter-spacing:.17em;margin:18px 0 12px}
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
          'beat_negative_rate': np.float64(37.8),
          'events': 39,
          'mean_return': np.float64(1.21),
          'median_return': np.float64(1.95),
          'negative_rate': np.float64(38.5)},
 'AMZN': {'beat_events': 29,
          'beat_negative_rate': np.float64(41.4),
          'events': 39,
          'mean_return': np.float64(0.66),
          'median_return': np.float64(-0.1),
          'negative_rate': np.float64(51.3)},
 'MSFT': {'beat_events': 36,
          'beat_negative_rate': np.float64(41.7),
          'events': 39,
          'mean_return': np.float64(0.79),
          'median_return': np.float64(1.06),
          'negative_rate': np.float64(43.6)},
 'NVDA': {'beat_events': 35,
          'beat_negative_rate': np.float64(45.7),
          'events': 39,
          'mean_return': np.float64(1.15),
          'median_return': np.float64(0.75),
          'negative_rate': np.float64(48.7)},
 'TSLA': {'beat_events': 22,
          'beat_negative_rate': np.float64(54.5),
          'events': 40,
          'mean_return': np.float64(-0.77),
          'median_return': np.float64(-2.12),
          'negative_rate': np.float64(57.5)}}

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
    st.markdown('<div class="efl-kicker">RESEARCH TERMINAL / COMPANY EXPLORER</div>',unsafe_allow_html=True)
    st.title("Explore earnings reactions")
    st.caption("Historical company summaries calculated from the 196-event v0.8 research snapshot. No upload required.")
    company_names={"AAPL":"Apple","NVDA":"NVIDIA","MSFT":"Microsoft","TSLA":"Tesla","AMZN":"Amazon"}
    selected=st.selectbox("SELECT EQUITY",list(company_names),format_func=lambda t:f"{t}  /  {company_names[t]}")
    r=COMPANY_SNAPSHOT[selected]
    st.markdown(f'<div class="efl-panel"><div class="eyebrow">{selected} / {company_names[selected].upper()}</div><div class="big">Earnings reaction profile</div><div class="small">Descriptive historical statistics, not a forecast. Returns are SPY-adjusted over provisional event windows.</div></div>',unsafe_allow_html=True)
    a,b,c,dcol=st.columns(4)
    a.metric("Events analyzed",r["events"])
    b.metric("Negative reactions",f'{r["negative_rate"]:.1f}%')
    c.metric("EPS beats",r["beat_events"])
    dcol.metric("Beats with negative returns",f'{r["beat_negative_rate"]:.1f}%')
    left,right=st.columns([1.25,1],gap="large")
    with left:
        st.markdown('<div class="efl-sect">01 / CROSS-COMPANY COMPARISON</div>',unsafe_allow_html=True)
        metric=st.radio("Compare companies by",["EPS beats followed by negative returns","All events with negative returns"],horizontal=True)
        field="beat_negative_rate" if metric.startswith("EPS") else "negative_rate"
        compare=pd.DataFrame([{"Ticker":t,"Negative reactions (%)":v[field]} for t,v in COMPANY_SNAPSHOT.items()]).set_index("Ticker")
        st.bar_chart(compare,horizontal=True,color="#81A8D1")
        st.caption("Each company has a different sample composition. Differences are descriptive, not statistically tested.")
    with right:
        st.markdown('<div class="efl-sect">02 / RETURN PROFILE</div>',unsafe_allow_html=True)
        st.metric("Mean abnormal return",f'{r["mean_return"]:+.2f}%')
        st.metric("Median abnormal return",f'{r["median_return"]:+.2f}%')
        st.markdown('<div class="efl-sect">HOW TO READ THIS</div>',unsafe_allow_html=True)
        st.write("A negative abnormal return means the stock underperformed SPY over the provisional event window. It does not establish that earnings caused the decline.")
    with st.expander("Optional / inspect individual events from your own research CSV"):
        uploaded=st.file_uploader("Upload v0.8 research CSV",type="csv",key="explorer_csv")
        if uploaded is not None:
            from efi_v1_showcase import _load
            try:
                data=_load(uploaded)
                view=data[data["ticker"]==selected]
                if view.empty: st.warning("No observations for this ticker in the uploaded file.")
                else:
                    st.scatter_chart(view,x="earnings_surprise_pct",y="abnormal_return_pct")
                    st.dataframe(view[["announcement_date","earnings_surprise_pct","abnormal_return_pct","prototype_fragility_score","split"]],hide_index=True,use_container_width=True)
            except Exception as exc: st.error(f"Unable to read CSV: {exc}")
    st.markdown('<div class="efl-tiny">SOURCE: v0.8 RESEARCH EXPORT · 196 USABLE EVENTS · AGGREGATED METRICS ONLY · PROVISIONAL TIMING</div>',unsafe_allow_html=True)

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
