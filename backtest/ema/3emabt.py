'''
RANK 4
Return (%): 229.69%
Sharpe Ratio: 0.778
Win Rate (%): 50.0%
Profit Factor: 7.25
'''

# not it.

'''3 EMA Crossover Strategy


Time frame: H1 or H4.


Indicators:

1) EMA 5(fast)

2) EMA 10(medium)

3) EMA 14(slow)

Signals:

Buy signal: When fast EMA 5 cross medium EMA 10 from lower to upper and then go throough EMA 14 as shown in fig, then take buy entry.

Sell signal: When fast EMA 5 cross medium EMA 10 from upper to lower and then go through EMA 14 as shown in fig, then take sell entry.

'''

'''
Start                     2023-08-12 00:00:00
End                       2024-02-27 00:00:00
Duration                    199 days 00:00:00
Exposure Time [%]                        77.0 <-
Equity Final [$]                 329685.37144
Equity Peak [$]                  441113.49952
Return [%]                         229.685371 <-
Buy & Hold Return [%]              346.848655
Return (Ann.) [%]                  782.128617
Volatility (Ann.) [%]             1005.015524
Sharpe Ratio                         0.778225 <-
Sortino Ratio                       16.023432
Calmar Ratio                        27.210549
Max. Drawdown [%]                  -28.743581
Avg. Drawdown [%]                   -10.86739
Max. Drawdown Duration       64 days 00:00:00
Avg. Drawdown Duration       13 days 00:00:00
# Trades                                   12 <- 
Win Rate [%]                             50.0 <-
Best Trade [%]                     316.438712
Worst Trade [%]                    -12.919775
Avg. Trade [%]                      10.362605
Max. Trade Duration          81 days 00:00:00
Avg. Trade Duration          13 days 00:00:00
Profit Factor                        7.250956
Expectancy [%]                      24.611762
SQN                                  0.777357
_strategy                    ThreeEMAStrategy
_equity_curve                             ...
_trades                       Size  EntryB...
dtype: object
'''




from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import talib

class ThreeEMAStrategy(Strategy):
    
    def init(self):
        # Calculate the EMAs using talib
        self.ema_fast = self.I(talib.EMA, self.data.Close, timeperiod=5)
        self.ema_medium = self.I(talib.EMA, self.data.Close, timeperiod=10)
        self.ema_slow = self.I(talib.EMA, self.data.Close, timeperiod=14)

    def next(self):
        if crossover(self.ema_fast, self.ema_medium) and \
                self.ema_fast[-1] > self.ema_slow[-1]:
            self.buy()

        if crossover(self.ema_medium, self.ema_fast) or \
                crossover(self.ema_slow, self.ema_fast):
            self.sell()


data = pd.read_csv('/Users/kluless/freedom/backtest/ema/storage_SOL-USD1d10.csv')
data['Datetime'] = pd.to_datetime(data['Datetime'])
data.set_index('Datetime', inplace=True)
data.sort_index(inplace=True)

bt = Backtest(data, ThreeEMAStrategy, cash=100000, commission=.002,
              exclusive_orders=True)

output = bt.run()
print(output)