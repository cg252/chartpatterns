import warnings, talib, yfinance as yf
warnings.simplefilter(action='ignore', category=FutureWarning)
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


TICKER = "SPY"
#arr = yf.download(TICKER, start="2022-09-03", interval="1h")
arr = yf.download(TICKER, interval="1d")

highs = arr['High']
lows = arr['Low']
opens = arr['Open']
closes = arr['Close']

ADXList = talib.ADX(highs, lows, closes, timeperiod=14)
RSIList = talib.RSI(closes, timeperiod=14)
MACDList, MACDSignalList, MACDHistList = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
DMMinList = talib.MINUS_DI(highs, lows, closes, timeperiod=14)
DMPlusList = talib.PLUS_DI(highs, lows, closes, timeperiod=14)

class YBRCross(Strategy):

    def init(self):
        self.closes = self.data.Close
        closes = self.data.Close
        lows = self.data.Low
        opens = self.data.Open
        highs = self.data.High

        self.ybrhigh = talib.SMA(highs, timeperiod=60)
        self.ybrlow = talib.SMA(lows, timeperiod=60)

    def next(self):
        if crossover(self.closes, self.ybrhigh):
            self.buy()
        elif crossover(self.ybrlow, self.closes):
            self.sell()


bt = Backtest(arr, YBRCross,
              cash=10000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()