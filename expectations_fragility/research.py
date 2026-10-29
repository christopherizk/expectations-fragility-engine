import numpy as np
import pandas as pd

FEATURES = ['valuation_pressure', 'forecast_dispersion', 'pre_event_momentum', 'historical_downside_sensitivity']
REQUIRED = ['ticker','announcement_date','earnings_surprise_pct','abnormal_return_pct',*FEATURES]

def validate(df):
    missing = [c for c in REQUIRED if c not in df]
    if missing: raise ValueError('Missing columns: '+', '.join(missing))
    d = df.copy()
    d['announcement_date'] = pd.to_datetime(d['announcement_date'], errors='coerce')
    for c in REQUIRED[2:]: d[c] = pd.to_numeric(d[c], errors='coerce')
    d = d.dropna(subset=REQUIRED).sort_values('announcement_date')
    if not len(d): raise ValueError('No complete rows remain after validation.')
    if not all(d[c].between(0,100).all() for c in FEATURES):
        raise ValueError('EFI feature columns must be between 0 and 100. These must be point-in-time pre-event scores.')
    return d

def evaluate(df):
    d = validate(df)
    d = d[d.earnings_surprise_pct < 0].copy()
    if len(d) < 40: raise ValueError('Need at least 40 complete negative-surprise events for this preliminary diagnostic.')
    d['downside_pct'] = np.maximum(0, -d['abnormal_return_pct'])
    n_train = int(len(d)*.7)
    train, test = d.iloc[:n_train], d.iloc[n_train:]
    # Fixed illustrative EFI is a hypothesis, not trained on outcomes.
    weights = np.array([.30,.20,.15,.35])
    d['efi'] = d[FEATURES].to_numpy() @ weights
    train, test = d.iloc[:n_train], d.iloc[n_train:]
    y_train = train.downside_pct.to_numpy(); y_test = test.downside_pct.to_numpy()
    def fit_predict(cols):
        x = np.column_stack([np.ones(len(train)), train[cols].to_numpy()])
        xt = np.column_stack([np.ones(len(test)), test[cols].to_numpy()])
        coef = np.linalg.lstsq(x, y_train, rcond=None)[0]
        return xt @ coef
    models = {
        'Training-period mean': np.full(len(test), y_train.mean()),
        'Valuation-only model': fit_predict(['valuation_pressure']),
        'Fixed EFI model': fit_predict(['efi']),
        'Four-feature linear model': fit_predict(FEATURES),
    }
    results = pd.DataFrame([{'Model':k, 'Holdout MAE (pp)':np.mean(np.abs(y_test-v)), 'Holdout RMSE (pp)':np.sqrt(np.mean((y_test-v)**2))} for k,v in models.items()])
    out = test[['ticker','announcement_date','earnings_surprise_pct','abnormal_return_pct','downside_pct','efi']].copy()
    for k,v in models.items(): out[k+' prediction'] = v
    return results, out, {'all_events':len(df),'negative_surprises':len(d),'training':len(train),'holdout':len(test),'holdout_start':str(test.announcement_date.min().date())}
