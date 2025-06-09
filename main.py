
import os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import time
from keep_alive_script import keep_alive

ALPHA_KEY = os.getenv("API_ALPHA_KEY")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

def get_data(symbol):
    url = (f"https://www.alphavantage.co/query?"
           f"function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&outputsize=compact&apikey={ALPHA_KEY}")
    r = requests.get(url).json()
    candles = list(r.get("Time Series (60min)", {}).values())[:50]
    return [float(c["4. close"]) for c in candles]

def rsi(closes):
    gains = [closes[i] - closes[i-1] for i in range(1, len(closes)) if closes[i] > closes[i-1]]
    losses = [closes[i-1] - closes[i] for i in range(1, len(closes)) if closes[i] < closes[i-1]]
    avg_gain = sum(gains)/14 if len(gains)>=14 else sum(gains)/max(1,len(gains))
    avg_loss = sum(losses)/14 if len(losses)>=14 else sum(losses)/max(1,len(losses))
    rs = avg_gain/avg_loss if avg_loss != 0 else float('inf')
    return 100 - (100 / (1 + rs))

def ema(closes, period):
    k = 2/(period+1)
    ema_val = closes[0]
    for price in closes[1:]:
        ema_val = price*k + ema_val*(1-k)
    return ema_val

def fibonacci_zonas(closes):
    high, low = max(closes), min(closes)
    diff = high - low
    sup = high - diff*0.618
    res = high - diff*0.236
    return sup, res

async def alerta(context: ContextTypes.DEFAULT_TYPE):
    ativos = {"BTC": "BTCUSD", "SPY": "SPY"}
    for nome, ticker in ativos.items():
        try:
            closes = get_data(ticker)
            r = rsi(closes)
            e20 = ema(closes, 20)
            e50 = ema(closes, 50)
            sup, res = fibonacci_zonas(closes)
            now = closes[0]

            entrar = (r < 30 or e20 > e50 or abs(now - sup)/now < 0.01)
            sair = (r > 70 or e20 < e50 or abs(now - res)/now < 0.01)

            if entrar:
                prob = "Alta" if e20 > e50 and r < 35 else "Média"
                entry = round(now * 0.985, 2)
                exitp = round(now * 1.03, 2)
                msg = (f"📊 [{nome}]\n"
                       f"🟢 Entrada: {entry} / 🔴 Saída: {exitp} / 🎯 Resist: {res:.2f}\n"
                       f"Prob: {prob}")
                await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            elif sair:
                msg = f"📊 [{nome}] ⚠️ Sinal de saída! RSI={r:.1f}, EMA20<{e50:.2f}"
                await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

        except Exception as e:
            print(f"Erro ao analisar {nome}: {e}")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🚨 Teste de alerta FIRE!")


if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))

    fire_hours = [time(h, 0) for h in range(9, 24, 2)]  # 9,11,...23
    for hora in fire_hours:
        app.job_queue.run_daily(alerta, time=hora)

    app.run_polling()
