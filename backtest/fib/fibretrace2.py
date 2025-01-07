'''
/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv

Start                     2023-08-12 00:00:00                                                                   
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00 <-
Exposure Time [%]                        74.5 <-
Equity Final [$]                  19048.94434
Equity Peak [$]                   19739.98464
Return [%]                          90.489443 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  224.163726
Volatility (Ann.) [%]               112.47598
Sharpe Ratio                         1.992992 <-
Sortino Ratio                       12.928623
Calmar Ratio                         16.65079
Max. Drawdown [%]                  -13.462648
Avg. Drawdown [%]                   -3.047986
Max. Drawdown Duration       51 days 00:00:00
Avg. Drawdown Duration        9 days 00:00:00
# Trades                                  147 <-
Win Rate [%]                        89.795918 <-
Best Trade [%]                     141.544774
Worst Trade [%]                    -27.633154
Avg. Trade [%]                      37.269032
Max. Trade Duration         100 days 00:00:00
Avg. Trade Duration          35 days 00:00:00
Profit Factor                       32.383519
Expectancy [%]                      42.140628
SQN                                 12.291504
_strategy                 EnhancedFibonacc...
_equity_curve                             ...
_trades                        Size  Entry...
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

class EnhancedFibonacciRetracementStrategy(Strategy):
    lookback_period = 20  # Optimizable parameter
    atr_period = 14  # ATR period for dynamic stop-loss and position sizing
    atr_multiplier = 1.5  # Multiplier for ATR-based stop-loss
    take_profit_multiplier = 3  # Increased reward-to-risk ratio
    cooldown_period = 5  # Reduced cooldown to allow more trades

    def init(self):
        # Precompute Fibonacci levels
        high = self.data.High
        low = self.data.Low

        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)

        # Calculate Fibonacci levels
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # Calculate ATR for dynamic stop-loss and position sizing
        self.atr = self.I(lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(), high, low, self.data.Close)

        # Compute 50-period moving average for trend confirmation
        self.ma50 = self.I(lambda x: pd.Series(x).rolling(window=50).mean(), self.data.Close)

    def next(self):
        # Check cooldown
        if len(self.trades) > 0 and self.trades[-1].exit_bar is not None and len(self.data) - self.trades[-1].exit_bar < self.cooldown_period:
            return

        # Trend confirmation using precomputed moving average
        trend_up = self.data.Close[-1] > self.ma50[-1]

        # Position sizing as a fraction of equity
        risk_per_trade = 0.02  # Risk 2% of equity per trade
        position_size = risk_per_trade  # Trade 2% of equity as a fraction

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and trend_up:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and not trend_up:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.sell(size=position_size, sl=sl, tp=tp)

# Prepare data for backtesting
bt = Backtest(data, EnhancedFibonacciRetracementStrategy, cash=10000, commission=0.002)
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    atr_period=range(10, 20, 2),
    atr_multiplier=[1, 1.5, 2, 2.5],
    take_profit_multiplier=[2, 3, 4],
    cooldown_period=range(3, 15, 2),
    maximize='Equity Final [$]'
)

# Print performance metrics
print(results)

# Plot results
bt.plot()
