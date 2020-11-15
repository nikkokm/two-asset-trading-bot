##############################
#      Fetches ETF
# price data and return data
#
##############################

import requests
import pandas as pd
import numpy as np
import datetime
from config import *


def get_prices(start, end):
    """

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
