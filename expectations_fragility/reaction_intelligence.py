"""Descriptive analytics for provisional earnings-event returns (not investment signals)."""
import numpy as np
import pandas as pd
import streamlit as st

REQUIRED = {"ticker", "announcement_date", "earnings_surprise_pct", "abnormal_return_pct"}


def render_reaction_intelligence(data: pd.DataFrame) -> None:
    missing = REQUIRED - set(data.columns)
    if missing:
        st.error(f"Missing dataset columns: {', '.join(sorted(missing))}")
        return

    df = data.copy()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df["announcement_date"] = pd.to_datetime(df["announcement_date"], errors="coerce")
    for field in ["earnings_surprise_pct", "abnormal_return_pct"]:
        df[field] = pd.to_numeric(df[field], errors="coerce")
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=list(REQUIRED))
    if df.empty:
        st.warning("No valid observations available.")
        return

    st.subheader("Earnings Reaction Intelligence · v0.7")
    st.caption("Descriptive research on provisional event windows. No causal or predictive claims.")

    options = sorted(df["ticker"].unique().tolist())
    selected = st.multiselect("Companies", options, default=options, key="eri_companies")
    if not selected:
        st.info("Select at least one company.")
        return

    earliest, latest = df["announcement_date"].min().date(), df["announcement_date"].max().date()
    date_range = st.date_input("Announcement dates", value=(earliest, latest),
                               min_value=earliest, max_value=latest, key="eri_dates")
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.info("Choose a start and end date.")
        return
    start, end = date_range
    category = st.selectbox("EPS surprise category", ["All", "Beats (> 0)", "Misses (< 0)", "Exact matches (= 0)"], key="eri_category")
    cap = st.checkbox("Exclude extreme EPS surprises", value=False, key="eri_cap_enabled")
    max_surprise = st.number_input("Maximum absolute EPS surprise (%)", min_value=1.0,
                                  value=100.0, step=25.0, disabled=not cap, key="eri_cap_value")

    view = df.loc[df["ticker"].isin(selected) &
                  df["announcement_date"].dt.date.between(start, end)].copy()
    if category == "Beats (> 0)":
        view = view.loc[view["earnings_surprise_pct"] > 0]
    elif category == "Misses (< 0)":
        view = view.loc[view["earnings_surprise_pct"] < 0]
    elif category == "Exact matches (= 0)":
        view = view.loc[view["earnings_surprise_pct"] == 0]
    if cap:
        view = view.loc[view["earnings_surprise_pct"].abs() <= max_surprise]
    if view.empty:
        st.info("No observations match these filters.")
        return

    beats = view.loc[view["earnings_surprise_pct"] > 0]
    misses = view.loc[view["earnings_surprise_pct"] < 0]
    paradox_count = int((beats["abnormal_return_pct"] < 0).sum())
    paradox_rate = 100 * paradox_count / len(beats) if len(beats) else np.nan
    miss_negative = 100 * (misses["abnormal_return_pct"] < 0).mean() if len(misses) else np.nan
    cols = st.columns(4)
    cols[0].metric("Events", len(view))
    cols[1].metric("EPS beats", len(beats))
    cols[2].metric("Beat + negative return", f"{paradox_rate:.1f}%" if len(beats) else "N/A")
    cols[3].metric("Miss + negative return", f"{miss_negative:.1f}%" if len(misses) else "N/A")
    st.caption(f"Beat/negative return: {paradox_count}/{len(beats)}. Strictly negative means < 0%; zero returns are not counted as negative.")

    def summarize(group: pd.DataFrame) -> pd.Series:
        positive = group.loc[group["earnings_surprise_pct"] > 0]
        negative = group.loc[group["earnings_surprise_pct"] < 0]
        return pd.Series({
            "Events": len(group),
            "EPS beats": len(positive),
            "EPS misses": len(negative),
            "Mean abnormal return (%)": group["abnormal_return_pct"].mean(),
            "Median abnormal return (%)": group["abnormal_return_pct"].median(),
            "Return std. dev. (pp)": group["abnormal_return_pct"].std(),
            "Beats with negative return (%)": 100 * (positive["abnormal_return_pct"] < 0).mean() if len(positive) else np.nan,
        })

    st.markdown("#### Company comparison")
    summary = pd.DataFrame([{"ticker": ticker, **summarize(group).to_dict()}
                            for ticker, group in view.groupby("ticker")])
    st.dataframe(summary.style.format(precision=2, na_rep="N/A"), use_container_width=True, hide_index=True)

    st.markdown("#### Earnings surprise vs. market-adjusted return")
    st.scatter_chart(view, x="earnings_surprise_pct", y="abnormal_return_pct", color="ticker")

    st.markdown("#### Statistical diagnostics")
    if len(view) >= 3 and view["earnings_surprise_pct"].nunique() > 1 and view["abnormal_return_pct"].nunique() > 1:
        pearson = view["earnings_surprise_pct"].corr(view["abnormal_return_pct"], method="pearson")
        spearman = view["earnings_surprise_pct"].corr(view["abnormal_return_pct"], method="spearman")
        c1, c2 = st.columns(2)
        c1.metric("Pearson correlation", f"{pearson:+.3f}")
        c2.metric("Spearman rank correlation", f"{spearman:+.3f}")
        st.caption("Correlations describe association, not causation, forecasting power, or statistical significance. Observations may be dependent.")
    else:
        st.info("Insufficient variation or observations to compute correlations.")

    st.markdown("#### Inspect and export observations")
    st.dataframe(view.sort_values("announcement_date", ascending=False),
                 use_container_width=True, hide_index=True)
    st.download_button("Download filtered research CSV", view.to_csv(index=False),
                       file_name="efi_v07_filtered_events.csv", mime="text/csv")
    st.warning("Event windows are provisional and may include unrelated news. Release times are unverified; results are not causal earnings reactions. Adjusted daily prices, benchmark choice, outliers, repeated observations, and data provenance need further validation.")
