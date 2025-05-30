# main.py

import signal
import sys

from telegram_bot import app  # importa Application ya construida
from logger_config import setup_logger

logger = setup_logger()

# Reinicio suave y logs de apagado
def handle_shutdown(signum, frame):
    logger.info(f"📴 Señal de apagado recibida ({signum}). Cerrando aplicación.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

if __name__ == "__main__":
    try:
        logger.info("🚀 Iniciando bot de Telegram...")
        app.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.exception(f"🔥 Error inesperado en el bot: {e}")
        sys.exit(1)