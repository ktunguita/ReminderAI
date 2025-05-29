#main.py

import asyncio
from telegram_bot import iniciar_bot

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # <- Evita conflicto si ya hay un loop
    asyncio.run(iniciar_bot())