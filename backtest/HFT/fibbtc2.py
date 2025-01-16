# /Users/kluless/freedom/backtest/HFT/fibrescalp_ml.py

'''

'''

import optuna
from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/echimoku/DATA.csv', parse_dates=['Date'])
data.rename(columns={'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
data.set_index('Date', inplace=True)

# Define the strategy
class FibonacciBreakoutStrategy(Strategy):
    lookback_period = 20
    atr_period = 14
    atr_multiplier = 1.5
    take_profit_multiplier = 3
    cooldown_period = 5
    max_tp_distance = 0.1  # Maximum TP distance as percentage of price

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
        current_price = self.data.Close[-1]

        if current_price > self.fib_618[-1]:
            sl = current_price - self.atr_multiplier * self.atr[-1]
            # Ensure TP is not too far from entry
            tp_distance = min(
                self.atr_multiplier * self.take_profit_multiplier * self.atr[-1],
                current_price * self.max_tp_distance
            )
            tp = current_price + tp_distance
            self.buy(size=position_size, sl=sl, tp=tp)

        elif current_price < self.fib_382[-1]:
            sl = current_price + self.atr_multiplier * self.atr[-1]
            # Ensure TP is not too far from entry and stays positive
            tp_distance = min(
                self.atr_multiplier * self.take_profit_multiplier * self.atr[-1],
                current_price * self.max_tp_distance
            )
            tp = max(0.001, current_price - tp_distance)  # Ensure TP stays positive
            self.sell(size=position_size, sl=sl, tp=tp)

# Define the objective function for Optuna
def objective(trial):
    # Suggest hyperparameters with more conservative ranges
    lookback_period = trial.suggest_int('lookback_period', 15, 40, step=5)
    atr_period = trial.suggest_int('atr_period', 10, 20, step=2)
    atr_multiplier = trial.suggest_float('atr_multiplier', 1.0, 2.0, step=0.25)  # Reduced range
    take_profit_multiplier = trial.suggest_float('take_profit_multiplier', 1.5, 3.0, step=0.5)  # Changed to float with reduced range
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
