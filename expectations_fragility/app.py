"""Expectations Fragility Lab | independent exploratory equity research."""
from pathlib import Path
import html
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="EFL | Expectations Fragility Lab", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "efl_research_events.csv"

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Libre+Baskerville:wght@400;700&display=swap');
:root{color-scheme:dark}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],[data-testid="stHeader"]{background:#090e16!important;color:#e9eff7!important}
[data-testid="stSidebar"]{background:#0e1723!important;border-right:1px solid #26384c!important}
[data-testid="stMainBlockContainer"]{max-width:1330px!important;padding-top:2rem!important;padding-bottom:3rem!important}
html,body,p,div,label,button{font-family:'DM Sans',sans-serif}
h1,h2,h3{letter-spacing:-.035em!important}h1{font-size:clamp(2rem,3vw,3.1rem)!important}h2{font-size:1.35rem!important}
[data-testid="stMetric"]{background:transparent!important;border:0!important;border-top:1px solid #39536d!important;padding:14px 4px!important}
[data-testid="stMetricLabel"]{color:#9fb0c3!important}
[data-testid="stMetricValue"]{color:#f0f5fb!important;font-size:clamp(1.3rem,2vw,2rem)!important;letter-spacing:-.045em!important}
[data-testid="stSelectbox"]>div>div{background:#132131!important;border-color:#38516a!important}
[data-testid="stDataFrame"],[data-testid="stExpander"],[data-testid="stFileUploader"]{border-color:#30465d!important;border-radius:4px!important}
[data-testid="stExpander"] summary p{white-space:normal!important;overflow-wrap:anywhere!important}
[data-testid="stSidebarCollapseButton"] span,[data-testid="stSidebarCollapsedControl"] span{font-size:0!important}
[data-testid="stSidebarCollapseButton"] span::after,[data-testid="stSidebarCollapsedControl"] span::after{content:'‹';font-family:Arial,sans-serif;font-size:22px!important;color:#c7d5e4}
.stButton>button{background:#15293d;border:1px solid #476582;border-radius:3px;color:#eaf1f9}
.efl-brand{font:400 24px Georgia,serif;letter-spacing:.16em;color:#f0f4f9;margin-bottom:5px}.efl-brand b{color:#8babc9;font-weight:400}
.efl-eyebrow{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:#9eb9d2;margin:8px 0 12px}
.efl-hero{border-top:1px solid #56738d;border-bottom:1px solid #304458;padding:25px 0 26px;margin:10px 0 24px}
.efl-hero h1{font:400 clamp(2.15rem,3.4vw,3.65rem)/1.24 'Libre Baskerville',Georgia,serif!important;letter-spacing:-.045em!important;max-width:960px;color:#f1f5fb;margin:0 0 15px}
.efl-deck{font-size:1rem;line-height:1.65;color:#a9bbcd;max-width:800px}
.efl-section{font:500 11px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:#9cb7d0;margin:24px 0 13px}
.efl-statement{background:#101c2a;border-left:2px solid #8eacc9;padding:20px 24px;margin:20px 0;color:#d6e0eb;line-height:1.6}
.efl-statement strong{font-size:1.13rem;color:#f1f5fb}
.efl-small{color:#93a7bc;font-size:.84rem;line-height:1.65}
.efl-company{font:400 clamp(2rem,3.3vw,3.4rem)/1.3 'Libre Baskerville',Georgia,serif;color:#f1f5fb;letter-spacing:-.045em;margin:8px 0}
.efl-rule{border:0;border-top:1px solid #2c4156;margin:15px 0}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_events():
    if not DATA_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(DATA_FILE)
    required = {'ticker','announcement_date','earnings_surprise_pct','abnormal_return_pct','momentum_20d_pct','downside_rms_60d_pp','prototype_fragility_score','split','group'}
    if not required.issubset(df.columns):
        return pd.DataFrame()
    df['announcement_date'] = pd.to_datetime(df['announcement_date'],errors='coerce')
    for c in ['earnings_surprise_pct','abnormal_return_pct','momentum_20d_pct','downside_rms_60d_pp','prototype_fragility_score']:
        df[c] = pd.to_numeric(df[c],errors='coerce')
    df['ticker'] = df['ticker'].astype(str).str.upper().str.strip()
    df['split'] = df['split'].astype(str).str.lower().str.strip()
    return df.dropna(subset=['ticker','announcement_date','earnings_surprise_pct','abnormal_return_pct']).sort_values('announcement_date')

D = load_events()
NAMES = {'AAPL':'Apple Inc.','NVDA':'NVIDIA Corporation','MSFT':'Microsoft Corporation','TSLA':'Tesla, Inc.','AMZN':'Amazon.com, Inc.'}
BLUE='#93b5d4'; CORAL='#d89d91'; GRID='#304359'

def heading(kicker,title,deck=''):
    st.markdown(f'<div class="efl-eyebrow">{html.escape(kicker)}</div><div class="efl-hero"><h1>{html.escape(title)}</h1><div class="efl-deck">{html.escape(deck)}</div></div>',unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="efl-section">{html.escape(label)}</div>',unsafe_allow_html=True)

def note(msg):
    st.markdown(f'<div class="efl-small">{html.escape(msg)}</div>',unsafe_allow_html=True)

def percent_negative(frame):
    return 100*(frame['abnormal_return_pct']<0).mean() if len(frame) else float('nan')

def plot_scatter(frame,x,y,tooltip=None):
    tooltip=tooltip or ['ticker','announcement_date','earnings_surprise_pct','abnormal_return_pct']
    base=alt.Chart(frame).mark_circle(size=64,opacity=.72).encode(
        x=alt.X(x,axis=alt.Axis(grid=True,gridColor=GRID,titleColor='#aabed1',labelColor='#aabed1')),
        y=alt.Y(y,axis=alt.Axis(grid=True,gridColor=GRID,titleColor='#aabed1',labelColor='#aabed1')),
        color=alt.Color('ticker:N',legend=alt.Legend(title=None,orient='bottom'),scale=alt.Scale(range=['#89b6d7','#d9a08f','#92c2b2','#b4a1cf','#d5bd8b'])),
        tooltip=tooltip).properties(height=340)
    st.altair_chart(base, use_container_width=True,theme=None)

with st.sidebar:
    st.markdown('<div class="efl-brand">E<b>|</b>F<b>|</b>L</div>',unsafe_allow_html=True)
    st.caption('EXPECTATIONS FRAGILITY LAB')
    st.divider()
    page=st.radio('RESEARCH TERMINAL',['Overview','Company explorer','Model validation','Methodology','Advanced workbench'])
    st.divider()
    st.caption('INDEPENDENT EQUITY RESEARCH')
    st.caption('Five US equities · historical sample')
    st.caption('Exploratory research · Not investment advice')

if page=='Overview':
    heading('RESEARCH NOTE 001  /  OCTOBER 2026','When earnings beats fail to impress the market.',
            'An empirical investigation of earnings surprises, SPY-adjusted market reactions and whether pre-announcement price conditions identify fragility.')
    a,b,c=st.columns(3)
    a.metric('Initial matched events','198')
    b.metric('EPS beats followed by negative returns','42.9%')
    c.metric('Usable model observations','196')
    st.markdown('<div class="efl-statement"><strong>The paradox: beating earnings estimates does not guarantee market outperformance.</strong><div>In the initial 198-event study, 69 of 161 positive EPS surprises coincided with negative SPY-adjusted event-window returns. This describes an association, not a causal effect.</div></div>',unsafe_allow_html=True)
    left,right=st.columns([1.1,1],gap='large')
    with left:
        section('01 / THE RESEARCH QUESTION')
        st.write('Can price conditions observed **before** an earnings announcement help identify companies more likely to underperform the market around the event?')
        section('02 / WHAT THE HOLDOUT SHOWED')
        st.write('**The initial prototype did not validate.** Higher-scoring events had a **50.0%** negative-reaction rate versus **59.5%** for lower-scoring events—the reverse of the hypothesized direction.')
        note('The 198-event paradox sample and 196-event feature sample are different snapshots; do not treat their denominators as interchangeable.')
    with right:
        section('LATER HOLDOUT / NEGATIVE REACTION FREQUENCY')
        hold=pd.DataFrame({'Group':['Higher EFI','Lower EFI'],'Rate':[50,59.46]})
        bar=alt.Chart(hold).mark_bar(size=25,color=BLUE).encode(x=alt.X('Rate:Q',scale=alt.Scale(domain=[0,70]),title='Negative reactions (%)'),y=alt.Y('Group:N',sort=['Higher EFI','Lower EFI'],title=None),tooltip=['Group','Rate'])
        st.altair_chart(bar.properties(height=190),use_container_width=True)
        note('59 holdout events: 22 higher-score and 37 lower-score observations. Provisional event windows.')
    if not D.empty:
        section('COVERAGE / FIVE EQUITIES')
        overview=D.groupby('ticker').agg(Events=('ticker','size'),Mean_return=('abnormal_return_pct','mean')).reset_index()
        overview['Mean_return']=overview['Mean_return'].round(2)
        st.dataframe(overview.rename(columns={'ticker':'Ticker','Mean_return':'Mean abnormal return (%)'}),hide_index=True,use_container_width=True)

elif page=='Company explorer':
    section('EQUITY INTELLIGENCE / COMPANY EXPLORER')
    selected=st.selectbox('SELECT COVERAGE',list(NAMES),format_func=lambda t:f'{t} — {NAMES[t]}')
    st.markdown(f'<div class="efl-company">{html.escape(NAMES[selected])}</div>',unsafe_allow_html=True)
    note(f'{selected} · Historical earnings event study · SPY-adjusted returns · Not a stock forecast')
    if D.empty:
        st.error('The companion research file efl_research_events.csv is missing. Upload it next to app.py.')
    else:
        group=D[D.ticker.eq(selected)].copy()
        beats=group[group.earnings_surprise_pct>0]
        a,b,c,d=st.columns(4)
        a.metric('Earnings events',len(group))
        b.metric('Negative reactions',f'{percent_negative(group):.1f}%')
        c.metric('Positive EPS surprises',len(beats))
        d.metric('Beats with negative returns',f'{percent_negative(beats):.1f}%' if len(beats) else 'N/A')
        section('01 / EARNINGS SURPRISE VS. MARKET REACTION')
        st.write('Each point is one historical earnings event. Hover to inspect the event date, EPS surprise and SPY-adjusted return.')
        filtered=group.copy()
        col1,col2=st.columns([1,1])
        with col1:
            sample=st.selectbox('OBSERVATION PERIOD',['All events','Training','Later holdout'])
        with col2:
            cap=st.checkbox('Exclude absolute EPS surprises above 100%',value=False)
        if sample!='All events':
            filtered=filtered[filtered.split.eq('training' if sample=='Training' else 'holdout')]
        if cap:
            filtered=filtered[filtered.earnings_surprise_pct.abs()<=100]
        if filtered.empty:
            st.info('No observations match the selected filters.')
        else:
            plot_scatter(filtered,'earnings_surprise_pct:Q','abnormal_return_pct:Q')
            note(f'{len(filtered)} selected events. X: EPS surprise (%). Y: stock return minus SPY return (%), over a provisional event window.')
        left,right=st.columns([1.15,1],gap='large')
        with left:
            section('02 / CROSS-COMPANY COMPARISON')
            metric=st.radio('COMPARE BY',['Beats followed by negative returns','All negative reactions'],horizontal=True)
            rows=[]
            for ticker,g in D.groupby('ticker'):
                subset=g[g.earnings_surprise_pct>0] if metric.startswith('Beats') else g
                rows.append({'Ticker':ticker,'Rate':percent_negative(subset)})
            comp=pd.DataFrame(rows)
            bar=alt.Chart(comp).mark_bar(size=20,color=BLUE).encode(x=alt.X('Rate:Q',title='Negative reaction rate (%)',scale=alt.Scale(domain=[0,70])),y=alt.Y('Ticker:N',sort='-x',title=None),tooltip=['Ticker','Rate'])
            st.altair_chart(bar.properties(height=250),use_container_width=True)
        with right:
            section('03 / RETURN PROFILE')
            x,y=st.columns(2)
            x.metric('Mean abnormal return',f'{group.abnormal_return_pct.mean():+.2f}%')
            y.metric('Median abnormal return',f'{group.abnormal_return_pct.median():+.2f}%')
            note('Negative abnormal returns indicate underperformance versus SPY, not necessarily an absolute stock-price decline.')
            note('These five selected stocks have small, dependent samples. Comparisons are descriptive, not rankings of future risk.')
        with st.expander('RESEARCH DATA / View historical event observations'):
            cols=['announcement_date','earnings_surprise_pct','abnormal_return_pct','momentum_20d_pct','downside_rms_60d_pp','split']
            st.dataframe(group[cols].sort_values('announcement_date',ascending=False),hide_index=True,use_container_width=True)

elif page=='Model validation':
    heading('MODEL RESEARCH / OUT-OF-SAMPLE TEST','A hypothesis tested. Not confirmed.',
            'The prototype EFI combines pre-event price momentum and downside volatility. Its later chronological holdout did not support the expected relationship.')
    a,b,c=st.columns(3)
    a.metric('Usable events','196')
    b.metric('Training observations','137')
    c.metric('Later holdout','59')
    section('01 / HOLDOUT COMPARISON')
    summary=pd.DataFrame({'Score group':['Higher EFI','Lower EFI'],'Events':[22,37],'Negative returns (%)':[50.0,59.46],'Mean abnormal return (%)':[-.05,-.22],'Median abnormal return (%)':[0,-1.26]})
    st.dataframe(summary,hide_index=True,use_container_width=True)
    st.altair_chart(alt.Chart(summary).mark_bar(size=28,color=BLUE).encode(x=alt.X('Negative returns (%):Q',scale=alt.Scale(domain=[0,70])),y=alt.Y('Score group:N',sort=['Higher EFI','Lower EFI']),tooltip=list(summary.columns)).properties(height=190),use_container_width=True)
    st.markdown('<div class="efl-statement"><strong>The observed direction was opposite to the hypothesis.</strong><div>11 of 22 higher-score events had negative abnormal returns, versus 22 of 37 lower-score events. This is not evidence of validated predictive performance.</div></div>',unsafe_allow_html=True)
    if not D.empty:
        section('02 / EXPLORE SCORE VS. OBSERVED RETURN')
        scope=st.radio('SAMPLE',['Later holdout','Training','All events'],horizontal=True)
        chosen=D if scope=='All events' else D[D.split.eq('holdout' if scope=='Later holdout' else 'training')]
        plot_scatter(chosen,'prototype_fragility_score:Q','abnormal_return_pct:Q',tooltip=['ticker','announcement_date','prototype_fragility_score','abnormal_return_pct'])
        section('03 / FEATURE ASSOCIATIONS')
        features={'20-session momentum':'momentum_20d_pct','60-session downside RMS':'downside_rms_60d_pp','Prototype EFI':'prototype_fragility_score'}
        corrs=[]
        for name,col in features.items():
            corrs.append({'Feature':name,'Pearson':chosen[col].corr(chosen.abnormal_return_pct),'Spearman':chosen[col].corr(chosen.abnormal_return_pct,method='spearman')})
        st.dataframe(pd.DataFrame(corrs).round(3),hide_index=True,use_container_width=True)
        note('Feature correlations are descriptive; they are not measures of forecasting accuracy.')

elif page=='Methodology':
    heading('RESEARCH NOTE 001 / METHODS','Methodology & research boundaries',
            'Transparent data sources, exploratory construction and limitations of the earnings event study.')
    section('01 / DATA SOURCES')
    st.write('Quarterly earnings actuals and analyst estimates: **Alpha Vantage**. Adjusted daily stock and benchmark prices: **Yahoo Finance** via yfinance. Coverage: AAPL, NVDA, MSFT, TSLA and AMZN.')
    section('02 / EVENT STUDY')
    st.write('A provisional abnormal event-window return is the stock return minus the SPY return over the same window. Exact announcement times (before-open versus after-close) were not independently verified, so event attribution is limited.')
    section('03 / PRE-EVENT PROTOTYPE')
    st.write('The EFI prototype combines **20-session momentum** and **60-session downside RMS volatility** using equal weights and training-referenced percentile ranks. A chronological split uses **137 training** and **59 later holdout** events. The weights are provisional and unvalidated.')
    section('04 / INTERPRETATION')
    st.write('The 198-event initial study and 196-event feature dataset are distinct analysis snapshots. The five-firm sample is selected; events are not independent; market regimes and unrelated news may affect returns. EPS surprise is only known after the earnings release and is **not** a pre-announcement predictor.')
    st.write('No causal mechanism, statistical significance, tradable alpha, or robust predictive power has been established. Historical data access and redistribution terms should be checked before publishing event-level records.')

else:
    heading('RESEARCH TERMINAL / ADVANCED WORKBENCH','Research workspace',
            'Optional legacy tools and experiments, separate from the published empirical findings.')
    try:
        from legacy_workbench import render_legacy_workbench
        render_legacy_workbench()
    except ImportError:
        st.info('The optional legacy_workbench.py module is not installed. The four main research sections remain fully functional.')
    except Exception as exc:
        st.warning(f'Legacy workbench could not be loaded: {exc}')

st.markdown('<hr class="efl-rule"><div class="efl-small">EXPECTATIONS FRAGILITY LAB · INDEPENDENT EXPLORATORY EQUITY RESEARCH · NOT INVESTMENT ADVICE</div>',unsafe_allow_html=True)
