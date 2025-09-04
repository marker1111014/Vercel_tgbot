# api/index.py
import re
import os
from flask import Flask, request

from telegram import Update, Bot
from telegram.ext import Application, ContextTypes, MessageHandler, filters

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # 用環境變數
bot = Bot(token=TELEGRAM_BOT_TOKEN)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Twitter regex
twitter_regex = re.compile(
    r"^(https?:\/\/)?(www\.)?(x|twitter)\.com\/\S+\/status\/\d+.*$",
    re.IGNORECASE
)

async def handle_link_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE = None):
    original_link = update.effective_message.text
    converted_link = re.sub(
        r"^(https?:\/\/)?(www\.)?(x|twitter)\.com",
        "https://vxtwitter.com",
        original_link,
        flags=re.IGNORECASE
    )
    if original_link != converted_link:
        await bot.send_message(
            chat_id=update.effective_message.chat_id,
            text=converted_link,
            reply_to_message_id=update.effective_message.message_id
        )

@app.route("/api/index", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    if update.effective_message and twitter_regex.match(update.effective_message.text):
        # 必須跑在async loop裡
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(handle_link_conversion(update))
    return "ok"
