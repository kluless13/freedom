# /Users/kluless/freedom/backtest/HFT/fibrescalp.py
'''
Start                     2024-01-01 00:00:00                                                                   
End                       2024-06-04 00:00:00
Duration                    155 days 00:00:00
Exposure Time [%]                   95.596133
Equity Final [$]                 11587.350507
Equity Peak [$]                  12692.267286
Return [%]                          15.873505
Buy & Hold Return [%]               -4.017331
Return (Ann.) [%]                   41.158323
Volatility (Ann.) [%]               36.828626
Sharpe Ratio                         1.117563
Sortino Ratio                        2.909026
Calmar Ratio                         4.674057
Max. Drawdown [%]                   -8.805696
Avg. Drawdown [%]                   -2.759073
Max. Drawdown Duration       64 days 16:00:00
Avg. Drawdown Duration        8 days 03:00:00
# Trades                                  876
Win Rate [%]                        38.356164
Best Trade [%]                      30.943481
Worst Trade [%]                    -15.172034
Avg. Trade [%]                       0.792049
Max. Trade Duration          18 days 20:00:00
Avg. Trade Duration           3 days 19:00:00
Profit Factor                        1.376564
Expectancy [%]                       1.245901
SQN                                  3.690279
_strategy                 FibonacciBreakou...
'''


from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/echimoku/DATA.csv', parse_dates=['Date'])
data.rename(columns={'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
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

