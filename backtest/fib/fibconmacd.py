'''
Start                     2023-08-12 00:00:00                                                                   
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        82.0 <-
Equity Final [$]                 18227.127389
Equity Peak [$]                  20381.864357
Return [%]                          82.271274 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  199.096112
Volatility (Ann.) [%]               99.796172
Sharpe Ratio                         1.995028 <-
Sortino Ratio                       12.285234
Calmar Ratio                        15.753611 <-
Max. Drawdown [%]                  -12.638125
Avg. Drawdown [%]                   -2.890919
Max. Drawdown Duration       64 days 00:00:00
Avg. Drawdown Duration       11 days 00:00:00
# Trades                                  124
Win Rate [%]                        76.612903 <-
Best Trade [%]                     130.066754
Worst Trade [%]                    -28.491588
Avg. Trade [%]                      43.418242
Max. Trade Duration          62 days 00:00:00
Avg. Trade Duration          34 days 00:00:00
Profit Factor                       27.628238
Expectancy [%]                      50.046573
SQN                                 10.079023
_strategy                 FibonacciMACDCon...
_equity_curve                             ...
_trades                        Size  Entry...
'''


from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])

# Ensure column names are in the required format
data.rename(columns={
    'Datetime': 'Date', 
    'Open': 'Open', 
    'High': 'High', 
    'Low': 'Low', 
    'Close': 'Close', 
    'Volume': 'Volume'
}, inplace=True)
data.set_index('Date', inplace=True)

class FibonacciMACDConfluenceStrategy(Strategy):
    lookback_period = 20
    macd_fast_period = 12
    macd_slow_period = 26
    macd_signal_period = 9
    atr_period = 14
    atr_multiplier = 1.5
    take_profit_multiplier = 2

    def init(self):
        # Precompute Fibonacci levels
        high = self.data.High
        low = self.data.Low
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # Compute ATR for dynamic stop-loss and position sizing
        self.atr = self.I(
            lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(),
            self.data.High, self.data.Low, self.data.Close
        )

        # Compute MACD and Signal line
        self.macd = self.I(
            lambda x: pd.Series(x).ewm(span=self.macd_fast_period).mean() -
                      pd.Series(x).ewm(span=self.macd_slow_period).mean(),
            self.data.Close
        )
        self.macd_signal = self.I(
            lambda x: pd.Series(x).ewm(span=self.macd_signal_period).mean(),
            self.macd
        )

    def next(self):
        # MACD crossover conditions
        macd_above_signal = self.macd[-1] > self.macd_signal[-1]
        macd_below_signal = self.macd[-1] < self.macd_signal[-1]

        # Position sizing
        risk_per_trade = 0.02
        position_size = risk_per_trade

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and macd_above_signal:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and macd_below_signal:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = max(0.01, self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1])
            self.sell(size=position_size, sl=sl, tp=tp)

# Prepare data for backtesting
bt = Backtest(data, FibonacciMACDConfluenceStrategy, cash=10000, commission=0.002)
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    macd_fast_period=range(10, 20, 2),
    macd_slow_period=range(20, 40, 5),
    macd_signal_period=range(5, 15, 2),
    atr_multiplier=[1, 1.5, 2, 2.5, 3],
    take_profit_multiplier=[2, 3, 4, 5],
    maximize='Equity Final [$]'
)

# Print performance metrics
print(results)

# Plot results
bt.plot()
