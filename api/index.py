import logging
import re
import os
import requests
from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("請在環境變數中設定 TELEGRAM_BOT_TOKEN")
    # 這裡不 raise，讓服務繼續暴露，以便你能看日誌排查

# 用來尋找訊息中的 Twitter/X 連結
twitter_link_pattern = re.compile(
    r"(https?:\/\/)?(www\.)?(x|twitter)\.com\/\S+",
    re.IGNORECASE
)

def replace_with_vxtwitter(url: str) -> str:
    return re.sub(
        r"^(https?:\/\/)?(www\.)?(x|twitter)\.com",
        "https://vxtwitter.com",
        url,
        flags=re.IGNORECASE
    )

def convert_text(text: str) -> str:
    # 對訊息中的所有符合的連結做替換
    def repl(match):
        url = match.group(0)
        return replace_with_vxtwitter(url)

    return twitter_link_pattern.sub(repl, text)

def post_send_message(chat_id: int, text: str, reply_to_message_id: int = None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id

    r = requests.post(url, json=payload)
    logger.info(f"sendMessage 回應: {r.status_code} {r.text}")

@app.route("/api/index", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logger.info(f"接收到的更新：{data}")

        if not data:
            return "OK", 200

        message = data.get("message")
        if not message:
            # 也可能是其他更新類型，暫時不處理
            return "OK", 200

        chat_id = message.get("chat", {}).get("id")
        message_id = message.get("message_id")
        text = message.get("text", "")

        if not chat_id or not text:
            return "OK", 200

        converted_text = convert_text(text)
        if converted_text != text:
            logger.info(f"轉換前: {text}")
            logger.info(f"轉換後: {converted_text}")
            post_send_message(chat_id, converted_text, message_id)

        return "OK", 200
    except Exception as e:
        logger.exception("Webhook 執行時發生錯誤")
        # 即使發生錯誤，也回 200，避免 Telegram 反覆重送
        return "OK", 200
