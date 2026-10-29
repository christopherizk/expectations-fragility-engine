"""EFI v0.8: exploratory pre-announcement features and chronological holdout.

This is a prototype, not a validated predictive model.
"""
import numpy as np
import pandas as pd
import streamlit as st
from market_reactions import daily_prices


def _features(events, prices_by_ticker):
    rows = []
    for _, event in events.iterrows():
        ticker = str(event['ticker']).upper()
        prices = prices_by_ticker.get(ticker)
        if prices is None or prices.empty:
            continue
        closes = prices['close'].dropna().sort_index()
        date = pd.Timestamp(event['announcement_date']).normalize()
        # Strictly before the reported announcement calendar date.
        history = closes.loc[closes.index < date]
        if len(history) < 61:
            continue
        momentum = 100 * (history.iloc[-1] / history.iloc[-21] - 1)
        daily = history.pct_change().dropna().iloc[-60:] * 100
        downside = np.sqrt(np.mean(np.minimum(daily.to_numpy(), 0.0) ** 2))
        rows.append({**event.to_dict(), 'momentum_20d_pct': momentum,
                     'downside_rms_60d_pp': downside,
                     'last_feature_date': history.index[-1]})
    return pd.DataFrame(rows)


def _percentile(reference, value):
    ref = np.asarray(reference, dtype=float)
    ref = ref[np.isfinite(ref)]
    if not len(ref) or not np.isfinite(value):
        return np.nan
    return 100 * np.mean(ref <= value)


def render_efi_pre_event(events):
    st.subheader('Pre-Earnings Fragility Research · v0.8')
    st.caption('Exploratory price-based fragility proxy. Not the full EFI: historical valuation and analyst dispersion are not yet available.')
    if events is None or events.empty:
        st.info('Run the multi-company event study first.')
        return
    required = {'ticker', 'announcement_date', 'abnormal_return_pct'}
    if not required.issubset(events.columns):
        st.error('Event data is missing required columns.')
        return
    if not st.button('Build pre-earnings features', key='efi08_run'):
        st.info('Click the button to retrieve historical daily prices and calculate pre-announcement features.')
        return
    prices = {}
    for ticker in sorted(events['ticker'].dropna().unique()):
        try:
            prices[ticker] = daily_prices(ticker)
        except Exception as exc:
            st.warning(f'{ticker}: price history unavailable ({exc})')
    frame = _features(events.copy(), prices)
    if frame.empty:
        st.warning('No events had sufficient pre-announcement price history.')
        return
    frame['announcement_date'] = pd.to_datetime(frame['announcement_date'])
    frame = frame.sort_values(['announcement_date', 'ticker']).reset_index(drop=True)
    split = max(1, int(len(frame) * 0.7))
    if split >= len(frame):
        st.warning('Not enough observations for a chronological holdout.')
        return
    train = frame.iloc[:split].copy()
    test = frame.iloc[split:].copy()
    # Scores are based exclusively on feature distributions from the training period.
    # Higher momentum is a speculative expectations proxy; higher downside RMS is a risk proxy.
    for subset in (train, test):
        subset['momentum_rank'] = subset['momentum_20d_pct'].apply(
            lambda x: _percentile(train['momentum_20d_pct'], x))
        subset['downside_rank'] = subset['downside_rms_60d_pp'].apply(
            lambda x: _percentile(train['downside_rms_60d_pp'], x))
        subset['prototype_fragility_score'] = (subset['momentum_rank'] + subset['downside_rank']) / 2
        subset['negative_reaction'] = subset['abnormal_return_pct'] < 0
    threshold = train['prototype_fragility_score'].median()
    test['group'] = np.where(test['prototype_fragility_score'] >= threshold,
                             'Higher prototype score', 'Lower prototype score')
    st.write(f'Events with usable features: **{len(frame)}** · Training: **{len(train)}** · Later holdout: **{len(test)}**')
    st.caption(f'Training ends {train.announcement_date.max().date()}; holdout begins {test.announcement_date.min().date()}. Score threshold fitted on training only: {threshold:.1f}.')
    summary = test.groupby('group').agg(
        events=('negative_reaction', 'size'),
        negative_reaction_rate=('negative_reaction', 'mean'),
        mean_abnormal_return_pct=('abnormal_return_pct', 'mean'),
        median_abnormal_return_pct=('abnormal_return_pct', 'median')).reset_index()
    summary['negative_reaction_rate'] *= 100
    st.markdown('#### Later-period holdout comparison')
    st.dataframe(summary.rename(columns={
        'group': 'Prototype group', 'events': 'Events',
        'negative_reaction_rate': 'Negative returns (%)',
        'mean_abnormal_return_pct': 'Mean abnormal return (%)',
        'median_abnormal_return_pct': 'Median abnormal return (%)'
    }).round(2), use_container_width=True, hide_index=True)
    st.markdown('#### Inspect pre-event features')
    st.dataframe(test[['ticker', 'announcement_date', 'last_feature_date',
                       'momentum_20d_pct', 'downside_rms_60d_pp',
                       'prototype_fragility_score', 'abnormal_return_pct', 'group']],
                 use_container_width=True, hide_index=True)
    st.download_button('Download v0.8 research CSV',
                       pd.concat([train.assign(split='training'), test.assign(split='holdout')]).to_csv(index=False),
                       file_name='efi_v08_pre_event_features.csv', mime='text/csv')
    st.warning('Research caveats: the score and its 50/50 weights are unvalidated. The 20-session momentum proxy is not a direct measure of analyst expectations. Corporate-action-adjusted Yahoo prices and provisional earnings windows are used. The 70/30 split is chronological, but observations share market conditions and firms; this is not an independent external validation. Do not interpret the score as a trading signal.')
