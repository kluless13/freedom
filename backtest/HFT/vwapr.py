from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/HFT/BTC-USD-5m-2022-2-02T00_00.csv', parse_dates=['datetime'])
data.rename(columns={'datetime': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
data.set_index('Date', inplace=True)

class VWAPReversionStrategy(Strategy):
    lookback_period = 20
    deviation_factor = 0.05  # Adjusted for larger deviations

    def init(self):
        close = self.data.Close
        volume = self.data.Volume

        # Compute cumulative price-volume and volume as pandas Series
        cum_price_volume = (close * volume).cumsum()
        cum_volume = volume.cumsum()

        # Use self.I to register these values
        self.cum_price_volume = self.I(lambda: cum_price_volume)
        self.cum_volume = self.I(lambda: cum_volume)

        # Compute VWAP
        self.vwap = self.I(lambda: self.cum_price_volume / self.cum_volume)

    def next(self):
        current_price = self.data.Close[-1]
        current_vwap = self.vwap[-1]

        # Debugging: Show current price and VWAP
        print(f"Current Price: {current_price}, VWAP: {current_vwap}")

        # Define a fixed position size for testing
        position_size = 0.1  # 10% of the portfolio for each trade

        # Buy signal: price below VWAP by deviation factor
        if current_price < current_vwap * (1 - self.deviation_factor):
            print(f"Buy Signal Triggered at Price: {current_price}, VWAP: {current_vwap}")
            sl = current_price * (1 - 0.01)  # Stop-loss 1% below entry
            tp = current_price * (1 + 0.02)  # Take-profit 2% above entry
            self.buy(size=position_size, sl=sl, tp=tp)

        # Sell signal: price above VWAP by deviation factor
        elif current_price > current_vwap * (1 + self.deviation_factor):
            print(f"Sell Signal Triggered at Price: {current_price}, VWAP: {current_vwap}")
            sl = current_price * (1 + 0.01)  # Stop-loss 1% above entry
            tp = current_price * (1 - 0.02)  # Take-profit 2% below entry
            self.sell(size=position_size, sl=sl, tp=tp)

# Backtest and optimization
bt = Backtest(data, VWAPReversionStrategy, cash=100000, commission=0.002)

# Run the backtest
results = bt.optimize(
    lookback_period=range(10, 50, 5),
    deviation_factor=np.arange(0.01, 0.10, 0.01),
    maximize='Equity Final [$]'
)

# Display results
print("\nBacktest Results:")
print(results)

# Plot equity curve and trades
bt.plot()
