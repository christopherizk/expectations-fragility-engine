
"""Exploratory earnings-event market reaction analysis."""

import pandas as pd
import requests
import streamlit as st

BASE = "https://www.alphavantage.co/query"


@st.cache_data(ttl=86400, show_spinner=False)
def daily_prices(ticker: str, _api_key: str) -> pd.DataFrame:
    """Retrieve available daily prices from Alpha Vantage."""
    response = requests.get(
        BASE,
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker,
            "outputsize": "compact",
            "apikey": _api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    if "Note" in payload or "Information" in payload:
        raise RuntimeError(
            f"{ticker}: API limit or plan restriction."
        )

    series = payload.get("Time Series (Daily)")
    if not series:
        raise ValueError(
            f"{ticker}: daily price data unavailable."
        )

    frame = pd.DataFrame.from_dict(
        series, orient="index"
    )

    frame.index = pd.to_datetime(frame.index)
    frame.index.name = "date"

    frame["close"] = pd.to_numeric(
        frame["4. close"], errors="coerce"
    )

    return (
        frame[["close"]]
        .dropna()
        .sort_index()
    )


def build_event_study(
    earnings_data: pd.DataFrame,
    stock_prices: pd.DataFrame,
    benchmark_prices: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Calculate indicative close-to-close event returns.

    This is not a timestamp-verified earnings reaction.
    """

    events = earnings_data.copy()
    events["reportedDate"] = pd.to_datetime(
        events["reportedDate"], errors="coerce"
    )

    stock = stock_prices["close"].rename("stock_close")
    benchmark = benchmark_prices["close"].rename("spy_close")

    prices = pd.concat(
        [stock, benchmark], axis=1, join="inner"
    ).dropna().sort_index()

    prices["stock_return_pct"] = (
        prices["stock_close"].pct_change() * 100
    )
    prices["market_return_pct"] = (
        prices["spy_close"].pct_change() * 100
    )

    prices["abnormal_return_pct"] = (
        prices["stock_return_pct"]
        - prices["market_return_pct"]
    )

    records = []

    for _, event in events.iterrows():
        announcement = event["reportedDate"]

        if pd.isna(announcement):
            continue

        # The next trading day is a provisional event
        # window, not a verified earnings-reaction window.
        eligible = prices.index[
            prices.index > announcement
        ]

        if len(eligible) == 0:
            continue

        event_day = eligible[0]

        if (event_day - announcement).days > 5:
            continue

        observation = prices.loc[event_day]

        if pd.isna(observation["abnormal_return_pct"]):
            continue

        records.append({
            "ticker": ticker,
            "announcement_date": announcement,
            "proxy_reaction_date": event_day,
            "earnings_surprise_pct": event.get(
                "surprisePercentage"
            ),
            "stock_return_pct": observation[
                "stock_return_pct"
            ],
            "market_return_pct": observation[
                "market_return_pct"
            ],
            "abnormal_return_pct": observation[
                "abnormal_return_pct"
            ],
        })

    return pd.DataFrame(records)
