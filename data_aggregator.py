#################################
#    Creates and maintains
#   a .csv file with all
#   data used in the algo
#################################

from config import *
import pandas as pd
import numpy as np
import ta
import requests
from os import remove
import datetime

def get_prices(start, end):
    """
    Fetches the prices of whatever securities we have specified in the config.py file

    start/end: (str) YYYY-MM-DD of the range considered, imported from config.py
    returns a pandas.DataFrame with prices
    """

    tickers = TICKERS  # fetch tickers from config.py
    df_final = pd.DataFrame()  # declared for merging purposes (inside loops)

    for ticker in tickers:  # Loop over tickers to fetch individual price series

        r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + ticker
                         + "&outputsize=full&apikey=" + ALPHAVANTAGE_KEY)
        r_dict = r.json()

        dates = np.array([])  # this loop makes the index into an index of datetime objects. Note the format.
        for i in r_dict['Time Series (Daily)'].keys():
            datetime_obj = datetime.datetime.strptime(i, '%Y-%m-%d')
            dates = np.append(dates, datetime_obj)

        prices = np.array([])  # This loop extracts all prices and put them into an array
        for i in r_dict['Time Series (Daily)']:
            x = r_dict['Time Series (Daily)'][i]['5. adjusted close']
            prices = np.append(prices, x)

        open_prices = np.array([])  # grab opening prices as well
        for i in r_dict['Time Series (Daily)']:
            x = r_dict['Time Series (Daily)'][i]['1. open']
            open_prices = np.append(open_prices, x)

        df = pd.DataFrame({  # This dataframe contains each individual stock
            'Date': dates,
            str(ticker + '_' + 'adjclose'): prices,
            str(ticker + '_' + 'open'): open_prices
        })
        df = df.set_index('Date')

        df_final = pd.DataFrame(data=df_final,
                                index=dates)  # these few lines are for merging the individual dataframes
        df_final.index.name = 'Date'
        df_final = df.merge(df_final, left_index=True, right_index=True)

    for ticker in tickers:  # convert to numeric values. Prices are just "objects"
        df_final[str(ticker + '_' + 'adjclose')] = pd.to_numeric(df_final[str(ticker + '_' + 'adjclose')])
        df_final[str(ticker + '_' + 'open')] = pd.to_numeric(df_final[str(ticker + '_' + 'open')])

    df_final = df_final.iloc[::-1]

    return df_final[start: end]  # slice the dataframe at the end, only return the specified date-range.


def compute_returns(data):
    """
    Computes the daily returns and trailing returns over 10 days, the latter of which is used to compute the label
    we want to predict with our ML model.

    data: pandas.DataFrame containing prices from get_prices()
    returns a pandas.DataFrame with returns
    """

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


def compute_indicators(data):

    """
    Computes the MACD and RSI indicator on OPENING prices for each of the two ETFs

    data: pandas.DataFrame with (opening) prices of the securities we want to trade
    returns a pandas.DataFrame with MACD and RSI indicators computed
    """
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
    """
    Fetches VIX opening values, used to train the ML model

    returns a pandas.DataFrame with VIX data
    """

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


def update_data():
    """
    Calls the above functions and merges data to create the final dataframe used.
    It writes said dataframe to a .csv file and returns nothing.
    This function is to be called in main.py to keep the data up-to-date
    """
    etf_prices = get_prices(start=START_DATE, end=END_DATE)
    etf_returns = compute_returns(etf_prices)
    merged_etf_data = etf_prices.merge(etf_returns, right_index=True, left_index=True)
    indicators = compute_indicators(merged_etf_data)  # this uses the "ta" lib, but it does not need
    # to be imported
    merged_etf_data = merged_etf_data.merge(indicators, right_index=True, left_index=True)
    vix_data = get_vix()
    data = merged_etf_data.merge(vix_data, right_index=True, left_index=True)
    data.to_csv('Data/database.csv')
    return
