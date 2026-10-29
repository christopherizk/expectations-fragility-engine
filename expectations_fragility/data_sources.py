"""Free-source data access. Never print, log, or persist API keys."""
import requests
import pandas as pd

BASE = 'https://www.alphavantage.co/query'

def earnings(ticker: str, api_key: str) -> pd.DataFrame:
    ticker = ticker.strip().upper()
    if not ticker or not api_key.strip():
        raise ValueError('Provide a ticker and an API key.')
    response = requests.get(BASE, params={'function':'EARNINGS','symbol':ticker,'apikey':api_key.strip()}, timeout=25)
    response.raise_for_status()
    payload = response.json()
    if 'Note' in payload or 'Information' in payload:
        raise RuntimeError('Alpha Vantage returned a rate-limit, plan-access, or information notice. Try again later or check your plan.')
    if 'Error Message' in payload:
        raise ValueError('Ticker not recognized by Alpha Vantage.')
    quarterly = payload.get('quarterlyEarnings')
    if not quarterly:
        raise ValueError('No quarterly earnings data returned for this ticker.')
    frame = pd.DataFrame(quarterly)
    for col in ('reportedEPS','estimatedEPS','surprise','surprisePercentage'):
        if col in frame:
            frame[col] = pd.to_numeric(frame[col].replace('None',pd.NA), errors='coerce')
    return frame
