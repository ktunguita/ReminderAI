#modulo_openai_audio.py

import os
import openai
import tempfile
from pydub import AudioSegment
from config import OPENAI_API_KEY
from modulo_openai_texto import interpretar_con_chatgpt

# Configurar clave de API
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def transcribir_y_interpretar_audio(ruta_ogg):
    try:
        # Convertir OGG a formato MP3 temporal
        audio = AudioSegment.from_ogg(ruta_ogg)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            audio.export(temp_audio.name, format="mp3")
            ruta_mp3 = temp_audio.name

        # Eliminar el archivo OGG original
        os.remove(ruta_ogg)

        # Transcripción con Whisper
        with open(ruta_mp3, "rb") as f:
            transcripcion = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="json"
            )

        # Eliminar archivo mp3 temporal
        os.remove(ruta_mp3)

        print(f"[DEBUG] Transcripción obtenida: {transcripcion}")

        texto = transcripcion.get("text", "") if isinstance(transcripcion, dict) else str(transcripcion)
        print(f"[DEBUG] el tipo de dato que se le enviar a chatgpt es: {type(texto)}")
        return interpretar_con_chatgpt(texto)

    except Exception as e:
        print(f"❌ Error al transcribir o interpretar audio: {e}")
        return {
            "es_recordatorio": False,
            "respuesta_texto": "❌ Hubo un error al procesar tu audio. Intenta nuevamente."
        }