# Two Assets Trading Bot
Inspired by Value and Momentum Everywhere (2013), although value and momentum ETF returns do not correlate negatively.

### Setup
Just clone the repo to a server with Python installed and 
run [main.py](main.py) after filling in the API keys and Alpaca
API endpoint in [config.py](config.py)

##### Packages Required
- pandas
- numpy
- requests
- sklean
- alpaca_trade_api
- ta

### How it Works
First and foremost, an AlphaVantage API key is needed as well as API keys to perform paper 
trading through Alpaca

##### Data
Data is updated and stored in [Data/databse.csv](Data/databse.csv) 
every day. Price data is pulled from AlphaVantage and VIX data
is pulled from the CBOE website. 

##### Trading Logic
I define a simple trading rule and codify it in a dummy variable:
>If for today, the 10-day cumulative return for the momentum ETF is 
>greater  than the 
>10-day cumulative return of the value ETF we go long momentum and short 
>value and vice versa.

If we go long in momentum and short in value, the label takes the value
of 1, otherwise it is 0.

The 10-day trailing return is computed from (adjusted) closing prices, 
such that every day the label indicates which ETF is currently
outperforming which

I then compute MACD and RSI indicators on opening prices for both ETFs 
and those, along with the opening values of the VIX are the features
used in a logistic regression.

Every day at market open, the algorithm fetches the opening value for VIX
and the MACD & RSI values for both ETFs (based on opening prices) and
these are fed into the model estimated on data in  [Data/databse.csv](Data/databse.csv).

The binary classification/prediction dictates the trade we do on that day
and the probability estimate of the model is rescaled to function
as the percentage of capital to devote to this trade.


