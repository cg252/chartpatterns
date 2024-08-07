import yfinance as yf
import numpy as np
import pandas as pd
import talib

tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
tickers = tickers[0]
tickers = (tickers['Symbol'].tolist())
#tickers = tickers[0:50]
for z in range(len(tickers)):
    tickers[z] = tickers[z].upper().replace(".", "-")
datafull = pd.DataFrame()

START = "2020-05-01"
maxlen = len(yf.download("SPY", start=START, interval="1d"))
for i in tickers:
    print("{0} / {1}".format(tickers.index(i), len(tickers)))
    arr = yf.download(i, start=START, interval="1d")
    if len(arr) > (maxlen - 4):
        closes = arr['Close']
        data = {i: closes}
        df = pd.DataFrame(data)
        df = df.round(6)
        datafull = pd.concat([df, datafull], axis="columns")
    else:
        print("{0} is too short".format(i))

datafull = datafull.pct_change(fill_method=None)
datafull = datafull.dropna()
datafull.to_pickle("data.pkl")
datafull.to_csv("data.csv")