# main.py

import time
import requests
import pandas as pd
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, COINS, INTERVAL_MINUTES
from strategy import fire_trader_strategy

def fetch_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {'vs_currency': 'usd', 'days': '2', 'interval': 'hourly'}
    res = requests.get(url, params=params).json()

    if 'prices' not in res or 'total_volumes' not in res:
        print(f"Erro: CoinGecko não retornou dados para {coin_id}")
        return pd.DataFrame()

    prices = res['prices']
    volumes = res['total_volumes']
    df = pd.DataFrame({
        'time': [p[0] for p in prices],
        'close': [p[1] for p in prices],
        'volume': [v[1] for v in volumes]
    })
    return df

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': message})

def main():
    while True:
        for coin_id, symbol in COINS.items():
            data = fetch_data(coin_id)
            if not data.empty:
                signal = fire_trader_strategy(data)
                if signal:
                    if signal['type'] == 'buy':
                        msg = f'''
COMPRA {symbol}
Entrada: ${signal['entry']}
Alvo: ${signal['target']}
Stop: ${signal['stop']}
Análise: {signal['summary']}
'''.strip()
                    elif signal['type'] == 'sell':
                        msg = f'''
VENDA {symbol}
Saída recomendada: ${signal['exit']}
Análise: {signal['summary']}
'''.strip()
                    send_telegram_message(msg)
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
