import yfinance as yf
import numpy as np
import pandas as pd

TICKER = "EURUSD=X"

arr = yf.download(TICKER, period="1mo", interval="15m")
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
for i in range(len(arr)):
    closeTD = arr['Close'].iloc[i]
    closeYD = arr['Close'].iloc[i-1]
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
SIGNAL = df['ema']


timeList = []
openList = []
closeList = []
highList = []
lowList = []
tsiList = []
tsiSigList = []

for i in range(len(TSI)-28):
    tsiList.append(TSI[i+28])
    tsiSigList.append(SIGNAL[i+28])
    closeList.append(arr['Close'].iloc[i+28])
    openList.append(arr['Open'].iloc[i+28])
    lowList.append(arr['Low'].iloc[i+28])
    highList.append(arr['High'].iloc[i+28])
    timeList.append(arr.index[i+28])

data = {"Time": timeList,
        "Open": openList,
        "Close": closeList,
        "High": highList, 
        "Low": lowList,
        "TSI": tsiList,
        "TSI_Signal": tsiSigList}

df = pd.DataFrame(data)
df = df.round(6)

print(df)

