# strategy.py

from indicators import rsi, macd, ema, bollinger_bands

def fire_trader_strategy(data):
    score = 0
    analysis = []

    rsi_val = rsi(data).iloc[-1]
    macd_line, signal_line = macd(data)
    ema9 = ema(data, 9)
    ema21 = ema(data, 21)
    upper, lower = bollinger_bands(data)
    close = data['close'].iloc[-1]
    volume = data['volume'].iloc[-1]
    avg_volume = data['volume'].rolling(10).mean().iloc[-1]

    if rsi_val < 30:
        score += 2
        analysis.append(f"RSI baixo ({rsi_val:.2f})")
    if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] < signal_line.iloc[-2]:
        score += 2
        analysis.append("MACD cruzamento bullish")
    if ema9.iloc[-1] > ema21.iloc[-1]:
        score += 1
        analysis.append("EMA9 acima da EMA21")
    if close < lower.iloc[-1]:
        score += 1
        analysis.append("Preço abaixo da Bollinger inferior")
    if volume > avg_volume:
        score += 1
        analysis.append("Volume acima da média")

    if score >= 5:
        entry = round(close * 0.995, 4)
        target = round(close * 1.08, 4)
        stop = round(close * 0.96, 4)
        return {
            'type': 'buy',
            'entry': entry,
            'target': target,
            'stop': stop,
            'rsi': round(rsi_val, 2),
            'analysis': analysis
        }

    if rsi_val > 70 or (macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] > signal_line.iloc[-2]):
        return {
            'type': 'sell',
            'rsi': round(rsi_val, 2),
            'exit': round(close, 4)
        }

    return None
