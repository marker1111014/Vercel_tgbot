from flask import Flask, request, jsonify
import logging, re, os, requests

# 建立應用與日誌
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# 從環境變數取得 Token（請放入 Vercel 的環境變數設定）
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# 正規表達式：抓取 Twitter/X 連結的狀態
twitter_regex = re.compile(
    r"^(https?:\/\/)?(www\.)?(x|twitter)\.com\/\S+\/status\/\d+.*$",
    re.IGNORECASE
)

def convert_link(text: str) -> str:
    # 將 x.twitter.com 替換為 vxtwitter.com
    return re.sub(
        r"^(https?:\/\/)?(www\.)?(x|twitter)\.com",
        "https://vxtwitter.com",
        text,
        flags=re.IGNORECASE
    )

@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    if not update:
        return jsonify({"status": "ok"}), 200

    try:
        # 取得訊息內容
        message = update.get("message") or update.get("edited_message")
        if not message:
            return jsonify({"status": "ok"}), 200

        text = message.get("text")
        if not text:
            return jsonify({"status": "ok"}), 200

        converted_text = convert_link(text)
        if converted_text != text:
            chat_id = message["chat"]["id"]
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": converted_text}
            requests.post(url, json=payload)
    except Exception as e:
        app.logger.exception("Error handling update")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    # 本機測試用
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
