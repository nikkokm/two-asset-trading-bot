#################################
#    Creates and maintains
#   a .csv file with all
#   features used in the algo
#################################

from config import *
import pandas as pd
import numpy as np
import prices
import ta
import requests
from os import remove


def compute_returns(data):
    daily_return_labels = [i + '_daily_return' for i in TICKERS]
    trailing_return_labels = [i + '_trailing_return' for i in TICKERS]

    daily_return_data = pd.DataFrame(columns=daily_return_labels)
    trailing_return_data = pd.DataFrame(columns=trailing_return_labels)

    for i, j, z in zip(TICKERS, daily_return_labels, trailing_return_labels):
        daily_return_data[j] = np.log(data[str(i + '_' + 'adjclose')]) - np.log(data[str(i + '_' + 'adjclose')].shift(1))
        trailing_return_data[z] = np.log(data[str(i + '_' + 'adjclose')]) - np.log(data[str(i + '_' + 'adjclose')].shift(10))

    return_data = daily_return_data.merge(trailing_return_data, left_index=True, right_index=True)
    return_data.dropna(inplace=True)

    return return_data


def compute_indicators(data): # indicators are computed on the OPENING prices, not closing!
    #  the data arg is a DF with only (opening) prices of the securities we want to trade
    MACD_labels = [i + '_MACD' for i in TICKERS]
    MACD_signal_labels = [i + '_MACD_signal' for i in TICKERS]
    RSI_labels = [i + '_RSI' for i in TICKERS]

    MACD_frame = pd.DataFrame(columns=MACD_labels)
    MACD_signal_frame = pd.DataFrame(columns=MACD_signal_labels)
    RSI_frame = pd.DataFrame(columns=RSI_labels)

    for i, j, z, q in zip(MACD_labels, MACD_signal_labels, RSI_labels, TICKERS):
        MACD_frame[i] = ta.trend.MACD(data[str(q + '_' + 'open')], n_slow=26, n_fast=12, n_sign=9, fillna=True).macd()
        MACD_signal_frame[j] = ta.trend.MACD(data[str(q + '_' + 'open')], n_slow=26, n_fast=12, n_sign=9, fillna=True).macd_signal()
        RSI_frame[z] = ta.momentum.rsi(data[str(q + '_' + 'open')], n=14, fillna=True)

    merged_frame = MACD_frame.merge(MACD_signal_frame, left_index=True, right_index=True)
    merged_frame = merged_frame.merge(RSI_frame, left_index=True, right_index=True)

    return merged_frame


def get_vix():
    url = 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vixcurrent.csv'
    r = requests.get(url)
    f = open('vix.csv', 'wb')
    #open('vix.csv', 'wb').write(r.content)
    f.write(r.content)
    f.close()
    df = pd.read_csv('vix.csv', header=1)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.drop(['VIX Close', 'VIX High', 'VIX Low'], inplace=True, axis=1) # we only care about the closing value
    df.rename(columns={'VIX Open': 'VIX_open'}, inplace=True)
    remove('vix.csv')
    return df


etf_prices = prices.get_prices(start=START_DATE, end=END_DATE)  # fetch prices of the ETFs
etf_returns = compute_returns(etf_prices)  # compute the daily and trailing returns
merged_etf_data = etf_prices.merge(etf_returns, right_index=True, left_index=True)  # merge it together
indicators = compute_indicators(merged_etf_data)  # compute all indicators for our ETFs
merged_etf_data = merged_etf_data.merge(indicators, right_index=True,
                                        left_index=True)  # merge indicators with the ETF returns

vix_data = get_vix() # get vix data
data = merged_etf_data.merge(vix_data, right_index=True, left_index=True) # merge it all together on the index
data.to_csv('Data/database.csv') # write to a .csv file



