import warnings, talib, yfinance as yf
warnings.simplefilter(action='ignore', category=FutureWarning)
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


TICKER = "SPY"
# Pull enough history for the 60-day channel + indicator warm-up to actually
# produce trades (the old 1-month default never gave the SMA(60) time to form).
arr = yf.download(TICKER, period="1y", interval="1h", multi_level_index=False)
arr.dropna(inplace=True)


class YBRCross(Strategy):
    """
    YBR Cross, trend-following: price breaking out above the 60-day
    SMA(High) channel still drives entries, unchanged from the original
    philosophy. What changed is risk management: instead of a fixed
    stop-loss/take-profit (which capped winners early) or mirroring every
    breakout with a short, this version is long-only and trails a wide
    ATR-based stop that locks in gains while giving the trend room to run.

    Backtesting showed that gating entries with ADX/RSI/MACD/DMI filters,
    or symmetrically shorting breakdowns, both reduced returns on a
    secularly uptrending instrument like SPY (shorts fight the trend, and
    the extra filters introduce lag that misses the start of the move) -
    so this version keeps the strategy intentionally simple.
    """
    channel_period = 60
    atr_period = 14
    atr_sl_mult = 7     # wide trailing stop so the trend has room to run

    def init(self):
        high, low, close = self.data.High, self.data.Low, self.data.Close

        self.ybrhigh = self.I(talib.SMA, high, self.channel_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)

    def next(self):
        atr = self.atr[-1]
        if atr != atr:  # NaN guard during indicator warm-up
            return

        price = self.data.Close[-1]
        long_signal = crossover(self.data.Close, self.ybrhigh)

        # Trail the stop up with price; never loosen it.
        for trade in self.trades:
            new_sl = price - self.atr_sl_mult * atr
            if trade.sl is None or new_sl > trade.sl:
                trade.sl = new_sl

        if long_signal and not self.position:
            self.buy(sl=price - self.atr_sl_mult * atr)


bt = Backtest(arr, YBRCross,
              cash=10000, commission=.002,
              exclusive_orders=True, finalize_trades=True)

output = bt.run()
print(output)
bt.plot()