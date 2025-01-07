'''
RANK 2
Return (%): 200.46%
Sharpe Ratio: 0.798
Win Rate (%): 55.77%
Profit Factor: 2.16
'''

# not tested.

'''
Strategy Performance Metrics:
----------------------------------------
Start                     2024-10-01 00:00:00
End                       2025-01-01 01:00:00
Duration                  92 days 00:00:00
Exposure Time [%]         100.000000
Equity Final [$]            3.004617
Equity Peak [$]             4.030656
Return [%]                200.461681 <-
Buy & Hold Return [%]     175.542117
Return (Ann.) [%]         549.090690
Volatility (Ann.) [%]     251.076802
Sharpe Ratio                0.798408 <-
Sortino Ratio               2.904416
Calmar Ratio                7.251039
Max. Drawdown [%]          27.645927
Avg. Drawdown [%]           6.707500
Max. Drawdown Duration    16 days 00:00:00
Avg. Drawdown Duration    1 days 00:00:00
# Trades                          52 <-
Win Rate [%]               55.769231 <-
Best Trade [%]            100.926987
Worst Trade [%]           -16.548938
Avg. Trade [%]              3.018970
Max. Trade Duration       5 days 00:00:00
Avg. Trade Duration       1 days 00:00:00
Profit Factor               2.163162
Expectancy [%]              2.888220
SQN                         1.376430
'''


import pandas as pd
import numpy as np
from datetime import datetime
import talib

