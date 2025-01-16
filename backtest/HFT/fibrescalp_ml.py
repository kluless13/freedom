'''
Start                     2023-08-12 00:00:00
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        82.0 <-
Equity Final [$]                   20122.6359
Equity Peak [$]                    20865.8317
Return [%]                         101.226359 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  258.281914
Volatility (Ann.) [%]              137.011325
Sharpe Ratio                         1.885114 <-
Sortino Ratio                       13.421092
Calmar Ratio                        17.077878
Max. Drawdown [%]                  -15.123771
Avg. Drawdown [%]                   -3.529058
Max. Drawdown Duration       51 days 00:00:00
Avg. Drawdown Duration       10 days 00:00:00
# Trades                                  161 <-
Win Rate [%]                        88.198758 <-
Best Trade [%]                     140.217375
Worst Trade [%]                    -26.219993
Avg. Trade [%]                        39.2806
Max. Trade Duration         100 days 00:00:00
Avg. Trade Duration          37 days 00:00:00
Profit Factor                       54.402844
Expectancy [%]                      44.607506
SQN                                 12.477236
_strategy                 FibonacciBreakou...
_equity_curve                             ...
_trades                        Size  Entry...
'''

import optuna
from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])
data.rename(columns={'Datetime': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
data.set_index('Date', inplace=True)

# Define the strategy
class FibonacciBreakoutStrategy(Strategy):
    lookback_period = 20
    atr_period = 14
    atr_multiplier = 1.5
    take_profit_multiplier = 3
    cooldown_period = 5

    def init(self):
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), self.data.High)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), self.data.Low)
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618
        self.atr = self.I(lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(), self.data.High, self.data.Low, self.data.Close)

    def next(self):
        if len(self.trades) > 0 and self.trades[-1].exit_bar is not None and len(self.data) - self.trades[-1].exit_bar < self.cooldown_period:
            return

        risk_per_trade = 0.02
        position_size = risk_per_trade

        if self.data.Close[-1] > self.fib_618[-1]:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        elif self.data.Close[-1] < self.fib_382[-1]:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.sell(size=position_size, sl=sl, tp=tp)

# Define the objective function for Optuna
def objective(trial):
    # Suggest hyperparameters
    lookback_period = trial.suggest_int('lookback_period', 15, 40, step=5)
    atr_period = trial.suggest_int('atr_period', 10, 20, step=2)
    atr_multiplier = trial.suggest_float('atr_multiplier', 1.5, 3, step=0.5)
    take_profit_multiplier = trial.suggest_int('take_profit_multiplier', 2, 4)
    cooldown_period = trial.suggest_int('cooldown_period', 5, 15, step=2)

    # Update strategy parameters
    FibonacciBreakoutStrategy.lookback_period = lookback_period
    FibonacciBreakoutStrategy.atr_period = atr_period
    FibonacciBreakoutStrategy.atr_multiplier = atr_multiplier
    FibonacciBreakoutStrategy.take_profit_multiplier = take_profit_multiplier
    FibonacciBreakoutStrategy.cooldown_period = cooldown_period

    # Run backtest
    bt = Backtest(data, FibonacciBreakoutStrategy, cash=10000, commission=0.002)
    stats = bt.run()

    # Penalize strategies with excessive trades (>500 trades)
    if stats['# Trades'] > 500:
        return float('-inf')

    # Combine multiple objectives: Sharpe Ratio + Profit Factor
    score = stats['Sharpe Ratio'] * 0.7 + stats['Profit Factor'] * 0.3
    return score

# Run Optuna study
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=200)

# Print best parameters
print("Best Parameters:", study.best_params)

# Backtest with best parameters
FibonacciBreakoutStrategy.lookback_period = study.best_params['lookback_period']
FibonacciBreakoutStrategy.atr_period = study.best_params['atr_period']
FibonacciBreakoutStrategy.atr_multiplier = study.best_params['atr_multiplier']
FibonacciBreakoutStrategy.take_profit_multiplier = study.best_params['take_profit_multiplier']
FibonacciBreakoutStrategy.cooldown_period = study.best_params['cooldown_period']

bt = Backtest(data, FibonacciBreakoutStrategy, cash=10000, commission=0.002)
results = bt.run()
print(results)
bt.plot()