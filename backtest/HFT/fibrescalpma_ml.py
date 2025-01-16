from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import optuna

# Load data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])

data.rename(columns={
    'Datetime': 'Date', 
    'Open': 'Open', 
    'High': 'High', 
    'Low': 'Low', 
    'Close': 'Close', 
    'Volume': 'Volume'
}, inplace=True)
data.set_index('Date', inplace=True)

class FibonacciMAConfluenceStrategy(Strategy):
    lookback_period = 20
    ma_short_period = 50
    ma_long_period = 200
    atr_period = 14
    atr_multiplier = 1.5
    take_profit_multiplier = 2
    max_volatility = 0.05  # ATR as a % of price

    def init(self):
        # Calculate Fibonacci levels
        high = self.data.High
        low = self.data.Low
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)
        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        # ATR for volatility and dynamic sizing
        self.atr = self.I(
            lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(),
            self.data.High, self.data.Low, self.data.Close
        )

        # Moving averages
        self.ma_short = self.I(lambda x: pd.Series(x).rolling(window=self.ma_short_period).mean(), self.data.Close)
        self.ma_long = self.I(lambda x: pd.Series(x).rolling(window=self.ma_long_period).mean(), self.data.Close)

    def next(self):
        # Trend confirmation
        trend_up = self.ma_short[-1] > self.ma_long[-1]
        trend_down = self.ma_short[-1] < self.ma_long[-1]

        # Volatility filter
        current_volatility = self.atr[-1] / self.data.Close[-1]
        if current_volatility > self.max_volatility:
            return

        # Dynamic position sizing
        risk_per_trade = 0.02
        position_size = risk_per_trade * (1 / current_volatility)

        # Buy conditions
        if self.data.Close[-1] > self.fib_618[-1] and trend_up:
            sl = self.data.Close[-1] - self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell conditions
        elif self.data.Close[-1] < self.fib_382[-1] and trend_down:
            sl = self.data.Close[-1] + self.atr_multiplier * self.atr[-1]
            tp = self.data.Close[-1] - self.atr_multiplier * self.take_profit_multiplier * self.atr[-1]
            self.sell(size=position_size, sl=sl, tp=tp)

# Define optimization objective

def objective(trial):
    # Suggest hyperparameters
    lookback_period = trial.suggest_int('lookback_period', 10, 50, step=5)
    ma_short_period = trial.suggest_int('ma_short_period', 20, 100, step=10)
    ma_long_period = trial.suggest_int('ma_long_period', 100, 300, step=20)
    atr_period = trial.suggest_int('atr_period', 10, 20, step=2)
    atr_multiplier = trial.suggest_float('atr_multiplier', 1.0, 3.0, step=0.5)
    take_profit_multiplier = trial.suggest_float('take_profit_multiplier', 1.0, 5.0, step=0.5)
    max_volatility = trial.suggest_float('max_volatility', 0.01, 0.10, step=0.01)

    # Update strategy parameters
    FibonacciMAConfluenceStrategy.lookback_period = lookback_period
    FibonacciMAConfluenceStrategy.ma_short_period = ma_short_period
    FibonacciMAConfluenceStrategy.ma_long_period = ma_long_period
    FibonacciMAConfluenceStrategy.atr_period = atr_period
    FibonacciMAConfluenceStrategy.atr_multiplier = atr_multiplier
    FibonacciMAConfluenceStrategy.take_profit_multiplier = take_profit_multiplier
    FibonacciMAConfluenceStrategy.max_volatility = max_volatility

    # Run backtest
    bt = Backtest(data, FibonacciMAConfluenceStrategy, cash=10000, commission=0.002)
    stats = bt.run()

    # Optimize for final equity
    return stats['Equity Final [$]']

# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)

# Use best parameters
best_params = study.best_params
print("Best Parameters:", best_params)

FibonacciMAConfluenceStrategy.lookback_period = best_params['lookback_period']
FibonacciMAConfluenceStrategy.ma_short_period = best_params['ma_short_period']
FibonacciMAConfluenceStrategy.ma_long_period = best_params['ma_long_period']
FibonacciMAConfluenceStrategy.atr_period = best_params['atr_period']
FibonacciMAConfluenceStrategy.atr_multiplier = best_params['atr_multiplier']
FibonacciMAConfluenceStrategy.take_profit_multiplier = best_params['take_profit_multiplier']
FibonacciMAConfluenceStrategy.max_volatility = best_params['max_volatility']

# Final backtest with optimized parameters
bt = Backtest(data, FibonacciMAConfluenceStrategy, cash=10000, commission=0.002)
results = bt.run()
print(results)
bt.plot()
