
# Indicators

## BB - Bollinger Bands

3 lines: middle (SMA), upper and lower band

Params:
- length: SMA samples
- std: factor, by which the standard deviation is multiplied

```
# ['BBL_5_2.0', 'BBM_5_2.0', 'BBU_5_2.0', 'BBB_5_2.0', 'BBP_5_2.0'] - [Low, SMA, Up, Bandwith, Percentage]
df = ta.bbands(self.df_min['close'], length=6, std=2.0)
col_l, col_m, col_u, col_b, col_p = list(df.columns)
```

Bearish: close > upper band -> if course is larger than the upper band
Bullish: close < lower band -> if course is smaller than the lower band




## MACD - Moving Average Convergence Divergence (MACD)

Spot changes in the strength, direction, momentum, and duration of a trend in a stock

Params:
- fast: fast moving average (typically a short-term EMA) | default = 12
- slow: slow moving average (typically a long-term EMA) | default = 26
- signal: The signal line is an EMA of the MACD line itself (the difference between the fast and slow EMAs) | default = 9

```
# ['MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9'] - [MACD, Histogram (Diff), Signal]
df = ta.macd(df['close'], fast=12, slow=26, signal=9)
col_MACD, coll_diff, col_signal = list(df.columns)
```

buy: when the MACD crosses the signal line from bottom to top
sell: when the MACD crosses the signal line from top to bottom




## RSI - Relative Strength Index

Params:
- length: period | default = 14 | 7, 9, 25, 38
- (border upper | default = 70)
- (border lower | default = 30)

```
# ['RSI_14', 'border_lower_30', 'border_upper_70']
df = ta.rsi(df['close'], length=14)
col_RSI, col_bl, col_bu = list(df.columns)
```

sell: RSI >= 70 -> too high -> sell | crossing from above under 70
buy: SI <= 30 -> too low -> buy | crossing from below over 30