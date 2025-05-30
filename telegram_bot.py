#telegram_bot.py

import uuid
#import logging
import os
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from config import AUDIO_FOLDER, TELEGRAM_BOT_TOKEN
from modulo_openai_texto import interpretar_con_chatgpt
from modulo_openai_audio import transcribir_y_interpretar_audio
from modulo_recordatorios import guardar_recordatorio, revisar_y_lanzar_recordatorios, tarea_periodica_recordatorios
 

# Configurar logging
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Enviame un mensaje o un audio.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"📩 Texto recibido: {user_text}")
    chat_id = update.message.chat_id

    resultado = interpretar_con_chatgpt(user_text)
    print(f"[DEBUG] Resultado interpretado: {resultado} ({type(resultado)})")

    if isinstance(resultado, dict) and resultado.get("es_recordatorio"):
        recordatorios = resultado.get("recordatorios", [])
        for recordatorio in recordatorios:
            mensaje_empatico = recordatorio.get("mensaje_recordatorio")
            mensaje = recordatorio.get("mensaje")
            fecha_hora = recordatorio.get("fecha_hora")

            guardar_recordatorio(chat_id, mensaje_empatico, fecha_hora)

            respuesta = recordatorio.get("respuesta_natural") or f'📌 Recordatorio agendado:\n"{mensaje}"\n🕒 Fecha y hora: {fecha_hora}'
            await update.message.reply_text(respuesta)
    else:
        respuesta = resultado.get("respuesta_texto", "❓ No entendí tu mensaje.")
        await update.message.reply_text(respuesta)

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        await update.message.reply_text("❌ No se recibió audio válido.")
        return

    chat_id = update.message.chat_id
    message_id = update.message.message_id
    filename_base = f"{chat_id}_{message_id}_{uuid.uuid4().hex}"  # único y trazable
    ogg_path = os.path.join(AUDIO_FOLDER, f"{filename_base}.ogg")

    # Descargar el audio
    file = await context.bot.get_file(voice.file_id)
    await file.download_to_drive(ogg_path)
    print(f"🔊 Audio guardado en {ogg_path}")

    await update.message.reply_text("🎙️ Audio recibido. Procesando...")

    # Transcripción y eliminación automática
    texto_transcripto = transcribir_y_interpretar_audio(ogg_path)

    if not texto_transcripto:
        await update.message.reply_text("❌ No pude transcribir tu audio.")
        return

    print(f"📝 Texto transcripto: {texto_transcripto}")

    if isinstance(texto_transcripto, dict) and texto_transcripto.get("es_recordatorio"):
        recordatorios = texto_transcripto.get("recordatorios", [])
        for recordatorio in recordatorios:
            mensaje_empatico = recordatorio.get("mensaje_recordatorio")
            mensaje = recordatorio.get("mensaje")
            fecha_hora = recordatorio.get("fecha_hora")

            guardar_recordatorio(chat_id, mensaje_empatico, fecha_hora)

            respuesta = recordatorio.get("respuesta_natural") or f'📌 Recordatorio agendado:\n"{mensaje}"\n🕒 Fecha y hora: {fecha_hora}'
            await update.message.reply_text(respuesta)
    else:
        respuesta = texto_transcripto.get("respuesta_texto", "❓ No entendí tu mensaje.")
        await update.message.reply_text(respuesta)

print("🤖 Inicializando bot de Telegram...")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.VOICE, handle_audio))
app.add_handler(CommandHandler("start", handle_start))

print("✅ Bot de Telegram iniciado correctamente.")
print("🟢 Bot corriendo. Esperando mensajes...")

# Configurar la tarea periódica
async def periodic_task(context):
    await tarea_periodica_recordatorios(app.bot)

app.job_queue.run_repeating(periodic_task, interval=600, first=10)