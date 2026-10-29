
"""Exploratory multi-company earnings event study.

Price source: Yahoo Finance via yfinance.
Earnings source: Alpha Vantage (handled separately).

Returns are proxies, not timestamp-verified earnings reactions.
"""

import pandas as pd
import streamlit as st
import yfinance as yf


@st.cache_data(ttl=86400, show_spinner=False)
def daily_prices(ticker: str, _api_key: str = "") -> pd.DataFrame:
    """Retrieve approximately 10 years of adjusted daily prices.

    The optional _api_key preserves compatibility with the
    existing app.py call signature; it is not sent to Yahoo.
    """
    ticker = ticker.strip().upper()

    if not ticker:
        raise ValueError("A stock ticker is required.")

    data = yf.download(
        ticker,
        period="10y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

    if data is None or data.empty:
        raise ValueError(
            f"{ticker}: no historical price data available."
        )

    close = data["Close"]

    # yfinance versions may return MultiIndex columns.
    if isinstance(close, pd.DataFrame):
        if close.shape[1] != 1:
            raise ValueError(
                f"{ticker}: unexpected price data structure."
            )
        close = close.iloc[:, 0]

    frame = pd.DataFrame({
        "close": pd.to_numeric(close, errors="coerce")
    })

    frame.index = pd.to_datetime(frame.index)

    if frame.index.tz is not None:
        frame.index = frame.index.tz_localize(None)

    frame.index = frame.index.normalize()
    frame.index.name = "date"

    frame = (
        frame.dropna()
        .sort_index()
        .loc[lambda x: ~x.index.duplicated(keep="last")]
    )

    if len(frame) < 3:
        raise ValueError(
            f"{ticker}: insufficient daily price history."
        )

    return frame


def build_event_study(
    earnings_data: pd.DataFrame,
    stock_prices: pd.DataFrame,
    benchmark_prices: pd.DataFrame,
    ticker: str,
) -> pd.DataFrame:
    """Calculate two provisional event-window return measures.

    Same-day proxy:
        Previous close to announcement-date close, when
        the announcement date is a trading session.

    Next-day proxy:
        Previous close to the first trading-session close
        strictly after the announcement date.

    These are alternative windows, not verified reactions.
    """

    events = earnings_data.copy()

    events["reportedDate"] = pd.to_datetime(
        events["reportedDate"],
        errors="coerce",
    ).dt.normalize()

    stock = stock_prices["close"].rename("stock_close")
    spy = benchmark_prices["close"].rename("spy_close")

    prices = pd.concat(
        [stock, spy],
        axis=1,
        join="inner",
    ).dropna().sort_index()

    if len(prices) < 3:
        return pd.DataFrame()

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

        # Require a trading session on or after the
        # reported announcement date.
        positions = prices.index.searchsorted(
            announcement, side="left"
        )

        if positions >= len(prices):
            continue

        same_day_pos = positions

        # First trading session strictly after the date.
        next_day_pos = prices.index.searchsorted(
            announcement, side="right"
        )

        if next_day_pos >= len(prices):
            continue

        same_day = prices.index[same_day_pos]
        next_day = prices.index[next_day_pos]

        # Reject events outside the available price range.
        if announcement < prices.index[0]:
            continue

        if (same_day - announcement).days > 5:
            continue

        if (next_day - announcement).days > 7:
            continue

        # For the next-day proxy, use the close before
        # the announcement-date session when available.
        start_pos = same_day_pos - 1

        if start_pos < 0:
            continue

        start = prices.iloc[start_pos]
        end = prices.iloc[next_day_pos]

        stock_window_return = (
            end["stock_close"] / start["stock_close"] - 1
        ) * 100

        market_window_return = (
            end["spy_close"] / start["spy_close"] - 1
        ) * 100

        window_abnormal = (
            stock_window_return - market_window_return
        )

        same_day_abnormal = None

        if same_day == announcement:
            same_day_abnormal = prices.iloc[
                same_day_pos
            ]["abnormal_return_pct"]

        records.append({
            "ticker": ticker,
            "announcement_date": announcement,
            "proxy_reaction_date": next_day,
            "earnings_surprise_pct": event.get(
                "surprisePercentage"
            ),
            "stock_return_pct": stock_window_return,
            "market_return_pct": market_window_return,
            "abnormal_return_pct": window_abnormal,
            "same_day_abnormal_return_pct": (
                same_day_abnormal
            ),
            "window_start_close_date": (
                prices.index[start_pos]
            ),
            "window_end_close_date": next_day,
        })

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records).sort_values(
        "announcement_date"
    ).reset_index(drop=True)
