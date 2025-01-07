Fib x HFT scalping

### **1. Fibonacci-Based Strategies**

#### **A. Fibonacci Retracement Strategy** :white_check_mark: [https://github.com/kluless13/freedom/blob/main/backtest/fib/fibretrace2.py]
- **Goal**: Buy at key Fibonacci support levels during retracements in an uptrend and sell at resistance levels in a downtrend.
- **Implementation**:
  - Identify major swing highs and lows over a given lookback period.
  - Calculate Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%).
  - Use price action or indicators like RSI for confirmation.

---

#### **B. Fibonacci Breakout Strategy** :white_check_mark: [https://github.com/kluless13/freedom/blob/main/backtest/fib/fibbreakout.py]
- **Goal**: Trade breakouts above the 61.8% retracement level or below the 38.2% level.
- **Implementation**:
  - Wait for the price to consolidate near Fibonacci levels.
  - Trade when the price breaks and closes decisively beyond key levels.
  - Use ATR for dynamic stop-loss and take-profit levels.

---

#### **C. Fibonacci Confluence Strategy** :white_check_mark: [https://github.com/kluless13/freedom/blob/main/backtest/fib/fibcon.py]
- **Goal**: Combine Fibonacci retracement/extensions with other indicators for high-confidence trades.
- **Implementation**:
  - Identify Fibonacci retracement levels.
  - Look for confluence with:
    - Moving averages (e.g., 200 EMA).
    - Oscillators like RSI or MACD.
    - Price action signals (e.g., pin bars, engulfing candles).

---

### **2. High-Frequency Trading (HFT) Strategies**

#### **A. Scalping with Moving Averages**
- **Goal**: Enter quick trades on short-term trend reversals.
- **Implementation**:
  - Use fast EMAs (e.g., 5 and 15 EMAs).
  - Buy when the 5 EMA crosses above the 15 EMA; sell on a reversal.

---

#### **B. VWAP Reversion Strategy**
- **Goal**: Trade price deviations from VWAP.
- **Implementation**:
  - Use Volume Weighted Average Price (VWAP) as a dynamic support/resistance level.
  - Buy when the price falls significantly below VWAP; sell on reversion.

---

#### **C. Momentum Oscillator Scalping**
- **Goal**: Use oscillators for overbought/oversold conditions on short timeframes.
- **Implementation**:
  - Use RSI or stochastic oscillators with short periods (5 or 10).
  - Enter trades on overbought (>70) or oversold (<30) signals.

---

#### **D. Order Flow Analysis**
- **Goal**: Trade based on volume and order book data.
- **Implementation**:
  - Monitor for unusual volume spikes or imbalances in buy/sell orders.
  - Enter trades when significant buy/sell volume occurs.

---

### **Fibonacci x Scalping Strategies for HFT**

1. **Fibonacci x Scalping Strategies for HFT**:
   - Combines Fibonacci levels with scalping techniques.
   - Aims for quick, small profits by leveraging Fibonacci retracement and extension levels during rapid market movements.

2. **Fibonacci Retracement Scalping**:
   - Uses Fibonacci retracement levels (e.g., 38.2%, 50%, 61.8%) to identify pullback levels in an existing trend.
   - Looks for quick entries and exits when price tests or bounces off these levels.

3. **Fibonacci Breakout Scalping**:
   - Focuses on breakouts beyond significant Fibonacci levels.
   - Scalps profits when price moves decisively past retracement or extension levels, signaling continuation.

4. **Fibonacci Confluence Scalping**:
   - Identifies confluence zones where multiple Fibonacci levels (from different swings) align.
   - Scalps trades when price reacts to these strong support/resistance zones.

5. **Scalping with Moving Averages + Fibonacci**:
   - Combines moving averages (e.g., EMA/SMA crossovers) with Fibonacci levels for trade confirmation.
   - Entries and exits align with moving average signals and Fibonacci support/resistance.

6. **VWAP Reversion + Fibonacci Levels**:
   - Adds VWAP (Volume Weighted Average Price) to the mix, using it as a dynamic mean-reversion indicator.
   - Trades are taken when price deviates from VWAP near key Fibonacci levels.

7. **Momentum Oscillator Scalping + Fibonacci**:
   - Incorporates momentum oscillators like RSI, Stochastic, or MACD with Fibonacci levels.
   - Uses oscillator signals (e.g., overbought/oversold) for entries/exits around Fibonacci retracement or extension levels.

8. **Order Flow Scalping + Fibonacci**:
   - Utilizes order flow analysis (e.g., order book imbalances, volume clusters) to enhance Fibonacci scalping strategies.
   - Focuses on high-probability zones with strong order flow confirmation.
---

### **Indicators for Confluence**

1. RSI (Relative Strength Index)
2. MACD (Moving Average Convergence Divergence)
3. ATR (Average True Range)
4. Volume/Volume Spikes
5. EMA (Exponential Moving Averages; e.g., 5, 15, 200)
6. VWAP (Volume Weighted Average Price)
7. Stochastic Oscillator
8. Candlestick Patterns (e.g., Pin Bars, Engulfing Candles)

---
