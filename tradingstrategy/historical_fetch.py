import yfinance as yf
import numpy as np
import pandas as pd
import talib

tickers = ["ES=F", "EURUSD=X", "YM=F", "NQ=F", "RTY=F", "GC=F","SI=F","PL=F"]
#TICKER = "EURUSD=X"

datafull = pd.DataFrame()
for i in tickers:
    arr = yf.download(i, start="2022-08-03", interval="1h")
    np.seterr(divide='ignore', invalid='ignore')
    #arr.index = arr.index.tz_convert("US/Eastern")

    highs = arr['High']
    lows = arr['Low']
    opens = arr['Open']
    closes = arr['Close']

    lowYBR = talib.SMA(lows, timeperiod=60)
    highYBR = talib.SMA(highs, timeperiod=60)
    ADXList = talib.ADX(highs, lows, closes, timeperiod=14)
    RSIList = talib.RSI(closes, timeperiod=14)
    MACDList, MACDSignalList, MACDHistList = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
    DMMinList = talib.MINUS_DI(highs, lows, closes, timeperiod=14)
    DMPlusList = talib.PLUS_DI(highs, lows, closes, timeperiod=14)

    #finds whether price recently crossed YBR to upside. 
    YBRCrossoverList = []
    for i in range(len(arr)):
        closeTD = arr['Close'].iloc[i]
        close3d = arr['Close'].iloc[i-3]
        YBRhighcur = highYBR.iloc[i]
        YBRhigh3d = highYBR.iloc[i-3]

        if closeTD > YBRhighcur:
            if close3d < YBRhigh3d:
                YBRCrossoverList.append(1)
            else:
                YBRCrossoverList.append(0)
        elif closeTD < YBRhighcur:
            if close3d > YBRhigh3d:
                YBRCrossoverList.append(2)
            else:
                YBRCrossoverList.append(0)
        else:
            YBRCrossoverList.append(0)
        


    ReturnList = []
    candlestickPattern = []

    #0: nothing
    #1-3: buy with varying confidence score
    MACDCrossover = []
    buysignal = []
    for i in range(len(MACDList)):
        MACDcur = MACDList.iloc[i]
        MACD1d = MACDList.iloc[i-1]
        MACD3d = MACDList.iloc[i-3]
        SIGcur = MACDSignalList.iloc[i]
        try:
            SIG3d = MACDSignalList.iloc[i-3]
        except:
            SIG3d = MACDSignalList.iloc[i]

        if MACDcur > SIGcur:
            if MACD3d < SIG3d:
                MACDCrossover.append(1)
            else:
                MACDCrossover.append(0)
        elif MACDcur < SIGcur:
            if MACD3d > SIG3d:
                MACDCrossover.append(2)
            else:
                MACDCrossover.append(0)
        else:
            MACDCrossover.append(0)


        #candle identification
        closeCur = arr["Close"].iloc[i]
        highCur = arr["High"].iloc[i]
        lowCur = arr["Low"].iloc[i]
        openCur = arr["Open"].iloc[i]
        

        ####
        buystrength = 0
        if (YBRCrossoverList[i] == 1 and MACDList.iloc[i] > MACDSignalList.iloc[i]):
            if (DMPlusList.iloc[i] > DMMinList.iloc[i] and ADXList.iloc[i] > 25):
                buystrength += 1

        if (YBRCrossoverList[i] == 1):
            for z in range(1, 300):
                    try:
                        tracingClose = arr["Close"].iloc[i+z]
                    except:
                        break
                    tracingYBRLow = lowYBR.iloc[i+z]
                    tracingYBRHigh= highYBR.iloc[i+z]
                    tracePercentChange = round(((tracingClose-closeCur)/closeCur)*100, 2)
                    if tracePercentChange < -0.05:
                        #stoploss
                        exitval = -0.05
                        break
                    if (tracingClose < tracingYBRHigh):
                        exitval = tracePercentChange
                        break
            if exitval > 0:
                exitval = 1
            else:
                exitval = 0
        else:
            try:
                exitval = 1 if (arr["Close"].iloc[i+3] > closeCur) else 0
            except:
                exitval = 0

        ReturnList.append(exitval)
        buysignal.append(buystrength)
        

    data = {"Close": closes,
            "MACD_Crossover": MACDCrossover,
            "YBR_Crossover": YBRCrossoverList,
            "adx": ADXList,
            "macd": MACDList,
        # "Hammer": candlestickPattern,
            "Signal": buysignal,
            "Return": ReturnList
            }


    df = pd.DataFrame(data)
    df = df[60:-5]
    #cut out incomplete data

    df = df.round(6)
    datafull = pd.concat([df, datafull])
    
datafull.to_csv("data.csv")

