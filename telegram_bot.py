#telegram_bot.py

import uuid
import os
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import AUDIO_FOLDER, TELEGRAM_BOT_TOKEN, INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS
from modulo_openai_texto import interpretar_con_chatgpt
from modulo_openai_audio import transcribir_y_interpretar_audio
from modulo_recordatorios import guardar_recordatorio, tarea_periodica_recordatorios
from logger_config import setup_logger

logger = setup_logger()

# --- Handlers ---

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Enviame un mensaje o un audio.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    logger.info(f"📩 Texto recibido: {user_text}")
    chat_id = update.message.chat_id

    resultado = interpretar_con_chatgpt(user_text)
    logger.info(f"[DEBUG] Resultado interpretado: {resultado} ({type(resultado)})")

    if isinstance(resultado, dict) and resultado.get("es_recordatorio"):
        for recordatorio in resultado.get("recordatorios", []):
            guardar_recordatorio(chat_id, recordatorio["mensaje_recordatorio"], recordatorio["fecha_hora"])
            respuesta = recordatorio.get("respuesta_natural") or f'📌 Recordatorio agendado:\n"{recordatorio["mensaje"]}"\n🕒 Fecha y hora: {recordatorio["fecha_hora"]}'
            await update.message.reply_text(respuesta)
    else:
        await update.message.reply_text(resultado.get("respuesta_texto", "❓ No entendí tu mensaje."))

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        await update.message.reply_text("❌ No se recibió audio válido.")
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    filename = f"{chat_id}_{message_id}_{uuid.uuid4().hex}.ogg"
    ogg_path = os.path.join(AUDIO_FOLDER, filename)

    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive(ogg_path)
    logger.info(f"🔊 Audio guardado en {ogg_path}")
    await update.message.reply_text("🎙️ Audio recibido. Procesando...")

    resultado = transcribir_y_interpretar_audio(ogg_path)

    if not resultado:
        await update.message.reply_text("❌ No pude transcribir tu audio.")
        return

    logger.info(f"📝 Texto transcripto: {resultado}")

    if isinstance(resultado, dict) and resultado.get("es_recordatorio"):
        for recordatorio in resultado.get("recordatorios", []):
            guardar_recordatorio(chat_id, recordatorio["mensaje_recordatorio"], recordatorio["fecha_hora"])
            respuesta = recordatorio.get("respuesta_natural") or f'📌 Recordatorio agendado:\n"{recordatorio["mensaje"]}"\n🕒 Fecha y hora: {recordatorio["fecha_hora"]}'
            await update.message.reply_text(respuesta)
    else:
        await update.message.reply_text(resultado.get("respuesta_texto", "❓ No entendí tu mensaje."))

# --- Inicialización del bot ---

logger.info("🤖 Inicializando bot de Telegram...")

# No se necesita job_queue_enabled() ni post_init
app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(CommandHandler("start", handle_start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.VOICE, handle_audio))

# Tarea periódica para revisar recordatorios
async def periodic_task(context: ContextTypes.DEFAULT_TYPE):
    await tarea_periodica_recordatorios(app.bot)

app.job_queue.run_repeating(periodic_task, interval=INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS, first=10)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❌ Error manejado: {context.error}", exc_info=True)

app.add_error_handler(error_handler)

logger.info("✅ Bot de Telegram iniciado correctamente.")

