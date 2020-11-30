############################
# This script fetches
#  the features used to
#  predict the label on
#      opening bell.
############################

from data_aggregator import get_vix, compute_indicators  # to compute features on opening prices
import pandas as pd
import numpy as np
from config import *
import alpaca_trade_api as tradeapi

labels = [i + '_open' for i in TICKERS]

def get_features():
    """
    This function computes the indicators on the opening prices, on the day that we initiate a trade.
    returns numpy.array that is fed into get_trade() in main.py
    """

    api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET_KEY, ALPACA_ENDPOINT)
    barset = api.get_barset(TICKERS, 'day', limit=1, start=TODAY, end=TODAY)

    opening_prices = np.array([])
    for i in TICKERS:
        opening_prices = np.append(opening_prices, barset[i][0].o)

    df = pd.read_csv('Data/database.csv', index_col='Date')
    df = df[labels]
    df = df.iloc[round(len(df)*0.75):]  # shorten the df just because
    df.loc[TODAY] = opening_prices

    features = compute_indicators(df)
    features = features.iloc[-1].values

    vix_today = get_vix()
    vix_today = vix_today['VIX_open'].values[-1]

    features = np.append(features, vix_today)

