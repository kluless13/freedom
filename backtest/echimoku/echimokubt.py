'''
RANK 6
Return (%): 16.58%
Sharpe Ratio: 1.734 (second-highest Sharpe Ratio)
Win Rate (%): 82.35%
Profit Factor: 2.65
'''

# Fine.

'''
Start                     2024-01-01 00:00:00
End                       2024-06-04 00:00:00
Duration                    155 days 00:00:00 <-
Exposure Time [%]                    6.766917 <-
Equity Final [$]                 11658.329237
Equity Peak [$]                  11658.329237
Return [%]                          16.583292 <-
Buy & Hold Return [%]               -4.017331
Return (Ann.) [%]                   43.189737
Volatility (Ann.) [%]               24.911066
Sharpe Ratio                         1.733757 <-
Sortino Ratio                         4.04015
Calmar Ratio                         8.129952
Max. Drawdown [%]                   -5.312422
Avg. Drawdown [%]                   -2.443126
Max. Drawdown Duration       30 days 20:00:00
Avg. Drawdown Duration        6 days 05:00:00
# Trades                                   17 <-
Win Rate [%]                        82.352941 <-
Best Trade [%]                       1.917656
Worst Trade [%]                     -5.074285
Avg. Trade [%]                       0.907024
Max. Trade Duration           2 days 00:00:00
Avg. Trade Duration           0 days 11:00:00
Profit Factor                          2.6552
Expectancy [%]                       0.927018
SQN                                  1.855014
_strategy                            ECHIMOKU
_equity_curve                             ...
_trades                       Size  EntryB...
dtype: object
'''

from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA
import pandas as pd

# Assuming OHLCV data is in the 'data' DataFrame and Ichimoku Oscillator is computed and added to 'data'

class ECHIMOKU(Strategy):
    
    def init(self):
        super().init()
        self.mm1 = self.I(SMA, self.data.Close, 18)
        self.mm2 = self.I(SMA, self.data.Close, 29)
        # Assuming ichimoku_oscillator function calculates the Ichimoku Oscillator and color
        self.ichimoku_oscillator_green = self.I(ichimoku_oscillator, self.data, 'green')
        self.ichimoku_oscillator_histo = self.I(ichimoku_oscillator, self.data, 'histo')

    def next(self):
        price = self.data.Close[-1]
        if not self.position:
            if (
                crossover(self.mm1, self.mm2) and
                price > self.mm1[-1] and
                price > self.mm2[-1] and
                self.ichimoku_oscillator_green[-1] and
                self.ichimoku_oscillator_histo[-1] > 0
            ):
                # Long entry
                self.buy(sl=self.data.Low[-21:].min(), tp=calculate_takeprofit(price, is_long=True))
            elif (
                crossover(self.mm2, self.mm1) and
                price < self.mm1[-1] and
                price < self.mm2[-1] and
                not self.ichimoku_oscillator_green[-1] and
                self.ichimoku_oscillator_histo[-1] < 0
            ):
                # Short entry
                self.sell(sl=self.data.High[-21:].max(), tp=calculate_takeprofit(price, is_long=False))
        else:
            if self.position.is_long and (
                price < self.mm1[-1] or
                price < self.mm2[-1]
            ):
                self.position.close()
            elif self.position.is_short and (
                price > self.mm1[-1] or
                price > self.mm2[-1]
            ):
                self.position.close()

# Dummy functions for Ichimoku oscillator calculation and takeprofit calculation - They should be replaced with actual implementations
def ichimoku_oscillator(data, mode):
    if mode == 'green':
        return data.Close > data.Open
    elif mode == 'histo':
        return data.Close - data.Open

def calculate_takeprofit(price, is_long=True):
    if is_long:
        return price * 1.02
    else:
        return price * 0.98  # Adjust the multiplier according to your strategy

# Load your own CSV data
data = pd.read_csv('/Users/kluless/freedom/backtest/echimoku/DATA.csv', parse_dates=True, index_col='Date')

# Initialize and run backtest
bt = Backtest(data, ECHIMOKU, cash=10000, commission=.002, exclusive_orders=True)
stats = bt.run()
print(stats)