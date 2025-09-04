from flask import Flask, request, jsonify
import logging, re, os, requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TELEGRAM_BOT_TOKEN:
    raise SystemExit("請設定環境變數 TELEGRAM_BOT_TOKEN")

twitter_regex = re.compile(
    r"^(https?:\/\/)?(www\.)?(x|twitter)\.com\/\S+\/status\/\d+.*$",
    re.IGNORECASE
)

def convert_link(text: str) -> str:
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
        message = update.get("message") or update.get("edited_message")
        if not message:
            return jsonify({"status": "ok"}), 200

        text = message.get("text")
        if not text:
            return jsonify({"status": "ok"}), 200

        converted = convert_link(text)
        if converted != text:
            chat_id = message["chat"]["id"]
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": converted}
            requests.post(url, json=payload)
    except Exception:
        app.logger.exception("handle update error")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
