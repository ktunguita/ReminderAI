#main.py
from telegram_bot import app  # <- importa la instancia de Application

if __name__ == "__main__":
    app.run_polling(drop_pending_updates=True)