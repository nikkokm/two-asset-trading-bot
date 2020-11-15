#######################
#   Main algo, yo
#
#######################

from config import *
import pandas as pd
import train_model
from features import get_features
import data_aggregator
import alpaca_trade_api as tradeapi


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

    api = tradeapi.REST(ALPACA_KEY_ID, ALPACA_SECRET_KEY, ALPACA_ENDPOINT)
    account = api.get_account()
    cash = float(account.cash)
    cash_to_spend = cash*weight



    if prediction == 1:  # we buy PDP if we predicted a 1

        pdp_quote = api.get_last_quote('PDP')
        qty_to_buy = int(cash_to_spend/float(pdp_quote.askprice))

        vtv_quote = api.get_last_quote('VTV')
        qty_to_sell = int(cash_to_spend/float(vtv_quote.bidprice))

        # this block makes sure we go long in PDP
        try:  # we check if we already have a PDP position:
            pos = api.get_position(symbol='PDP')
            current_qty = int(pos.qty)  # our existing position

            if pos.side == 'short':  # if we are short, we close the short and go long
                current_qty = current_qty * (-1)
                api.submit_order(symbol='PDP', qty=current_qty+qty_to_buy, side='buy', type='market', time_in_force='day')

            else:  # if we are already long, we do nothing OR we scale up/down our position according to "weight" (?)
                pass

        except:  # if we get an error, we do not have PDP and will therefore go long
            api.submit_order(symbol='PDP', qty=qty_to_buy, side='buy', type='market', time_in_force='day')

        # this block makes sure we short VTV
        try:
            pos = api.get_position(symbol='VTV')
            current_qty = int(pos.qty)

            if pos.side == 'long':  # if we are long VTV we close it and go short
                api.submit_order(symbol='VTV', qty=current_qty+qty_to_sell, side='sell', type='market', time_in_force='day')

            else:  # if we are already short, we do nothing OR re-scale our position
                pass

        except:  # if we do not have a VTV position, we go short
            api.submit_order(symbol='VTV', qty=qty_to_sell, side='sell', type='market', time_in_force='day')

        return


    elif prediction == 0:  # we buy VTV if we predicted a 0

        pdp_quote = api.get_last_quote('PDP')
        qty_to_sell = int(cash_to_spend / float(pdp_quote.bidprice))

        vtv_quote = api.get_last_quote('VTV')
        qty_to_buy = int(cash_to_spend / float(vtv_quote.askprice))

        # this block makes sure we are long VTV
        try:
            pos = api.get_position(symbol='VTV')
            current_qty = int(pos.qty)

            if pos.side == 'short':  # if we are short, close it and go long
                current_qty = current_qty*(-1)
                api.submit_order(symbol='VTV', qty=current_qty+qty_to_buy, side='buy', type='market', time_in_force='day')

            else:  # we are already long, so we do nothing or we re-scale
                pass

        except:  # we do not have a VTV position so we go long
            api.submit_order(symbol='VTV', qty=qty_to_buy, side='buy', type='market', time_in_force='day')

        # this block makes sure we are short PDP
        try:
            pos = api.get_position(symbol='PDP')
            current_qty = int(pos.qty)

            if pos.side == 'long':  # if we are already long PDP, we close it and go short
                api.submit_order(symbol='PDP', qty=current_qty+qty_to_sell, side='sell', type='market', time_in_force='day')

            else:  # if we are already short, we do nothing or we re-scale the position
                pass

        except:  # if we do not have a PDP position, we go short
            api.submit_order(symbol='PDP', qty=qty_to_sell, side='sell', type='market', time_in_force='day')

        return

data_aggregator.update_data()

df = pd.read_csv('Data/database.csv', index_col='Date')
df = train_model.compute_label(df=df)

train_model.train_model_in_sample(df)
#pred, weight = get_trade()
#trade(pred, weight)
