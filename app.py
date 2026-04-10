import threading
import os
import asyncio
from flask import Flask
from handlers import bot, dp # Import bot and dp from handlers

app = Flask(__name__)

@app.route('/')
def hello():
    return "Welcome Bot is Running!"

# Start aiogram polling in a separate thread to keep Flask responsive
def run_bot():
    """Run the aiogram bot polling in a separate event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Note: run_polling is tricky in threads, we use the raw dp.start_polling
    # A simpler approach is dp.run_polling(bot) if using modern aiogram
    # Let's keep it simple with standard polling and modern aiogram
    logging.info("Aiogram thread started...")
    loop.run_until_complete(dp.start_polling(bot))

if __name__ == '__main__':
    # Start the bot thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Flask runs on the port specified by Render
    port = int(os.environ.get("PORT", 5000)) # Render will set PORT env var
    # Bind to 0.0.0.0 is critical for Render!
    app.run(host='0.0.0.0', port=port)
