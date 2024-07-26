import yfinance as yf
import numpy as np
import pandas as pd

#TICKER = "EURUSD=X"
TICKER = "ES=F"
#TICKER = "SPY"
# number of candles before selling
#start-  2022-07-9


# buy sell column // do nothing 

arr = yf.download(TICKER, start="2022-07-25", interval="1h")
np.seterr(divide='ignore', invalid='ignore')
arr.index = arr.index.tz_convert("US/Eastern")

#print(arr.index[519])

PCList = []
AbsPCList = [] 

###finds ema
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
lowYBRList = []
highYBRList = []
YBRposList = []
for i in range(len(arr)):
    closeTD = arr['Close'].iloc[i]
    print(i)
    closeYD = arr['Close'].iloc[i-1]
    PCList.append(closeTD - closeYD)
    AbsPCList.append(abs(closeTD - closeYD))

    #calculate current SMA value highs 60 period and lows 60 period
    last60hsum = 0
    last60lsum = 0

    highList = arr['High']
    lowList = arr['Low']
    last60hsum = sum(highList.iloc[(i-59):(i+1)])
    last60lsum = sum(lowList.iloc[(i-59):(i+1)])
        
    highval = last60hsum/60
    lowval = last60lsum/60
    highYBRList.append(highval)
    lowYBRList.append(lowval)

    #append integer value based on the positon of close relative to YBR range
    # 1 for bullish, 2 for bearish, 0 for neutral
    if closeTD > highval: 
            YBRposList.append(1)
    elif closeTD < lowval:
        YBRposList.append(2)
    elif lowval < closeTD < highval: 
        YBRposList.append(0)
    else:
         YBRposList.append(0)

#finds whether price recently crossed YBR to upside. 
YBRCrossoverList = []
for i in range(len(arr)):
    closeTD = arr['Close'].iloc[i]
    close3d = arr['Close'].iloc[i-3]
    YBRhighcur = highYBRList[i]
    YBRhigh3d = highYBRList[i-3]

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

PCS = EMA(PCList, 25)
PCDS = EMA(PCS, 13)
APCS = EMA(AbsPCList, 25)
APCDS = EMA(APCS, 13)
TSI = (PCDS/APCDS)*100

#calculate signal line using pandas
df = pd.DataFrame({'close': TSI})
df['ema'] = df['close'].ewm(span=13, adjust=False, min_periods=5).mean()
SIGNAL = df['ema']


### calculate TSI positon relative to signal line
### 1 if recently crossed to upside and is holding, 2 if the same but to the downside, 0 if nothing
### TSIRelativePosition could be positive or negative, 0 for under, 1 for over
TSICrossover = []
TSIRelativePosition = []
ReturnList = []
candlestickPattern = []

#0: nothing
#1-3: buy with varying confidence score
buysignal = []
for i in range(len(TSI)):
    TSIcur = TSI[i]
    TSI1d = TSI[i-1]
    TSI3d = TSI[i-3]
    SIGcur = SIGNAL[i]
    try:
        SIG3d = SIGNAL[i-3]
    except:
        SIG3d = SIGNAL[i]

    TSIRelativePosition.append(TSIcur/SIGcur)

    if TSIcur > SIGcur:
        if TSI3d < SIG3d:
            TSICrossover.append(1)
        else:
             TSICrossover.append(0)
    elif TSIcur < SIGcur:
        if TSI3d > SIG3d:
            TSICrossover.append(2)
        else:
            TSICrossover.append(0)
    else:
         TSICrossover.append(0)

    ####


    buystrength = 0

    #candle identification
    closeCur = arr["Close"].iloc[i]
    highCur = arr["High"].iloc[i]
    lowCur = arr["Low"].iloc[i]
    openCur = arr["Open"].iloc[i]
    tsiCur = TSI[i]
    sigCur = SIGNAL[i]
    
    bodylen = abs(closeCur-openCur)
    fulllen = abs(highCur-lowCur)

    topwick = highCur-max(openCur, closeCur)
    bottomwick = min(openCur, closeCur)-lowCur

    avglen5 = (fulllen + abs( arr["High"].iloc[i-1]- arr["Low"].iloc[i-1]) + abs( arr["High"].iloc[i-2] - arr["Low"].iloc[i-2])
    + abs( arr["High"].iloc[i-3]- arr["Low"].iloc[i-3]) + abs( arr["High"].iloc[i-4]- arr["Low"].iloc[i-4]))/5

    if (topwick < 0.15*fulllen) and (bottomwick>1.35*bodylen) and (min(openCur, closeCur) > lowCur) and (fulllen > 0.9*avglen5):
        candlestickPattern.append('0')
        # 0 for hammer, 1 for inverted hammer
        #add 1 to buystrength if hammer is present at current tracing location and price has recently crossed ybr to upside
        if (YBRCrossoverList[i] == 1):
            buystrength += 1
    elif (bottomwick < 0.15*fulllen) and (topwick > 1.35*bodylen) and (max(openCur, closeCur) < highCur) and (fulllen > 0.9*avglen5):
        candlestickPattern.append('1')
        if (YBRCrossoverList[i] == 1):
            buystrength += 1
    else:
        candlestickPattern.append('')


    ####

    if (YBRCrossoverList[i] == 1):
        buystrength += 1
        if (TSICrossover[i] == 1):
            buystrength += 1

    if buystrength > 1:
        sl1 = False
        for z in range(1, 200):
            try:
                tracingClose = arr["Close"].iloc[i+z]
            except:
                break
            tracingYBRLow = lowYBRList[i+z]
            tracingYBRHigh= highYBRList[i+z]
            tracePercentChange = round(((tracingClose-closeCur)/closeCur)*100, 2)
            if tracePercentChange < -0.15:
                sl1 = True
            if (tracingClose < tracingYBRHigh):
                stoploss = tracePercentChange
                break
     #   if sl1 == True:
          #  ReturnList.append(-0.15)
     #   else:
        ReturnList.append(stoploss)
    else: 
        ReturnList.append(0)

    buysignal.append(buystrength)
     

data = {"Close": arr['Close'],
       # "TSI_Position": TSIRelativePosition,
        "TSI_Crossover": TSICrossover,
    #    "YBR_Position": YBRposList,
        "YBR_Crossover": YBRCrossoverList,
        "Hammer": candlestickPattern,
        "Signal": buysignal,
        "Return": ReturnList
        }


df = pd.DataFrame(data)
df = df[60:-5]
#cut out incomplete data

df = df.round(6)
df.to_csv("data.csv")

