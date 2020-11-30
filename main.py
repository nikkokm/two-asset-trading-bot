#######################
#   Main script
#
#######################

from config import *
import pandas as pd
import train_model
from features import get_features
import data_aggregator
import alpaca_trade_api as tradeapi
from pytz import timezone
import datetime
import time


def get_trade():
    """
    This function gets the predicted trade for today and the relative capital amount to trade
    returns the prediction (what to go long/short in for today) and how much capital to spend
    """
    df = pd.read_csv("Data/database.csv", index_col='Date')
    df = train_model.compute_label(df=df)
    features = get_features()
    prediction, weight = train_model.fit_model(df=df, data=features)
    return prediction, weight


def trade(prediction, weight):
    """
    This function executes the trades as per prediction and weight from get_trade()
    """
    account = api.get_account()
    cash = float(account.cash)
    cash_to_spend = cash * weight

    if prediction == 1:  # we buy MTUM if we predicted a 1

        mtum_quote = api.get_last_quote('MTUM')
        qty_to_buy = int(cash_to_spend / float(mtum_quote.askprice))

        vtv_quote = api.get_last_quote('VTV')
        qty_to_sell = int(cash_to_spend / float(vtv_quote.bidprice))

        # this block makes sure we go long in MTUM
        try:  # we check if we already have a MTUM position:
            pos = api.get_position(symbol='MTUM')
            current_qty = int(pos.qty)  # our existing position

            if pos.side == 'short':  # if we are short, we close the short and go long
                current_qty = current_qty * (-1)
                api.submit_order(symbol='MTUM', qty=current_qty + qty_to_buy, side='buy', type='market',
                                 time_in_force='day')

            else:  # if we are already long, we do nothing OR we scale up/down our position according to "weight" (?)
                pass

        except:  # if we get an error, we do not have MTUM and will therefore go long
            api.submit_order(symbol='MTUM', qty=qty_to_buy, side='buy', type='market', time_in_force='day')

        # this block makes sure we short VTV
        try:
            pos = api.get_position(symbol='VTV')
            current_qty = int(pos.qty)

            if pos.side == 'long':  # if we are long VTV we close it and go short
                api.submit_order(symbol='VTV', qty=current_qty + qty_to_sell, side='sell', type='market',
                                 time_in_force='day')

            else:  # if we are already short, we do nothing OR re-scale our position
                pass

        except:  # if we do not have a VTV position, we go short
            api.submit_order(symbol='VTV', qty=qty_to_sell, side='sell', type='market', time_in_force='day')

        return


    elif prediction == 0:  # we buy VTV if we predicted a 0

        mtum_quote = api.get_last_quote('MTUM')
        qty_to_sell = int(cash_to_spend / float(mtum_quote.bidprice))

        vtv_quote = api.get_last_quote('VTV')
        qty_to_buy = int(cash_to_spend / float(vtv_quote.askprice))

        # this block makes sure we are long VTV
        try:
            pos = api.get_position(symbol='VTV')
            current_qty = int(pos.qty)

            if pos.side == 'short':  # if we are short, close it and go long
                current_qty = current_qty * (-1)
                api.submit_order(symbol='VTV', qty=current_qty + qty_to_buy, side='buy', type='market',
                                 time_in_force='day')

            else:  # we are already long, so we do nothing or we re-scale
                pass

        except:  # we do not have a VTV position so we go long
            api.submit_order(symbol='VTV', qty=qty_to_buy, side='buy', type='market', time_in_force='day')

        # this block makes sure we are short MTUM
        try:
            pos = api.get_position(symbol='MTUM')
            current_qty = int(pos.qty)

            if pos.side == 'long':  # if we are already long PDP, we close it and go short
                api.submit_order(symbol='MTUM', qty=current_qty + qty_to_sell, side='sell', type='market',
                                 time_in_force='day')

            else:  # if we are already short, we do nothing or we re-scale the position
                pass

        except:  # if we do not have a MTUM position, we go short
            api.submit_order(symbol='MTUM', qty=qty_to_sell, side='sell', type='market', time_in_force='day')

        return


def check_trade_history():
    """
    Check if we have submitted an order that was filled, today. if so, return True, else return False
    """
    today = datetime.date.today()
    lower = today - datetime.timedelta(days=1)
    upper = today + datetime.timedelta(days=1)

    orders = api.list_orders(status='all', after=lower, until=upper)

    if not orders:  # if we have not traded today, the orders object is an empty list
        return False
    else:
        return True


def is_market_open():
    """
    Checks if the market is open today. Returns True if so, otherwise it returns False.
    Evaluated against NYC time. i.e. when it is 1 AM on a Monday in Europe, the function returns False,
    as it is Sunday in NYC.
    Note that the function only accounts for date, not time. i.e. 6 AM on Tuesday, NYC time returns True
    """

    nyc = timezone('America/New_York')
    today_us_time = datetime.datetime.today().astimezone(nyc)
    today_us_str = today_us_time.strftime('%Y-%m-%d')
    calendar = api.get_calendar(start=today_us_str, end=today_us_str)[0]
    open_date = calendar.date.strftime('%Y-%m-%d')

    if open_date == today_us_str:
        return True
    else:
        return False


api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET_KEY, ALPACA_ENDPOINT)

#This block of code is to for running the algo non-stop
while True:
    trading_day_today = is_market_open()

    if trading_day_today is False:
        time.sleep(1800)  # wait 30 minutes
        continue  # go back and check if now, 30 minutes later, we are in a trading day (from the POV of NYC)

    else:
        traded_today = check_trade_history()

        if traded_today is True:
            time.sleep(1800)  # wait 30 minutes
            continue  # go back to top of loop

        else:

            clock = api.get_clock()
            if clock.is_open is False:  # Today is a trading day, we did not trade yet and the market is closed.
                time.sleep(30)  # wait only 30 seconds if we have not traded yet
                continue

            else:  # Today is a trading day, we did not trade yet, the market is open.
                data_aggregator.update_data()  # update the CSV with most recent data
                df = pd.read_csv('Data/database.csv', index_col='Date')
                df = train_model.compute_label(df=df)
                pred, weight = get_trade()
                trade(prediction=pred, weight=weight)
                print('Trade Executed...')
                time.sleep(7200)  # wait 20 hours before resuming while loop
                continue