class RSIDivergenceTOSMAStrategy:
    def __init__(self, period_tma=20, period_rsi=14):
        self.period_tma = period_tma
        self.period_rsi = period_rsi
        
    def calculate_tma(self, data, period):
        """Calculate Triangular Moving Average"""
        sma1 = data.rolling(window=period).mean()
        return sma1.rolling(window=period).mean()
    
    def calculate_osma(self, data):
        """Calculate OSMA (Moving Average of Oscillator)"""
        ema12 = talib.EMA(data, timeperiod=12)
        ema26 = talib.EMA(data, timeperiod=26)
        macd = ema12 - ema26
        signal = talib.EMA(macd, timeperiod=9)
        return macd - signal
    
    def detect_rsi_divergence(self, price, rsi):
        """Detect bullish and bearish RSI divergences"""
        bullish_div = []
        bearish_div = []
        
        for i in range(2, len(price)):
            # Bullish divergence: Lower price lows but higher RSI lows
            if (price[i] < price[i-1] and price[i-1] < price[i-2] and 
                rsi[i] > rsi[i-1] and rsi[i-1] > rsi[i-2]):
                bullish_div.append(1)
            else:
                bullish_div.append(0)
                
            # Bearish divergence: Higher price highs but lower RSI highs
            if (price[i] > price[i-1] and price[i-1] > price[i-2] and 
                rsi[i] < rsi[i-1] and rsi[i-1] < rsi[i-2]):
                bearish_div.append(1)
            else:
                bearish_div.append(0)
                
        # Pad the first two values
        bullish_div = [0, 0] + bullish_div[:-2]
        bearish_div = [0, 0] + bearish_div[:-2]
        
        return pd.Series(bullish_div), pd.Series(bearish_div)
    
    def find_swing_points(self, data, window=5):
        """Find swing highs and lows"""
        highs = []
        lows = []
        
        for i in range(window, len(data) - window):
            if all(data[i] > data[i-j] for j in range(1, window+1)) and \
               all(data[i] > data[i+j] for j in range(1, window+1)):
                highs.append(data[i])
            else:
                highs.append(np.nan)
                
            if all(data[i] < data[i-j] for j in range(1, window+1)) and \
               all(data[i] < data[i+j] for j in range(1, window+1)):
                lows.append(data[i])
            else:
                lows.append(np.nan)
                
        # Pad the edges
        pad = [np.nan] * window
        highs = pad + highs + pad
        lows = pad + lows + pad
        
        return pd.Series(highs), pd.Series(lows)
    
    def backtest(self, data):
        """Perform backtesting on the strategy"""
        df = data.copy()
        
        # Calculate indicators
        df['TMA'] = self.calculate_tma(df['Close'], self.period_tma)
        df['OSMA'] = self.calculate_osma(df['Close'])
        df['RSI'] = talib.RSI(df['Close'], timeperiod=self.period_rsi)
        
        # Calculate three TMA lines
        df['TMA_Blue'] = self.calculate_tma(df['Close'], 10)
        df['TMA_Green'] = self.calculate_tma(df['Close'], 20)
        df['TMA_Red'] = self.calculate_tma(df['Close'], 30)
        
        # Detect RSI divergences
        df['Bullish_Div'], df['Bearish_Div'] = self.detect_rsi_divergence(df['Close'], df['RSI'])
        
        # Find swing points for stop loss
        df['Swing_Highs'], df['Swing_Lows'] = self.find_swing_points(df['Close'])
        
        # Initialize trading signals
        df['Signal'] = 0  # 1 for long, -1 for short, 0 for no position
        df['Stop_Loss'] = np.nan
        df['Take_Profit_1'] = np.nan  # 2x stop loss
        df['Take_Profit_2'] = np.nan  # 3x stop loss
        
        # Generate trading signals
        for i in range(1, len(df)):
            # Long signal conditions
            if (df['TMA_Blue'].iloc[i] > df['TMA_Green'].iloc[i] and 
                df['TMA_Blue'].iloc[i-1] <= df['TMA_Green'].iloc[i-1] and
                df['Close'].iloc[i] > df['TMA_Green'].iloc[i] and
                df['Bullish_Div'].iloc[i]):
                
                df.loc[df.index[i], 'Signal'] = 1
                # Set stop loss at recent swing low
                recent_lows = df['Swing_Lows'].iloc[max(0, i-20):i]
                if not recent_lows.isna().all():
                    stop_loss = recent_lows.dropna().iloc[-1]
                    df.loc[df.index[i], 'Stop_Loss'] = stop_loss
                    # Set take profits
                    price_diff = df['Close'].iloc[i] - stop_loss
                    df.loc[df.index[i], 'Take_Profit_1'] = df['Close'].iloc[i] + (2 * price_diff)
                    df.loc[df.index[i], 'Take_Profit_2'] = df['Close'].iloc[i] + (3 * price_diff)
            
            # Short signal conditions
            elif (df['TMA_Blue'].iloc[i] < df['TMA_Red'].iloc[i] and 
                  df['TMA_Blue'].iloc[i-1] >= df['TMA_Red'].iloc[i-1] and
                  df['Close'].iloc[i] < df['TMA_Red'].iloc[i] and
                  df['Bearish_Div'].iloc[i]):
                
                df.loc[df.index[i], 'Signal'] = -1
                # Set stop loss at recent swing high
                recent_highs = df['Swing_Highs'].iloc[max(0, i-20):i]
                if not recent_highs.isna().all():
                    stop_loss = recent_highs.dropna().iloc[-1]
                    df.loc[df.index[i], 'Stop_Loss'] = stop_loss
                    # Set take profits
                    price_diff = stop_loss - df['Close'].iloc[i]
                    df.loc[df.index[i], 'Take_Profit_1'] = df['Close'].iloc[i] - (2 * price_diff)
                    df.loc[df.index[i], 'Take_Profit_2'] = df['Close'].iloc[i] - (3 * price_diff)
        
        return df

    def calculate_metrics(self, results):
        """Calculate detailed performance metrics"""
        signals = results[results['Signal'] != 0].copy()
        
        # Basic trade statistics
        start_date = results.index[0]
        end_date = results.index[-1]
        duration = (end_date - start_date).days
        
        # Calculate returns and drawdowns
        signals['Returns'] = signals['Close'].pct_change()
        signals['Cumulative_Returns'] = (1 + signals['Returns']).cumprod()
        signals['Running_Max'] = signals['Cumulative_Returns'].cummax()
        signals['Drawdown'] = (signals['Running_Max'] - signals['Cumulative_Returns']) / signals['Running_Max'] * 100
        
        # Calculate trade durations
        signals['Duration'] = signals.index.to_series().diff()
        
        # Calculate metrics
        total_return = (signals['Cumulative_Returns'].iloc[-1] - 1) * 100 if len(signals) > 0 else 0
        volatility = signals['Returns'].std() * np.sqrt(252) * 100  # Annualized
        max_drawdown = signals['Drawdown'].max()
        avg_drawdown = signals['Drawdown'].mean()
        max_drawdown_duration = signals['Drawdown'].value_counts().max() if len(signals) > 0 else 0
        
        # Calculate profit factor and other ratios
        winning_trades = signals[signals['Returns'] > 0]
        losing_trades = signals[signals['Returns'] < 0]
        
        total_wins = len(winning_trades)
        total_losses = len(losing_trades)
        
        win_rate = (total_wins / len(signals)) * 100 if len(signals) > 0 else 0
        
        avg_win = winning_trades['Returns'].mean() * 100 if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['Returns'].mean() * 100 if len(losing_trades) > 0 else 0
        
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        # Calculate Sortino and Calmar ratios
        negative_returns = signals[signals['Returns'] < 0]['Returns']
        downside_std = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else 1
        sortino_ratio = (total_return / 100) / downside_std if downside_std != 0 else 0
        calmar_ratio = (total_return / 100) / (max_drawdown / 100) if max_drawdown != 0 else 0
        
        # Calculate SQN (System Quality Number)
        sqn = np.sqrt(len(signals)) * (signals['Returns'].mean() / signals['Returns'].std()) if len(signals) > 0 else 0
        
        metrics = {
            'Start': start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'End': end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'Duration': f"{duration} days 00:00:00",
            'Exposure Time [%]': 100.0,  # Assuming full exposure
            'Equity Final [$]': signals['Cumulative_Returns'].iloc[-1] if len(signals) > 0 else 1,
            'Equity Peak [$]': signals['Running_Max'].max() if len(signals) > 0 else 1,
            'Return [%]': total_return,
            'Buy & Hold Return [%]': ((results['Close'].iloc[-1] / results['Close'].iloc[0]) - 1) * 100,
            'Return (Ann.) [%]': total_return * (252 / duration) if duration > 0 else 0,
            'Volatility (Ann.) [%]': volatility,
            'Sharpe Ratio': total_return / volatility if volatility != 0 else 0,
            'Sortino Ratio': sortino_ratio,
            'Calmar Ratio': calmar_ratio,
            'Max. Drawdown [%]': max_drawdown,
            'Avg. Drawdown [%]': avg_drawdown,
            'Max. Drawdown Duration': f"{int(max_drawdown_duration)} days 00:00:00",
            'Avg. Drawdown Duration': f"{int(signals['Duration'].mean().days)} days 00:00:00" if len(signals) > 0 else "0 days",
            '# Trades': len(signals),
            'Win Rate [%]': win_rate,
            'Best Trade [%]': signals['Returns'].max() * 100 if len(signals) > 0 else 0,
            'Worst Trade [%]': signals['Returns'].min() * 100 if len(signals) > 0 else 0,
            'Avg. Trade [%]': signals['Returns'].mean() * 100 if len(signals) > 0 else 0,
            'Max. Trade Duration': f"{signals['Duration'].max().days} days 00:00:00" if len(signals) > 0 else "0 days",
            'Avg. Trade Duration': f"{int(signals['Duration'].mean().days)} days 00:00:00" if len(signals) > 0 else "0 days",
            'Profit Factor': profit_factor,
            'Expectancy [%]': (win_rate * avg_win + (100 - win_rate) * avg_loss) / 100,
            'SQN': sqn
        }
        
        return metrics

# Main execution
if __name__ == "__main__":
    # Load the data
    data = pd.read_csv('/Users/kluless/freedom/backtest/rsi/Zata1h.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)

    # Initialize and run the strategy
    strategy = RSIDivergenceTOSMAStrategy()
    results = strategy.backtest(data)
    
    # Calculate and print metrics
    metrics = strategy.calculate_metrics(results)
    
    # Print metrics in the desired format
    print("\nStrategy Performance Metrics:")
    print("-" * 40)
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key:<25} {value:>10.6f}")
        else:
            print(f"{key:<25} {value:>10}")