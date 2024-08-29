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
        closes = self.data.Close
        lows = self.data.Low
        opens = self.data.Open
        highs = self.data.High

        self.ybrhigh = self.I(SMA, highs, 60)
        self.ybrlow = self.I(SMA, lows, 60)

    def next(self):
        if crossover(self.data.Close, self.ybrhigh):
            self.buy()
        elif crossover(self.ybrlow, self.data.Close):
            self.sell()


bt = Backtest(arr, YBRCross,
              cash=10000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)
bt.plot()