import yfinance as yf
import numpy as np
import pandas as pd

TICKER = "EURUSD=X"

arr = yf.download(TICKER, start="2024-05-5", interval="15m")
np.seterr(divide='ignore', invalid='ignore')

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
    closeYD = arr['Close'].iloc[i-1]
    PCList.append(closeTD - closeYD)
    AbsPCList.append(abs(closeTD - closeYD))

    #calculate current SMA value highs 60 period and lows 60 period
    last60hsum = 0
    last60lsum = 0

    for z in range(60):
        highList = arr['High']
        lowList = arr['Low']
        last60hsum += highList.iloc[i-z-1]
        last60lsum += lowList.iloc[i-z-1]
        
    highval = last60hsum/60
    lowval = last60lsum/60
    highYBRList.append(highval/60)
    lowYBRList.append(lowval/60)

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
for i in range(len(TSI)):
    TSIcur = TSI[i]
    TSI1d = TSI[i-1]
    TSI2d = TSI[i-2]
    SIGcur = SIGNAL[i]

    try:
        SIG1d = SIGNAL[i-1]
        SIG2d = SIGNAL[i-2]
    except:
        SIG1d = 0
        SIG2d = 0

    if TSIcur > SIGcur:
        TSIRelativePosition.append(1)
        if TSI2d < SIGcur:
               TSICrossover.append(1)
        else:
             TSICrossover.append(0)
    elif TSIcur < SIGcur:
        TSIRelativePosition.append(0)
        if TSI2d > SIGcur:
            TSICrossover.append(2)
        else:
            TSICrossover.append(0)
    else:
         TSIRelativePosition.append(0)
         TSICrossover.append(0)
     

timeList = []
openList = []
closeList = []
highList = []
lowList = []
newtsiList = []
newtsiSigPosList = []
newtsiCrossoverList = []
newYBRposList = []

for i in range(len(TSI)-60):
    newtsiList.append(TSI[i+60])
    closeList.append(arr['Close'].iloc[i+60])
    openList.append(arr['Open'].iloc[i+60])
    lowList.append(arr['Low'].iloc[i+60])
    highList.append(arr['High'].iloc[i+60])
    timeList.append(arr.index[i+60])
    newYBRposList.append(YBRposList[i+60])
    newtsiSigPosList.append(TSIRelativePosition[i+60])
    newtsiCrossoverList.append(TSICrossover[i+60])



data = {"Time": timeList,
        "Open": openList,
        "Close": closeList,
        "High": highList, 
        "Low": lowList,
        "TSI": newtsiList,
        "TSI Signal Position": newtsiSigPosList,
        "TSI Crossover": newtsiCrossoverList,
        "YBR Position": newYBRposList,
        "Profit Rating": 5
        }


df = pd.DataFrame(data)
df = df.round(6)
  
df.to_csv("data.csv")


