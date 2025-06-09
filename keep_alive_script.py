
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🔥 Bot ativo!")

async def alerta_teste(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=int(os.getenv("TELEGRAM_CHAT_ID")),
        text="📈 [ALERTA DE TESTE] BTC swing: Entrada 104 500 | SL: 101 500 | TP: 110 000"
    )
def keep_alive():
    from flask import Flask
    from threading import Thread

    app = Flask('')

    @app.route('/')
    def home():
        return "Bot está vivo!"

    def run():
        app.run(host='0.0.0.0', port=8080)

    t = Thread(target=run)
    t.start()
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.job_queue.run_once(alerta_teste, 5)  # Envia alerta após 5 segundos
    print("BOT ONLINE")
    app.run_polling()