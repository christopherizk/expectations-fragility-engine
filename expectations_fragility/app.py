import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title='Expectations Fragility Lab',layout='wide')
st.title('Expectations Fragility Lab')
st.caption('Research prototype · scenario exploration only · no predictive claims')
st.write('Explore how valuation, disagreement, momentum and historical sensitivity could combine into an experimental Expectations Fragility Index (EFI).')
with st.sidebar:
    st.header('Scenario inputs (0–100)')
    valuation=st.slider('Valuation expectations',0,100,75)
    dispersion=st.slider('Forecast dispersion',0,100,60)
    momentum=st.slider('Pre-event momentum',0,100,45)
    sensitivity=st.slider('Historical downside sensitivity',0,100,80)
    st.header('Hypothetical earnings event')
    surprise=st.slider('Earnings surprise (%)',-30,30,-5)
    beta=st.slider('Sensitivity coefficient (illustrative)',0.0,3.0,1.0,0.1)
weights={'Valuation expectations':.30,'Forecast dispersion':.20,'Pre-event momentum':.15,'Historical downside sensitivity':.35}
values={'Valuation expectations':valuation,'Forecast dispersion':dispersion,'Pre-event momentum':momentum,'Historical downside sensitivity':sensitivity}
score=sum(weights[k]*values[k] for k in weights)
a,b=st.columns(2)
a.metric('Experimental EFI',f'{score:.1f}/100')
b.metric('Illustrative event response',f'{surprise*beta*(.5+score/100):.1f}%')
st.warning('The event response is an arbitrary scenario formula, NOT a return forecast. EFI weights are not calibrated or validated.')
st.subheader('Component contributions')
st.bar_chart(pd.DataFrame({'Weighted contribution':{k:values[k]*weights[k] for k in weights}}))
st.subheader('Sensitivity to earnings surprise')
surprises=np.arange(-30,31,2)
responses=surprises*beta*(.5+score/100)
st.line_chart(pd.DataFrame({'Illustrative response (%)':responses},index=surprises),x_label='Earnings surprise (%)',y_label='Illustrative response (%)')
st.subheader('Research roadmap')
st.markdown('''1. Define a testable target: abnormal return after earnings announcements, conditional on negative surprise.\n2. Obtain point-in-time analyst forecasts, announcement timestamps, prices, sector and market factors.\n3. Normalize each EFI feature using training-period distributions only.\n4. Estimate weights on a training sample; evaluate chronological holdout performance against simple baselines.\n5. Report uncertainty, sector effects, transaction costs (if applicable), data gaps, and negative findings.''')
st.download_button('Download current scenario (CSV)',pd.DataFrame([dict(**values,EFI=score,Earnings_surprise_pct=surprise,Illustrative_response_pct=surprise*beta*(.5+score/100))]).to_csv(index=False),file_name='efi_scenario.csv',mime='text/csv')

st.divider()
st.header('Historical event-study workbench · v0.2')
st.write('Upload an earnings-event CSV to test whether EFI adds information beyond a valuation-only model. This is a preliminary diagnostic, not a validated trading strategy.')
st.code('ticker,announcement_date,earnings_surprise_pct,abnormal_return_pct,valuation_pressure,forecast_dispersion,pre_event_momentum,historical_downside_sensitivity',language='text')
st.caption('All four feature scores must be 0–100 and measured strictly before each announcement. Abnormal return is the market-adjusted event-window return in percentage points. Use one consistent, documented event window.')
uploaded=st.file_uploader('Upload historical event data (CSV)',type=['csv'])
if uploaded:
    from research import evaluate
    try:
        raw=pd.read_csv(uploaded)
        results, predictions, info=evaluate(raw)
        st.success(f"Analyzed {info['negative_surprises']} negative-surprise events; {info['training']} training and {info['holdout']} chronological holdout events (from {info['holdout_start']}).")
        st.dataframe(results,hide_index=True,use_container_width=True)
        st.caption('MAE/RMSE are in percentage points of downside abnormal return; lower is better. A lower error is not evidence of tradable alpha. The weights remain illustrative.')
        st.download_button('Download holdout predictions',predictions.to_csv(index=False),file_name='efi_holdout_results.csv',mime='text/csv')
        st.dataframe(predictions.head(20),hide_index=True,use_container_width=True)
        st.warning('Research cautions: no controls for sector, volatility, size or surprise magnitude yet; event timing and point-in-time analyst estimates must be verified. Cross-sectional dependence and data leakage may invalidate apparent performance.')
    except Exception as exc:
        st.error(str(exc))
