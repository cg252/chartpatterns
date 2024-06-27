import json
import yfinance as yf
import time
from datetime import datetime
import numpy as np
import pandas as pd
np.seterr(divide='ignore', invalid='ignore')

TICKER = "EURUSD=X"

while True:
    #runs endlessly
    if datetime.today().weekday() < 5:
        #if market is openn
        historical_prices = yf.Ticker(TICKER).history(period='1d', interval='15m')
        # Get the latest price and time
        latest_price = historical_prices['Close'].iloc[-1]
        latest_time = historical_prices.index[-1].strftime('%H:%M')

        if latest_time == "00:00":
            with open('livedata.json', 'w') as f:
                f.write('{ }')


        #section to find current TSI rating

        arr = yf.download(TICKER, period="5d", interval="15m")
        dateList = arr.index
        closeList = arr['Close']
        PCList = []
        AbsPCList = []

        ### finding EMA
        def EMA(prices, period):
        #  weightfactor = 0.095278
            weightfactor = 0.10063
            ema = np.zeros(len(prices))
            sma = np.mean(prices[:period])
            ema[period - 1] = sma
            for i in range(period, len(prices)):
                ema[i] = (prices[i] * weightfactor) + (ema[i - 1] * (1 - weightfactor))
            return ema

        ### finding TSI
        for i in range(len(arr)):
            closeTD = closeList.iloc[i]
            closeYD = closeList.iloc[i-1]

            PCList.append(closeTD - closeYD)
            AbsPCList.append(abs(closeTD - closeYD))

        PCS = EMA(PCList, 25)
        PCDS = EMA(PCS, 13)
        APCS = EMA(AbsPCList, 25)
        APCDS = EMA(APCS, 13)
        TSI = (PCDS/APCDS)*100

        #calculate signal line using pandas
        df = pd.DataFrame({'close': TSI})
        df['ema'] = df['close'].ewm(span=13, adjust=False, min_periods=5).mean()
        TSIsignal = df['ema']

        curTSI = TSI[len(TSI)-1]
        curTSISignal = TSIsignal[len(TSI)-1]


        #### find SMA line values


        #calculate current SMA value highs 60 period and lows 60 period
        last60hsum = 0
        last60lsum = 0
        for i in range(60):
            highList = arr['High']
            lowList = arr['Low']
            last60hsum += highList.iloc[len(arr)-i-1]
            last60lsum += lowList.iloc[len(arr)-i-1]

        curHighSMA = last60hsum/60
        curLowSMA = last60lsum/60


        newdata = {
            latest_time: {
                "Price": latest_price,
                "TSI": curTSI,
                "TSI_Signal": curTSISignal,
                "YBR_High": curHighSMA,
                "YBR_Low": curLowSMA
            }
            }

        with open('livedata.json') as file:
            olddata = json.load(file)
        

        olddata.update(newdata)

        with open("livedata.json", 'w') as file:
            json.dump(olddata, file)

        print('{} Fetched'.format(latest_time))
        time.sleep(15)
    else:
        time.sleep(60)


