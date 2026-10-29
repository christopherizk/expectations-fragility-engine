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
st.header('Real earnings data · Alpha Vantage')
st.write('Fetch historical reported and estimated EPS for a ticker. Data availability depends on the free API plan and provider limits. This is an exploratory data viewer, not yet a validated EFI score.')
with st.form('alpha_fetch'):
    symbol = st.text_input('Ticker', value='AAPL').strip().upper()
    secret = st.text_input('Alpha Vantage API key (kept out of exports)', type='password', help='For deployment, configure ALPHA_VANTAGE_API_KEY in Streamlit secrets. Never commit it to GitHub.')
    fetch = st.form_submit_button('Fetch real earnings')
if fetch:
    from data_sources import earnings
    try:
        api_key = secret or st.secrets.get('ALPHA_VANTAGE_API_KEY','')
        with st.spinner('Retrieving earnings history...'):
            historical = earnings(symbol, api_key)
        st.success(f'{len(historical)} quarterly earnings records retrieved for {symbol}.')
        st.dataframe(historical, use_container_width=True, hide_index=True)
        st.download_button('Download earnings CSV', historical.to_csv(index=False), file_name=f'{symbol}_earnings.csv', mime='text/csv')
        st.info('Important: this earnings dataset alone cannot validate EFI. We still need pre-event valuation features, reliable announcement timestamps, and market-adjusted event returns. Free coverage may be limited.')
    except Exception as exc:
        st.error(f'Data retrieval failed: {exc}')
