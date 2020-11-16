##############################################
#           Global Vars Needed
##############################################

import datetime

#API Keys needed
ALPACA_SECRET_KEY = 'jwYb6J3JzWqFjJeDkzkAjzqbsUbzCa4OXhGV9Sbk'
ALPACA_KEY_ID = 'PKWG2JNVN30BZJX3ONT0'
ALPACA_ENDPOINT = 'https://paper-api.alpaca.markets'
ALPHAVANTAGE_KEY = 'AX9L41Q11KV9IDD9'

# start and end data for data
START_DATE = '2013-01-18'
TODAY = datetime.date.today()
END_DATE = TODAY - datetime.timedelta(days=1)
END_DATE = END_DATE.strftime('%Y-%m-%d')
TODAY = TODAY.strftime('%Y-%m-%d')

# We trade a momentum and a value ETF
TICKERS = ['MTUM', 'VTV']


