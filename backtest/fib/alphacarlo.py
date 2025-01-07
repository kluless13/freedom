import numpy as np
from backtesting import Backtest, Strategy
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


class EnhancedFibonacciRetracementStrategy(Strategy):
    lookback_period = 20
    atr_period = 14
    atr_multiplier = 1.5
    take_profit_multiplier = 3
    cooldown_period = 5

    def init(self):
        high = self.data.High
        low = self.data.Low

        self.swing_high = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).max(), high)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(window=self.lookback_period).min(), low)

        self.fib_382 = self.swing_high - (self.swing_high - self.swing_low) * 0.382
        self.fib_618 = self.swing_high - (self.swing_high - self.swing_low) * 0.618

        self.atr = self.I(lambda h, l, c: pd.Series(h - l).rolling(window=self.atr_period).mean(), high, low, self.data.Close)
        self.ma50 = self.I(lambda x: pd.Series(x).rolling(window=50).mean(), self.data.Close)

    def next(self):
    # Check cooldown
        if len(self.trades) > 0 and self.trades[-1].exit_bar is not None and len(self.data) - self.trades[-1].exit_bar < self.cooldown_period:
            return

    # Ensure sufficient data
        if np.isnan(self.fib_382[-1]) or np.isnan(self.fib_618[-1]) or np.isnan(self.atr[-1]):
            return

    # Trend confirmation using precomputed moving average
        trend_up = self.data.Close[-1] > self.ma50[-1]

    # Position sizing as a fraction of equity
        risk_per_trade = 0.02
        position_size = risk_per_trade

    # Calculate SL and TP with bounds
        sl = max(self.data.Close[-1] - self.atr_multiplier * self.atr[-1], 0.01)
        tp = max(self.data.Close[-1] + self.atr_multiplier * self.take_profit_multiplier * self.atr[-1], 0.01)

    # Buy conditions (Long)
        if self.data.Close[-1] > self.fib_618[-1] and trend_up:
            if sl < self.data.Close[-1] and tp > self.data.Close[-1]:
                self.buy(size=position_size, sl=sl, tp=tp)

    # Sell conditions (Short)
        elif self.data.Close[-1] < self.fib_382[-1] and not trend_up:
            if sl > self.data.Close[-1] and tp < self.data.Close[-1]:
                self.sell(size=position_size, sl=sl, tp=tp)





# Alpha Decay Testing
def run_alpha_decay_test(data, strategy_class, delays):
    for delay in delays:
        print(f"Running backtest with {delay}-minute delay...")
        strategy_class.cooldown_period = delay
        bt = Backtest(data, strategy_class, cash=10000, commission=0.002)
        stats = bt.run()
        print(stats)
        print("\n" + "=" * 50 + "\n")


# Monte Carlo Simulation
def monte_carlo_simulation(data, strategy_class, n_simulations=100):
    results = []
    equity_curves = []

    for i in range(n_simulations):
        shuffled_data = data.sample(frac=1, replace=False).reset_index(drop=True)
        bt = Backtest(shuffled_data, strategy_class, cash=10000, commission=0.002)
        stats = bt.run()

        equity_curve = stats['_equity_curve']['Equity']
        equity_curves.append(equity_curve.values)

        results.append({
            'Final Equity': equity_curve.iloc[-1],
            'Return [%]': stats['Return [%]'],
            'Max Drawdown [%]': stats['Max. Drawdown [%]'],
            'Sharpe Ratio': stats['Sharpe Ratio']
        })

    return results, equity_curves


# Load Data
data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv', parse_dates=['Datetime'])
data.rename(columns={'Datetime': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'}, inplace=True)
data.set_index('Date', inplace=True)

# Run Alpha Decay Test
delays = [0, 1, 2, 5, 10, 15]
run_alpha_decay_test(data, EnhancedFibonacciRetracementStrategy, delays)

# Run Monte Carlo Simulation
n_simulations = 100
results, equity_curves = monte_carlo_simulation(data, EnhancedFibonacciRetracementStrategy, n_simulations)

# Plot Monte Carlo Simulation
plt.figure(figsize=(12, 6))
for equity_curve in equity_curves:
    plt.plot(equity_curve, color='blue', alpha=0.1)
plt.title(f'Monte Carlo Simulation ({n_simulations} runs)')
plt.xlabel('Time')
plt.ylabel('Equity')
plt.show()
