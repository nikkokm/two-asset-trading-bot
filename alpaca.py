import alpaca_trade_api as tradeapi
from config import *
import datetime
from pytz import timezone


api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET_KEY, ALPACA_ENDPOINT)




