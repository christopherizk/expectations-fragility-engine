"""EFI v1.0 | Research showcase for user-provided derived event-study CSV.

This page is descriptive and does not claim predictive performance.
"""
import numpy as np
import pandas as pd
import streamlit as st

NEEDED = {"ticker", "announcement_date", "earnings_surprise_pct", "abnormal_return_pct",
          "momentum_20d_pct", "downside_rms_60d_pp", "prototype_fragility_score", "split"}


def _load(source):
    data = pd.read_csv(source)
    missing = NEEDED.difference(data.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    data["announcement_date"] = pd.to_datetime(data["announcement_date"], errors="coerce")
    for col in ["earnings_surprise_pct", "abnormal_return_pct", "momentum_20d_pct",
                "downside_rms_60d_pp", "prototype_fragility_score"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data["ticker"] = data["ticker"].astype(str).str.upper().str.strip()
    data["split"] = data["split"].astype(str).str.lower().str.strip()
    return data.replace([np.inf, -np.inf], np.nan).dropna(subset=list(NEEDED)).sort_values("announcement_date")


def _percentage(condition):
    return 100 * condition.mean() if len(condition) else float("nan")


def _fmt(x, suffix="%"):
    return f"{x:+.2f}{suffix}" if pd.notna(x) else "N/A"


def render_efi_showcase():
    st.markdown("---")
    st.title("Expectations Fragility Lab")
    st.caption("v1.0 · Quantitative equity research | Historical earnings reactions & pre-event risk proxies")
    st.info("Research prototype, not an investment recommendation or a validated trading strategy.")
    with st.expander("Research question & methodology", expanded=True):
        st.markdown("**Can pre-announcement market conditions help identify stocks vulnerable to negative market-adjusted returns around earnings?**")
        st.write("We study quarterly EPS surprises, adjusted stock-price returns and SPY-adjusted event-window returns. "
                 "The exploratory score combines 20-session pre-event momentum and 60-session downside volatility "
                 "at equal weights. Score distributions and the high/low cutoff were derived from the training period. "
                 "Later events are reserved for a chronological holdout.")
        st.caption("Important: the return window is a broad proxy and announcement timestamps have not been verified. "
                   "The score is not a direct measure of analyst expectations. No causal or predictive conclusion follows from these charts.")

    st.subheader("Published research snapshot")
    st.caption("Historical sample through 28 October 2026 · Five US equities · Fixed exploratory snapshot")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Usable earnings events", "196")
    k2.metric("Companies", "5")
    k3.metric("Training events", "137")
    k4.metric("Later holdout events", "59")

    st.markdown("**What did the prototype find?**")
    st.write(
        "In the later-period holdout, the higher-scoring group did **not** show "
        "more frequent negative market-adjusted returns than the lower-scoring group. "
        "The exploratory price-based EFI has not demonstrated predictive power."
    )
    snapshot = pd.DataFrame([
        {"Score group": "Higher prototype score", "Events": 22,
         "Negative reactions (%)": 50.00, "Mean abnormal return (%)": -0.05,
         "Median abnormal return (%)": 0.00},
        {"Score group": "Lower prototype score", "Events": 37,
         "Negative reactions (%)": 59.46, "Mean abnormal return (%)": -0.22,
         "Median abnormal return (%)": -1.26},
    ])
    st.dataframe(snapshot, hide_index=True, use_container_width=True)
    st.caption(
        "Holdout starts November 2023. Higher/lower cutoff was determined from "
        "training observations. Figures are rounded; return windows are provisional."
    )
    with st.expander("Research conclusions and next steps", expanded=False):
        st.markdown(
            "**Observed:** The higher-score group had a 50.0% negative-reaction "
            "rate (11/22), compared with 59.5% (22/37) for the lower-score group. "
            "This is opposite to the initial hypothesis.\n\n"
            "**Not established:** Forecast accuracy, statistical significance, "
            "causality, or investable performance.\n\n"
            "**Next research priorities:** Verify release timestamps and event windows; "
            "test features separately; obtain historical point-in-time expectation "
            "variables; evaluate rolling chronological holdouts."
        )

    with st.expander("Explore the full interactive dataset (optional)", expanded=False):
        st.write(
            "Upload your own compatible v0.8 research CSV to access the "
            "company filters, scatter plots, detailed correlations and downloadable tables. "
            "The published summary above is available without an upload."
        )
        uploaded = st.file_uploader(
            "Upload v0.8 research CSV", type=["csv"], key="efi_v1_csv"
        )
    if uploaded is None:
        st.caption("Expectations Fragility Lab · Independent educational research · v1.0")
        return
    try:
        df = _load(uploaded)
    except Exception as exc:
        st.error(f"Could not read research CSV: {exc}")
        return
    if df.empty:
        st.warning("No valid observations in the uploaded file.")
        return
    all_tickers = sorted(df["ticker"].unique())
    selected = st.multiselect("Research universe", all_tickers, default=all_tickers, key="efi_v1_universe")
    if not selected:
        st.warning("Select at least one company.")
        return
    data = df[df["ticker"].isin(selected)].copy()
    dates = (data["announcement_date"].min().date(), data["announcement_date"].max().date())
    c1, c2 = st.columns(2)
    with c1:
        sample = st.selectbox("Evaluation period", ["All observations", "Training", "Later holdout"], key="efi_v1_split")
    with c2:
        limit = st.checkbox("Exclude absolute EPS surprises over 100%", value=False, key="efi_v1_outliers")
    if sample != "All observations":
        data = data[data["split"].eq("training" if sample == "Training" else "holdout")]
    if limit:
        data = data[data["earnings_surprise_pct"].abs() <= 100]
    if data.empty:
        st.warning("No events match the filters.")
        return
    beats = data[data["earnings_surprise_pct"] > 0]
    misses = data[data["earnings_surprise_pct"] < 0]
    a, b, c, d = st.columns(4)
    a.metric("Historical events", f"{len(data)}")
    b.metric("Companies", f"{data['ticker'].nunique()}")
    c.metric("Beat + negative return", f"{_percentage(beats['abnormal_return_pct'] < 0):.1f}%" if len(beats) else "N/A")
    d.metric("Mean abnormal return", _fmt(data["abnormal_return_pct"].mean()))
    st.caption(f"Selected sample: {data['announcement_date'].min():%d %b %Y} – {data['announcement_date'].max():%d %b %Y}. "
               "Abnormal returns = stock window return − SPY window return; window dates are provisional.")

    tab1, tab2, tab3, tab4 = st.tabs(["Research findings", "Company comparison", "EFI prototype", "Methodology & limitations"])
    with tab1:
        st.subheader("The earnings paradox")
        x, y = st.columns(2)
        x.metric("EPS beats with negative return", f"{int((beats['abnormal_return_pct'] < 0).sum())} / {len(beats)}")
        y.metric("EPS misses with negative return", f"{int((misses['abnormal_return_pct'] < 0).sum())} / {len(misses)}")
        st.scatter_chart(data, x="earnings_surprise_pct", y="abnormal_return_pct", color="ticker")
        clean = data[["earnings_surprise_pct", "abnormal_return_pct"]].dropna()
        if len(clean) >= 3 and clean.nunique().min() > 1:
            p, s = st.columns(2)
            p.metric("Pearson", f"{clean.corr(method='pearson').iloc[0,1]:+.3f}")
            s.metric("Spearman", f"{clean.corr(method='spearman').iloc[0,1]:+.3f}")
        st.caption("Correlations are descriptive. Earnings surprise is observed after the event and is not a pre-event EFI input.")
    with tab2:
        st.subheader("Cross-sectional overview")
        rows = []
        for ticker, grp in data.groupby("ticker"):
            beat_grp = grp[grp["earnings_surprise_pct"] > 0]
            rows.append({"Ticker": ticker, "Events": len(grp),
                         "Mean return (%)": grp["abnormal_return_pct"].mean(),
                         "Median return (%)": grp["abnormal_return_pct"].median(),
                         "Negative events (%)": _percentage(grp["abnormal_return_pct"] < 0),
                         "Beats with negative return (%)": _percentage(beat_grp["abnormal_return_pct"] < 0)})
        st.dataframe(pd.DataFrame(rows).round(2), hide_index=True, use_container_width=True)
        st.caption("Small company samples and shared market regimes limit comparisons.")
    with tab3:
        st.subheader("Does the exploratory score separate negative reactions?")
        st.caption("Use 'Later holdout' above for the cleanest descriptive comparison. "
                   "The 50/50 weights are hypothetical and were not optimized on holdout outcomes.")
        group_data = data.copy()
        # A precomputed group in the exported holdout preserves the training-derived cutoff.
        if "group" in group_data and group_data["group"].notna().any():
            group_data = group_data[group_data["group"].notna()].copy()
            group_data["Score group"] = group_data["group"].astype(str)
        else:
            st.info("High/low groups are available in the exported holdout rows. "
                    "Select 'Later holdout' to inspect them without re-estimating a threshold.")
            group_data = group_data.iloc[0:0]
        if not group_data.empty:
            summary = group_data.groupby("Score group").agg(
                Events=("abnormal_return_pct", "size"),
                Negative_rate=("abnormal_return_pct", lambda x: _percentage(x < 0)),
                Mean_return=("abnormal_return_pct", "mean"),
                Median_return=("abnormal_return_pct", "median")
            ).reset_index().rename(columns={"Negative_rate": "Negative returns (%)",
                                          "Mean_return": "Mean abnormal return (%)",
                                          "Median_return": "Median abnormal return (%)"})
            st.dataframe(summary.round(2), hide_index=True, use_container_width=True)
        st.scatter_chart(data, x="prototype_fragility_score", y="abnormal_return_pct", color="ticker")
        st.write("**Feature correlations with abnormal return**")
        feat = data[["momentum_20d_pct", "downside_rms_60d_pp", "prototype_fragility_score", "abnormal_return_pct"]]
        st.dataframe(pd.DataFrame({"Feature": ["20-session momentum", "60-session downside RMS", "Prototype EFI"],
            "Pearson": [feat[x].corr(feat["abnormal_return_pct"]) for x in feat.columns[:-1]],
            "Spearman": [feat[x].corr(feat["abnormal_return_pct"], method="spearman") for x in feat.columns[:-1]]}).round(3),
            hide_index=True, use_container_width=True)
    with tab4:
        st.markdown("""**Research design**

- **Universe:** AAPL, NVDA, MSFT, TSLA, AMZN (subject to selected filters).
- **Earnings data:** quarterly EPS estimates, actual EPS and surprise percentages retrieved from Alpha Vantage.
- **Market data:** Yahoo Finance adjusted daily closing prices, benchmarked against SPY.
- **Pre-event features:** 20-session price momentum and 60-session downside RMS, calculated using closes strictly before the reported announcement date.
- **Prototype score:** equal-weight percentile ranks, referenced to the original training sample.
- **Validation:** chronological 70/30 training/holdout split, not independent external validation.

**Limitations:** earnings release times are not verified; broad return windows may include unrelated news; adjusted returns are not pure announcement reactions. The five stocks are a selected convenience sample, event observations are dependent, and feature weights are unvalidated. No trading costs, risk-adjusted portfolio performance, or live forecasting have been tested. Historical estimate availability and data-provider licensing should be reviewed before redistribution.

**Interpretation:** the current score has not demonstrated predictive power. The project documents a testable hypothesis and a reproducible exploratory workflow rather than a successful trading strategy.
""")
        st.download_button("Download filtered research observations", data.to_csv(index=False).encode(),
                           file_name="efi_v1_filtered_research.csv", mime="text/csv", key="efi_v1_download")
    st.caption("Expectations Fragility Lab · Independent educational research · v1.0")
