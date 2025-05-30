#main.py
import os
from telegram_bot import app  # importa Application ya construida
from logger_config import setup_logger
from config import URL_BASE

logger = setup_logger()

if __name__ == "__main__":
    WEBHOOK_PATH = "/webhook"
    PORT = int(os.environ.get("PORT", 8080))

    logger.info("🟢 Iniciando bot con Webhook...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH,
        webhook_url=URL_BASE + WEBHOOK_PATH
    )