else:
    st.info('No dataset loaded. The application does not invent historical observations or present synthetic results as evidence.')


st.divider()
st.header("Earnings Intelligence · v0.3")

st.caption(
    "Historical earnings analysis powered by Alpha Vantage. "
    "Reported observations, not investment forecasts."
)

with st.form("alpha_fetch"):
    symbol = st.text_input(
        "Stock ticker",
        value="AAPL",
        help="Examples: AAPL, NVDA, MSFT, TSLA, AMZN",
    ).strip().upper()

    fetch = st.form_submit_button("Analyze earnings")

if fetch:
    from data_sources import earnings

    try:
        api_key = st.secrets.get("ALPHA_VANTAGE_API_KEY", "")

        if not api_key:
            st.error("The earnings data service is not configured.")
        else:
            with st.spinner("Retrieving historical earnings..."):
                historical = earnings(symbol, api_key)

            st.session_state["earnings_data"] = historical
            st.session_state["earnings_symbol"] = symbol

    except Exception as exc:
        st.error(f"Data retrieval failed: {exc}")

if "earnings_data" in st.session_state:
    historical = st.session_state["earnings_data"].copy()
    active_symbol = st.session_state["earnings_symbol"]

    st.subheader(f"{active_symbol} · Earnings overview")

    valid = historical.dropna(
        subset=["reportedEPS", "estimatedEPS"]
    ).copy()

    valid["eps_difference"] = (
        valid["reportedEPS"] - valid["estimatedEPS"]
    )

    beats = int((valid["eps_difference"] > 0).sum())
    misses = int((valid["eps_difference"] < 0).sum())
    matches = int((valid["eps_difference"] == 0).sum())

    total = len(valid)
    beat_rate = (beats / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Quarters analyzed", total)
    c2.metric("EPS beats", beats)
    c3.metric("EPS misses", misses)
    c4.metric("Historical beat rate", f"{beat_rate:.1f}%")

    st.caption(
        f"{matches} quarters matched analyst estimates exactly. "
        "Beat rate uses quarters with both reported and estimated EPS."
    )

    st.subheader("Reported EPS vs. Analyst Estimates")

    if not valid.empty:
        eps_chart = valid.set_index("reportedDate")[
            ["reportedEPS", "estimatedEPS"]
        ].rename(
            columns={
                "reportedEPS": "Reported EPS",
                "estimatedEPS": "Estimated EPS",
            }
        )

        st.line_chart(
            eps_chart,
            x_label="Earnings report date",
            y_label="EPS",
        )
    else:
        st.info("No comparable EPS observations are available.")

    st.subheader("Historical Earnings Surprises")

    surprise_data = historical.dropna(
        subset=["surprisePercentage", "reportedDate"]
    ).copy()

    if not surprise_data.empty:
        surprise_chart = surprise_data.set_index(
            "reportedDate"
        )[["surprisePercentage"]].rename(
            columns={
                "surprisePercentage": "EPS surprise (%)"
            }
        )

        st.bar_chart(
            surprise_chart,
            x_label="Earnings report date",
            y_label="EPS surprise (%)",
        )

        st.caption(
            "Surprise percentages are supplied by Alpha Vantage. "
            "Large percentages can occur when estimated EPS "
            "is close to zero."
        )
    else:
        st.info("No earnings surprise percentages are available.")

    st.subheader("Historical Earnings Records")

    display = historical.sort_values(
        "reportedDate",
        ascending=False,
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download earnings dataset (CSV)",
        historical.to_csv(index=False),
        file_name=f"{active_symbol}_earnings.csv",
        mime="text/csv",
    )

    st.info(
        "These statistics describe historical EPS results. "
        "They do not establish whether a stock was attractively "
        "valued or predict its reaction to future announcements. "
        "EFI validation requires pre-announcement features "
        "and market-adjusted event returns."
    )


st.divider()
st.header("Multi-Company Market Reactions · v0.4")

st.caption(
    "Exploratory analysis using daily stock prices and "
    "earnings announcements. Event timing is not verified."
)

from market_reactions import (
    daily_prices,
    build_event_study,
)

companies = st.multiselect(
    "Select companies",
    ["AAPL", "NVDA", "MSFT", "TSLA", "AMZN"],
    default=["AAPL", "NVDA"],
)

run_study = st.button("Run market reaction analysis")

if run_study:
    if not companies:
        st.warning("Select at least one company.")
    else:
        api_key = st.secrets.get(
            "ALPHA_VANTAGE_API_KEY", ""
        )

        if not api_key:
            st.error("Alpha Vantage is not configured.")
        else:
            from data_sources import earnings

            all_events = []

            try:
                with st.spinner(
                    "Retrieving SPY benchmark prices..."
                ):
                    benchmark = daily_prices(
                        "SPY", api_key
                    )

                for ticker in companies:
                    try:
                        with st.spinner(
                            f"Analyzing {ticker}..."
                        ):
                            eps_data = earnings(
                                ticker, api_key
                            )

                            prices = daily_prices(
                                ticker, api_key
                            )

                            events = build_event_study(
                                eps_data,
                                prices,
                                benchmark,
                                ticker,
                            )

                        if not events.empty:
                            all_events.append(events)
                        else:
                            st.warning(
                                f"{ticker}: no matching "
                                "events in available "
                                "price history."
                            )

                    except Exception as exc:
                        st.warning(
                            f"{ticker}: {exc}"
                        )

                if all_events:
                    st.session_state[
                        "market_events"
                    ] = pd.concat(
                        all_events,
                        ignore_index=True,
                    )
                else:
                    st.session_state.pop(
                        "market_events", None
                    )
                    st.info(
                        "No matched events available."
                    )

            except Exception as exc:
                st.error(
                    f"Benchmark retrieval failed: {exc}"
                )

if "market_events" in st.session_state:
    events = st.session_state[
        "market_events"
    ].copy()

    st.subheader("Event Study Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Matched events",
        len(events),
    )

    c2.metric(
        "Companies",
        events["ticker"].nunique(),
    )

    c3.metric(
    "Mean window abnormal return",
    f"{events['abnormal_return_pct'].mean():.2f}%",

    )

    st.subheader(
        "Earnings Surprise vs. Abnormal Return"
    )

    plot_data = events.dropna(
        subset=[
            "earnings_surprise_pct",
            "abnormal_return_pct",
        ]
    )

    if not plot_data.empty:
        st.scatter_chart(
            plot_data,
            x="earnings_surprise_pct",
            y="abnormal_return_pct",
            color="ticker",
        )
    else:
        st.info(
            "No observations available for "
            "the scatter chart."
        )

    st.subheader("Company Comparison")

    summary = events.groupby(
        "ticker"
    ).agg(
        events=("ticker", "size"),
        mean_abnormal_return_pct=(
            "abnormal_return_pct", "mean"
        ),
        median_abnormal_return_pct=(
            "abnormal_return_pct", "median"
        ),
    ).reset_index()

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Event-Level Observations")

    st.dataframe(
        events,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download event study (CSV)",
        events.to_csv(index=False),
        file_name="efi_market_reactions.csv",
        mime="text/csv",
    )
    
st.warning(
    "Research limitations: prices are adjusted daily closes "
    "from Yahoo Finance. Abnormal returns are stock returns "
    "minus SPY returns over provisional event windows. "
    "Announcement timestamps have not been verified. "
    "These are not isolated or causal earnings reactions. "
    "Coverage and data quality must be checked before "
    "interpreting results."
)

st.divider()
st.header("Research Analytics · v0.7")

from reaction_intelligence import render_reaction_intelligence

if "market_events" in st.session_state:
    render_reaction_intelligence(
        st.session_state["market_events"]
    )
else:
    st.info(
        "Run the Multi-Company Market Reactions analysis "
        "above to activate the research dashboard."
    )

    
