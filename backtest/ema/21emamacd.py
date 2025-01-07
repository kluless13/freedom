'''
RANK 1
Return (%): 334.99%
Sharpe Ratio: 0.806
Win Rate (%): 33.33% (low win rate, but large profit factor compensates)
Profit Factor: 24.99
'''

# not it.

'''21 EMA & MACD Strategy

Time Frames: 1H above

Required Indicators
21 EMA
MACD indicators

Buy Setup Rules
✪ First market price needs to cross 21 EMA from lower to upper.
✪ When 21 EMA upside breakout complete, then look at MACD indicator
✪ At the same time, if MACD stay above 0.0 level, then open buy entry.

Sell Setup Rules
✪ First market price needs to cross 21 EMA from upper to lower
✪ When 21 EMA downside breakout complete, then look at MACD indicator
✪ At the same time, if MACD stay below 0.0 level, then open sell entry.

'''
'''
Start                     2023-08-12 00:00:00
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        79.5
Equity Final [$]                 434986.35872
Equity Peak [$]                  482125.40456
Return [%]                         334.986359 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                 1362.911448
Volatility (Ann.) [%]             1690.064148
Sharpe Ratio                         0.806426 <-
Sortino Ratio                       27.137105
Calmar Ratio                        43.920761
Max. Drawdown [%]                  -31.031144
Avg. Drawdown [%]                   -9.097333
Max. Drawdown Duration       64 days 00:00:00
Avg. Drawdown Duration       12 days 00:00:00
# Trades                                    6 <-
Win Rate [%]                        33.333333 <-
Best Trade [%]                     347.412586
Worst Trade [%]                    -12.673907
Avg. Trade [%]                      27.768754
Max. Trade Duration          87 days 00:00:00
Avg. Trade Duration          27 days 00:00:00
Profit Factor                       24.989066
Expectancy [%]                      57.719248
SQN                                  1.108427
_strategy                     EMAMACDStrategy
_equity_curve                             ...
_trades                      Size  EntryBa...
dtype: object
'''

import pandas as pd
import talib as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class EMAMACDStrategy(Strategy):
    def init(self):
        self.ema21 = self.I(ta.EMA, self.data.Close, timeperiod=21)
        self.macd, self.macdsignal, self.macdhist = self.I(ta.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)

    def next(self):
        if crossover(self.data.Close, self.ema21) and self.macd[-1] > 0:
            self.buy()
        elif crossover(self.ema21, self.data.Close) and self.macd[-1] < 0:
            self.sell()

# Load and preprocess data
data = pd.read_csv('/Users/kluless/freedom/backtest/21emamacd/storage_SOL-USD1d10.csv')
data['Datetime'] = pd.to_datetime(data['Datetime'])
data.set_index('Datetime', inplace=True)
data.sort_index(inplace=True)


# Define backtest parameters
bt = Backtest(
    data,
    EMAMACDStrategy,
    cash=100000,
    commission=0.002,
    exclusive_orders=True
)

# Run the backtest
output = bt.run()

# Print the output
print(output)