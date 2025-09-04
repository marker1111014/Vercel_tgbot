import os
import logging
import re
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定 Telegram Bot
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set.")

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# 正規表達式來匹配 Twitter (X) 連結
twitter_regex = re.compile(
    r"^(https?:\/\/)?(www\.)?(x|twitter)\.com\/\S+\/status\/\d+.*$",
    re.IGNORECASE
)

async def handle_link_conversion(update: Update, context) -> None:
    """處理 Twitter/X 連結並將其轉換為 vxtwitter 連結。"""
    original_link = update.effective_message.text

    # 使用 re.sub 進行替換
    converted_link = re.sub(
        r"^(https?:\/\/)?(www\.)?(x|twitter)\.com",
        "https://vxtwitter.com",
        original_link,
        flags=re.IGNORECASE
    )

    if original_link != converted_link:
        logger.info(f"將連結轉換為: {converted_link}")
        await update.effective_message.reply_text(
            converted_link,
            reply_to_message_id=update.effective_message.message_id
        )

# 註冊處理器
application.add_handler(MessageHandler(filters.TEXT & filters.Regex(twitter_regex), handle_link_conversion))

# Flask App
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def webhook_handler():
    """處理來自 Telegram 的 Webhook 請求。"""
    if request.method == "POST":
        # 獲取並處理來自 Telegram 的 JSON 資料
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.process_update(update)
        return jsonify({"status": "ok"})
    return "Telegram Bot Webhook Endpoint"