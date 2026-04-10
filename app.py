import threading
import os
import asyncio
import logging
from flask import Flask
from handlers import bot, dp  # Aapke handlers.py se import ho raha hai

# Logging setup
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running perfectly!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    """Bot ko background thread mein chalane ke liye."""
    logging.info("Starting Aiogram Polling...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # handle_signals=False sabse important hai threading ke liye
    try:
        loop.run_until_complete(dp.start_polling(bot, handle_signals=False))
    except Exception as e:
        logging.error(f"Bot Error: {e}")

if __name__ == '__main__':
    # 1. Bot ko alag thread mein shuru karein
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 2. Flask ko main thread mein shuru karein (Render ke liye)
    # Render PORT variable provide karta hai, default 5000 rakha hai
    port = int(os.environ.get("PORT", 5000))
    
    logging.info(f"Flask app starting on port {port}")
    # host='0.0.0.0' hona zaroori hai Render connectivity ke liye
    app.run(host='0.0.0.0', port=port)
