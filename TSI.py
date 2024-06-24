import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


arr = yf.download("NVDA", period="max", interval="1d", start="2022-01-01")
dateList = arr.index

openList = arr['Open']
closeList = arr['Close']
lowList = arr['Low']
highList = arr['High']
highlowList = arr['High'] - arr['Low']

PCList = []
AbsPCList = []


setupDates = []
Return2d = []
Return4d = []
Return7d = []


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
SIGNAL = df['ema']

x = dateList
y = TSI
 
plt.plot(x, y, label='TSI')
plt.plot(x, SIGNAL, label='Signal')
plt.xlabel('Date')
plt.ylabel('TSI')
plt.title('TSI')
plt.legend()
plt.show()