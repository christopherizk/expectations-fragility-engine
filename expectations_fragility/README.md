# Expectations Fragility Lab

A functional **scenario exploration prototype**, not a validated stock predictor. No market data is fetched yet. The EFI inputs are manually entered, weights are illustrative, and the earnings-response formula is arbitrary. Never interpret its output as an empirical return estimate.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Research hypothesis

Do pre-announcement valuation expectations, analyst forecast dispersion, momentum, and historical downside sensitivity help explain *abnormal returns conditional on negative earnings surprises*, beyond volatility, sector, and valuation baselines?

## Proposed rigorous design

- Obtain point-in-time consensus estimates and earnings announcement dates with exact publication times; align returns to after-hours vs regular-session events.
- Measure surprises relative to pre-announcement expectations; define sector- and market-adjusted event returns over multiple windows.
- Avoid look-ahead bias and survivorship bias; keep delisted firms and vintage fundamentals where possible.
- Train on earlier dates, validate on later dates, and compare against sector, size, volatility, and simple valuation benchmarks.
- Quantify predictive uncertainty, test sensitivity to outliers and weighting choices, and report negative results.

## Attribution

AI-assisted implementation; financial assumptions and empirical claims require independent review and validation.

## v0.2 — historical research workbench

The app now accepts a real event-level CSV and runs a **chronological 70/30 holdout** evaluation on negative earnings surprises. It compares a training mean, valuation-only linear model, fixed-weight EFI linear model, and four-feature linear model. It reports holdout MAE and RMSE, with predictions downloadable for inspection. No performance claims are made without data.

### CSV contract

`ticker,announcement_date,earnings_surprise_pct,abnormal_return_pct,valuation_pressure,forecast_dispersion,pre_event_momentum,historical_downside_sensitivity`

- One row per stock/earnings announcement; date in ISO `YYYY-MM-DD` format.
- `earnings_surprise_pct`: actual versus point-in-time consensus, percent; negative values indicate misses. Define treatment of zero/negative consensus earnings before collecting data.
- `abnormal_return_pct`: stock event-window return minus benchmark return, in percentage points, consistently aligned to announcement timestamps.
- Four component scores: 0–100, constructed **ex ante**, with methodology and normalization fixed using only past information.
- Do not backfill revised analyst consensus, use post-announcement information in features, or omit delisted companies without disclosure.
- Preliminary workbench requires 40+ negative-surprise events. Results are diagnostics only. No sector/size/volatility/surprise-magnitude controls or statistical uncertainty yet.

### Next research milestone

Build a licensed or otherwise legally accessible, point-in-time dataset with accurate earnings release timestamps, historical pre-release consensus, prices, and sector controls. Define features independently of the outcome; freeze specifications before running final holdout tests. Compare against a richer baseline with surprise magnitude, size, beta/volatility, sector, and date effects; report uncertainty and multiple-testing limitations.

## v0.3: Free Alpha Vantage earnings integration

1. Install Python 3.10+ and run `pip install -r requirements.txt`.
2. Run `streamlit run app.py` from the project folder.
3. Open the **Real earnings data** section. Enter a ticker and your Alpha Vantage key in the password field, then click **Fetch real earnings**.
4. Alternatively, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and replace the placeholder with your key. This private file is ignored by Git. On Streamlit Community Cloud, paste the key into the app's **Secrets** settings rather than into your repository.
5. Never share or commit your key. If you accidentally publish it, revoke/rotate it.

**Data limits:** Alpha Vantage's free plan may restrict EARNINGS access, calls, and coverage. This application reports provider errors rather than inventing data. The historical event-study workbench still requires a separately validated, point-in-time dataset; earnings EPS history alone is not sufficient. The EFI weights are experimental and the app makes no predictive-performance claims.

**Publication:** You can publish the source to GitHub and deploy the app publicly once you have tested it. A public deployment should use Streamlit Secrets and ideally cache/throttle data retrieval to protect API quotas. No deployment has been performed for you.
