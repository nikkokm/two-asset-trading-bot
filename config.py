##############################################
#           Global Vars Needed, yo
#
##############################################

import datetime

ALPACA_SECRET_KEY = 'KKxtjwMdDvRYoYx6mixm6DFhKwweRalmAbNzlkVA'
ALPACA_KEY_ID = 'PK63GXZC77ZKHP9MX3BN'
ALPACA_ENDPOINT = 'https://paper-api.alpaca.markets'

ALPHAVANTAGE_KEY = 'AX9L41Q11KV9IDD9'

# start and end data for data
START_DATE = '2013-01-18'
TODAY = datetime.date.today()
END_DATE = TODAY - datetime.timedelta(days=1)
END_DATE = END_DATE.strftime('%Y-%m-%d')
TODAY = TODAY.strftime('%Y-%m-%d')

# Keep tickers of the investable universe in here
#TICKERS = ['PDP', 'VTV']
TICKERS = ['MTUM', 'VTV']


