import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import talib
import matplotlib.pyplot as plt
import warnings

# Suppress specific warnings related to plotting
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Define the Enhanced Pivot Point Strategy
class EnhancedPivotPointStrategy(Strategy):
    def init(self):
        # Initialize indicators
        # Simple Moving Averages
        self.ma_short = self.I(SMA, self.data.Close, 10)
        self.ma_long = self.I(SMA, self.data.Close, 50)
    
        # Relative Strength Index using talib
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
    
        # Average True Range using talib
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
    def next(self):
        # ATR multiplier constants for position sizing
        atr_sl_multiplier = 2.5  # Increased SL distance
        atr_tp_multiplier = 5.0  # Increased TP distance  
        buffer = 0.005  # Increased buffer size
        
        # Current Close Price
        current_close = self.data.Close[-1]
        
        # Current Pivot Points and Support/Resistance Levels 
        PP = self.data.PP[-1]
        R1 = self.data.R1[-1]
        S1 = self.data.S1[-1]
        
        # Current Indicator Values
        ma_short = self.ma_short[-1]
        ma_long = self.ma_long[-1]
        current_rsi = self.rsi[-1]
        current_atr = self.atr[-1]
        
        # Trade size set to 1 unit (0.001 BTC)
        size = 1
        
        # Debugging: Print relevant information
        print(f"PP: {PP:.2f}, R1: {R1:.2f}, S1: {S1:.2f}, Close: {current_close:.2f}, "
              f"SMA10: {ma_short:.2f}, SMA50: {ma_long:.2f}, RSI: {current_rsi:.2f}, ATR: {current_atr:.2f}, Size: {size}")
        
        # Entry Conditions
        if not self.position:
            # Buy Signal Conditions
            if (current_close > PP and
                crossover(self.ma_short, self.ma_long) and
                current_rsi < 70 and
                current_close > self.ma_long[-1]):
                
                # Calculate dynamic SL and TP based on ATR
                # Calculate dynamic SL and TP based on ATR with fixed multipliers
                atr_sl_multiplier = 2.0  # SL distance in ATR units
                atr_tp_multiplier = 4.0  # TP distance in ATR units
                buffer = 0.001  # Small buffer to ensure proper ordering

                # For buy orders: SL below entry, TP above entry
                sl_price = current_close - (atr_sl_multiplier * current_atr) - buffer
                tp_price = current_close + (atr_tp_multiplier * current_atr) + buffer
                
                # Execute Buy Order
                self.buy(sl=sl_price, tp=tp_price, size=size)
                print("Executed Buy Order")
                
            # Sell Signal Conditions
            elif (current_close < PP and
                  crossover(self.ma_long, self.ma_short) and
                  current_rsi > 30 and
                  current_close < self.ma_long[-1]):
                
                # Calculate dynamic SL and TP based on ATR
                # For sell orders: SL above entry, TP below entry
                sl_price = current_close + (atr_sl_multiplier * current_atr) + buffer
                tp_price = current_close - (atr_tp_multiplier * current_atr) - buffer
                
                # Execute Sell Order (Short)
                self.sell(sl=sl_price, tp=tp_price, size=size)
                print("Executed Sell Order")
        
        else:
            # Adjust stop loss and take profit for existing positions
            if self.position.is_long:
                # Long positions: SL and TP are managed automatically by Backtesting.py
                pass  # No additional logic needed as SL and TP are set during entry
                
            elif self.position.is_short:
                # Short positions: SL and TP are managed automatically by Backtesting.py
                pass  # No additional logic needed as SL and TP are set during entry

# Path to your CSV data
data_path = '/Users/kluless/freedom/backtest/BTC-USD-15m-2023-1-01T00_00 (1).csv'

# Load the data
df = pd.read_csv(data_path, parse_dates=['datetime'])

# Rename columns to match Backtest library expectations
df.rename(columns=lambda x: x.strip().capitalize(), inplace=True)
# Example: 'open' -> 'Open', 'high' -> 'High', etc.

# Drop the unnamed column if it exists
if 'Unnamed: 6' in df.columns:
    df.drop(columns=['Unnamed: 6'], inplace=True)

# Set datetime as the DataFrame index
df.set_index('Datetime', inplace=True)

# Ensure there are no duplicate indices
df = df[~df.index.duplicated(keep='first')]

# Sort the DataFrame by datetime just in case
df.sort_index(inplace=True)

# Resample to daily frequency to get previous day's high, low, and close
daily = df.resample('D').agg({
    'High': 'max',
    'Low': 'min',
    'Close': 'last'
})

# Shift the daily data by one day to get previous day's values
daily_shifted = daily.shift(1).rename(columns={
    'High': 'High_prev',
    'Low': 'Low_prev',
    'Close': 'Close_prev'
})

# Merge the shifted daily data back into the 15-minute DataFrame
df = df.merge(daily_shifted, left_index=True, right_index=True, how='left')

# Forward fill the pivot point data to propagate the previous day's values to all 15-minute intervals of the current day
df[['High_prev', 'Low_prev', 'Close_prev']] = df[['High_prev', 'Low_prev', 'Close_prev']].ffill()

# Drop any rows that still have NaN values in pivot point columns (typically the first day)
df.dropna(subset=['High_prev', 'Low_prev', 'Close_prev'], inplace=True)

# Ensure numerical types
df[['High_prev', 'Low_prev', 'Close_prev']] = df[['High_prev', 'Low_prev', 'Close_prev']].astype(float)

# Precompute Pivot Points and Support/Resistance Levels
df['PP'] = (df['High_prev'] + df['Low_prev'] + df['Close_prev']) / 3
df['R1'] = (2 * df['PP']) - df['Low_prev']
df['S1'] = (2 * df['PP']) - df['High_prev']
df['R2'] = df['PP'] + (df['High_prev'] - df['Low_prev'])
df['S2'] = df['PP'] - (df['High_prev'] - df['Low_prev'])

# Scale down the price columns
scaling_factor = 1000
price_columns = ['Open', 'High', 'Low', 'Close', 'High_prev', 'Low_prev', 'Close_prev', 'PP', 'R1', 'S1', 'R2', 'S2']
df[price_columns] = df[price_columns] / scaling_factor

# Validate pivot points
assert (df['R1'] > df['PP']).all(), "R1 should always be greater than PP."
assert (df['PP'] > df['S1']).all(), "PP should always be greater than S1."

# Initialize the Backtest with the prepared DataFrame and the EnhancedPivotPointStrategy
bt = Backtest(
    df,
    EnhancedPivotPointStrategy,
    cash=100,  # Increased initial cash to $100 (scaled)
    commission=0.002,  # 0.2% commission per trade
    exclusive_orders=True  # Ensures no overlapping orders
)

# Run the backtest
stats = bt.run()

# Print the backtest statistics
print(stats)

# Optionally, plot the equity curve using matplotlib to avoid Bokeh issues
# Extract equity curve
equity = stats['_equity_curve']
equity['Equity'] = equity['Equity'] * scaling_factor  # Scale back to original values if needed

# Plot the Equity Curve
plt.figure(figsize=(12, 6))
plt.plot(equity.index, equity['Equity'], label='Equity Curve')
plt.xlabel('Date')
plt.ylabel('Equity ($)')
plt.title('Equity Curve')
plt.legend()
plt.grid(True)
plt.show()
