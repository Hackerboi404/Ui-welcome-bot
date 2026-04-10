import threading
import os
import asyncio
import logging
from flask import Flask
from handlers import bot, dp

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Alive!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    logging.info("Starting Aiogram Polling...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Conflict se bachne ke liye purane updates skip karna zaroori hai
    loop.run_until_complete(dp.start_polling(bot, handle_signals=False, skip_updates=True))

if __name__ == '__main__':
    # Bot ko background thread mein start karein
    threading.Thread(target=run_bot, daemon=True).start()

    # Render ka port bind karein
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host='0.0.0.0', port=port)
