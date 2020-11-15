import alpaca_trade_api as tradeapi
from config import *

api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET_KEY, ALPACA_ENDPOINT)


asset = api.get_asset('PTF')
print(asset.shortable)
