'''
RANK 3
Return (%): 77.61%
Sharpe Ratio: 1.431 (highest among the strategies)
Win Rate (%): 69.23%
Profit Factor: 4.74
'''

# Good.

'''
Open      0
High      0
Low       0
Close     0
Volume    0
dtype: int64
Start                     2024-01-01 00:00:00
End                       2024-07-10 12:00:00
Duration                    191 days 12:00:00
Exposure Time [%]                   15.885417 <-
Equity Final [$]                 17761.022016
Equity Peak [$]                  17761.022016
Return [%]                           77.61022 <-
Buy & Hold Return [%]               42.251044
Return (Ann.) [%]                  198.022444
Volatility (Ann.) [%]              138.366876
Sharpe Ratio                         1.431141 <-
Sortino Ratio                        9.444662
Calmar Ratio                        20.144403
Max. Drawdown [%]                   -9.830147
Avg. Drawdown [%]                   -5.389158
Max. Drawdown Duration       63 days 12:00:00
Avg. Drawdown Duration       19 days 03:00:00
# Trades                                   13 <-
Win Rate [%]                        69.230769 <-
Best Trade [%]                      23.776998
Worst Trade [%]                      -7.84024
Avg. Trade [%]                       4.519904
Max. Trade Duration           6 days 12:00:00
Avg. Trade Duration           2 days 00:00:00
Profit Factor                        4.738021
Expectancy [%]                          4.893
SQN                                  1.870685
_strategy                          DMITrategy
_equity_curve                             ...
_trades                       Size  EntryB...
dtype: object
'''

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib

# Load your CSV data
BTCUSDT_data = pd.read_csv('/Users/kluless/freedom/backtest/DMIT/Zata12h.csv', index_col='Date', parse_dates=True)

# Check for NaN values
print(BTCUSDT_data.isna().sum())

class DMITrategy(Strategy):
    def init(self):
        # Set up the indicators
        self.high = self.data.High
        self.low = self.data.Low
        self.close = self.data.Close
        self.open = self.data.Open
        
        # Using Talib to calculate +DI and -DI
        self.plus_di = self.I(talib.PLUS_DI, self.high, self.low, self.close, timeperiod=14)
        self.minus_di = self.I(talib.MINUS_DI, self.high, self.low, self.close, timeperiod=14)

    def next(self):
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        recent_high = max(self.data.High[-2], high)
        recent_low = min(self.data.Low[-2], low)
        
        # Check if a bullish crossover happened and if the recent candle is bullish
        is_bullish = self.close[-1] > self.open[-1]
        if crossover(self.plus_di, self.minus_di) and is_bullish:
            self.buy(sl=recent_low, tp=price + (price - recent_low) * 2)  # for Risk/Reward of 1:2

        # Check if a bearish crossover happened and if the recent candle is bearish
        is_bearish = self.close[-1] < self.open[-1]
        if crossover(self.minus_di, self.plus_di) and is_bearish:
            self.sell(sl=recent_high, tp=price - (recent_high - price) * 2)  # for Risk/Reward of 1:2

        # Exit logic is handled by the stop loss and take profit orders

# Ensure the DataFrame 'BTCUSDT_data' contains the correct datetime index and required columns
bt = Backtest(BTCUSDT_data, DMITrategy,
              cash=10000, commission=.002,
              exclusive_orders=True)

stats = bt.run()
print(stats)