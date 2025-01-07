'''
Start                     2023-08-12 00:00:00                                                                   
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        82.0 <-
Equity Final [$]                  17605.87208
Equity Peak [$]                   18164.90288
Return [%]                          76.058721 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  180.753393
Volatility (Ann.) [%]               81.431524
Sharpe Ratio                         2.219698
Sortino Ratio                       13.017223
Calmar Ratio                        17.829373
Max. Drawdown [%]                  -10.137956
Avg. Drawdown [%]                   -2.722051
Max. Drawdown Duration       51 days 00:00:00
Avg. Drawdown Duration       10 days 00:00:00
# Trades                                  158 <-
Win Rate [%]                        80.379747 <-
Best Trade [%]                     113.184312
Worst Trade [%]                    -25.619748
Avg. Trade [%]                      27.085964
Max. Trade Duration          69 days 00:00:00
Avg. Trade Duration          24 days 00:00:00
Profit Factor                       13.998857
Expectancy [%]                      31.406397
SQN                                 10.862541
_strategy                 FibonacciBreakou...
_equity_curve                             ...
_trades                        Size  Entry...
dtype: object
'''

from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])
data.rename(columns={'Datetime': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
data.set_index('Date', inplace=True)

class FibonacciBreakoutStrategy(Strategy):
    lookback_period = 20  # Swing high/low calculation period
    atr_period = 14  # ATR period for stop-loss and take-profit
    atr_multiplier = 1.5  # Multiplier for ATR-based stop-loss
    take_profit_multiplier = 3  # Risk-reward ratio multiplier
    cooldown_period = 5  # Minimum bars between trades

    def init(self):
        # Calculate swing highs and lows
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), self.data.High)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), self.data.Low)

        # Calculate Fibonacci retracement levels
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # Calculate ATR for dynamic stop-loss and take-profit
        self.atr = self.I(lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(), self.data.High, self.data.Low, self.data.Close)

    def next(self):
        # Cooldown check
        if len(self.trades) > 0 and self.trades[-1].exit_bar is not None and len(self.data) - self.trades[-1].exit_bar < self.cooldown_period:
            return

        # Define position size as a fraction of equity
        risk_per_trade = 0.02  # Risk 2% of equity per trade
        position_size = risk_per_trade

        # Buy condition: Breakout above 61.8% retracement level
        if self.data.Close[-1] > self.fib_618[-1]:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell condition: Breakout below 38.2% retracement level
        elif self.data.Close[-1] < self.fib_382[-1]:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.sell(size=position_size, sl=sl, tp=tp)

# Backtest setup
bt = Backtest(data, FibonacciBreakoutStrategy, cash=10000, commission=0.002)

# Run optimization
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    atr_period=range(10, 20, 2),
    atr_multiplier=[1, 1.5, 2],
    take_profit_multiplier=[2, 3, 4],
    cooldown_period=range(3, 15, 2),
    maximize='Equity Final [$]'
)

# Print results
print(results)

# Plot results
bt.plot()
