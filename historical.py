import yfinance as yf
import numpy as np
import pandas as pd
import json
import os

TICKER = "NVDA"


arr = yf.download(TICKER, period="1mo", interval="15m")
np.seterr(divide='ignore', invalid='ignore')

dateList = arr.index
closeList = arr['Close']
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

open('historicaldata.json', 'w').close()

for i in range(len(TSI)-28):
    curTSI = TSI[i+28]
    curSIG = SIGNAL[i+28]
    curPRICE = closeList.iloc[i+28]

    dtlist = dateList[i+28]
    curTIME = dtlist.strftime('%x') + "-" + dtlist.strftime('%H:%M')
    #curDATE = dtlist.strftime('%x')

    newdata = {curTIME: {
                "Price": curPRICE,
                "TSI": curTSI,
                "TSI_Signal": curSIG
            }
            }
    
  #  with open('historicaldatatemp.json', 'r+') as f:
   #     json.dump(newdata,f)

    with open('historicaldata.json', 'r+') as f:
        if os.stat("historicaldata.json").st_size != 0:
            olddata = json.load(f)
        else:
             olddata = ''
     
    newdata.update(olddata)

    with open('historicaldata.json', 'r+') as file:
            json.dump(newdata, file)
