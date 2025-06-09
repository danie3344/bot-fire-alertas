# indicators.py

import pandas as pd

def rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ema(data, span):
    return data['close'].ewm(span=span, adjust=False).mean()

def macd(data):
    ema12 = ema(data, 12)
    ema26 = ema(data, 26)
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    return macd_line, signal_line

def bollinger_bands(data, period=20):
    sma = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper, lower
