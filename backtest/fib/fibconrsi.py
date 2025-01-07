'''
Start                     2023-08-12 00:00:00                                                                   
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        54.5
Equity Final [$]                 11563.634413
Equity Peak [$]                  11647.742513
Return [%]                          15.636344
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                   30.360853
Volatility (Ann.) [%]                9.734261
Sharpe Ratio                         3.118968 <-
Sortino Ratio                        7.252493
Calmar Ratio                         8.743349 <-
Max. Drawdown [%]                   -3.472451
Avg. Drawdown [%]                    -0.69207
Max. Drawdown Duration       13 days 00:00:00
Avg. Drawdown Duration        5 days 00:00:00
# Trades                                   35
Win Rate [%]                        85.714286 <-
Best Trade [%]                     122.064649
Worst Trade [%]                    -23.125529
Avg. Trade [%]                      22.247083
Max. Trade Duration          46 days 00:00:00
Avg. Trade Duration          26 days 00:00:00
Profit Factor                       30.376143
Expectancy [%]                      26.559938
SQN                                  3.792976
_strategy                 FibonacciRSIConf...
_equity_curve                             ...
_trades                       Size  EntryB...
dtype: object
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

class FibonacciRSIConfluenceStrategy(Strategy):
    lookback_period = 20  # Default value for optimization
    rsi_period = 14  # Default value for optimization
    ma_period = 50  # Moving average period, now a class variable
    atr_multiplier = 1.5  # Default value for optimization
    take_profit_multiplier = 2  # Default value for optimization

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
            lambda h, l, c: pd.Series(h - l).rolling(window=self.lookback_period).mean(),
            self.data.High, self.data.Low, self.data.Close
        )

        # Compute moving average
        self.ma = self.I(lambda x: pd.Series(x).rolling(window=self.ma_period).mean(), self.data.Close)

        # Compute RSI
        self.rsi = self.I(
            lambda x: 100 - (100 / (1 + (pd.Series(x).diff().clip(lower=0).rolling(window=self.rsi_period).mean() /
                                       pd.Series(x).diff().clip(upper=0).abs().rolling(window=self.rsi_period).mean()))),
            self.data.Close
        )

    def next(self):
        # Relaxed RSI conditions
        rsi_buy_zone = self.rsi[-1] < 45
        rsi_sell_zone = self.rsi[-1] > 55

        # Position sizing
        risk_per_trade = 0.02
        position_size = risk_per_trade

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and rsi_buy_zone:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and rsi_sell_zone:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = max(0.01, self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1])
            self.sell(size=position_size, sl=sl, tp=tp)

# Prepare data for backtesting
bt = Backtest(data, FibonacciRSIConfluenceStrategy, cash=10000, commission=0.002)
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    ma_period=range(20, 100, 10),  # Include ma_period in optimization
    rsi_period=range(10, 30, 5),  # Include rsi_period in optimization
    atr_multiplier=[1, 1.5, 2, 2.5, 3],
    take_profit_multiplier=[2, 3, 4, 5],
    maximize='Equity Final [$]'
)

# Print performance metrics
print(results)

# Plot results
bt.plot()

