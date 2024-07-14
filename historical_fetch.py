import yfinance as yf
import numpy as np
import pandas as pd

#TICKER = "EURUSD=X"
TICKER = "SPY"
Position_duration = 3
# number of candles before selling
#start-  2022-07-9


# buy sell column // do nothing 

arr = yf.download(TICKER, start="2023-07-15", interval="1h")
np.seterr(divide='ignore', invalid='ignore')


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
ResultsList = []
candlestickPattern = []

#might be 0 for hold, or 1 for buy
buysignal = []

for i in range(len(TSI)):
    #candle identification
    closeCur = arr["Close"].iloc[i]
    highCur =  arr["High"].iloc[i]
    lowCur =  arr["Low"].iloc[i]
    openCur =  arr["Open"].iloc[i]
    tsiCur = TSI[i]
    sigCur = SIGNAL[i]
    
    bodylen = abs(closeCur-openCur)
    fulllen = abs(highCur-lowCur)

    topwick = highCur-max(openCur, closeCur)
    bottomwick = min(openCur, closeCur)-lowCur

    avglen5 = (fulllen + abs( arr["High"].iloc[i-1]- arr["Low"].iloc[i-1]) + abs( arr["High"].iloc[i-2] - arr["Low"].iloc[i-2])
    + abs( arr["High"].iloc[i-3]- arr["Low"].iloc[i-3]) + abs( arr["High"].iloc[i-4]- arr["Low"].iloc[i-4]))/5

    if (topwick < 0.15*fulllen) and (bottomwick>1.35*bodylen) and (min(openCur, closeCur) > lowCur) and (fulllen > 0.8*avglen5):
        if tsiCur > sigCur:
            candlestickPattern.append('hammer')
        else:
            candlestickPattern.append('hammer')
    else:
        candlestickPattern.append('')



    ######


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

    TSIRelativePosition.append(TSIcur/SIGcur)

    if TSIcur > SIGcur:
        if TSI2d < SIGcur:
            TSICrossover.append(1)
        else:
             TSICrossover.append(0)
    elif TSIcur < SIGcur:
        if TSI2d > SIGcur:
            TSICrossover.append(2)
        else:
            TSICrossover.append(0)
    else:
         TSICrossover.append(0)

    #1 for green, 0 for red.
    #Results rating used to train model. 
    #based on Position_duration variable
    try:
        closefuture = arr["Close"].iloc[i+Position_duration]
    except: 
        closefuture = 0

    pr = closefuture-closeCur
    if pr > 0:
        pr = 1
    else:
         pr = 0
    ResultsList.append(pr)
     

data = {"Open": arr['Open'],
        "Close": arr['Close'],
        "High": arr['High'], 
        "Low": arr['Low'],
        "TSI": TSI,
        "TSI_Position": TSIRelativePosition,
        "TSI_Crossover": TSICrossover,
        "YBR_Position": YBRposList,
        "Hammer": candlestickPattern,
        "Results": ResultsList
        }


df = pd.DataFrame(data)
df = df[60:-Position_duration]
#cut out incomplete data

df = df.round(6)
df.to_csv("data.csv")

print(df['Results'].value_counts())