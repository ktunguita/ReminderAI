#modulo_recordatorios_cloud.py
from google.cloud import storage
import json
import asyncio
import os
from datetime import datetime, timedelta
from config import gcs_bucket, TIEMPO_TOLERANCIA_MINUTOS, INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS

def _gcs_path(chat_id):
    return f"{chat_id}.json"

def _leer_recordatorios_gcs(chat_id):
    blob = gcs_bucket.blob(_gcs_path(chat_id))
    if not blob.exists():
        return []
    data = blob.download_as_text()
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return []

def _escribir_recordatorios_gcs(chat_id, lista_recordatorios):
    blob = gcs_bucket.blob(_gcs_path(chat_id))
    blob.upload_from_string(json.dumps(lista_recordatorios, indent=2), content_type='application/json')

def guardar_recordatorio(chat_id, mensaje, fecha_hora_str):
    print(f"[GUARDAR] Guardando recordatorio para {chat_id}: '{mensaje}' a las {fecha_hora_str}")
    try:
        recordatorios = _leer_recordatorios_gcs(chat_id)
        recordatorios.append({
            "mensaje": mensaje,
            "fecha_hora": fecha_hora_str
        })
        _escribir_recordatorios_gcs(chat_id, recordatorios)
    except Exception as e:
        print("❌ Error al guardar recordatorio:", e)

async def revisar_y_lanzar_recordatorios(bot):
    ahora = datetime.now()

    blobs = list(gcs_bucket.list_blobs(prefix="", delimiter="/"))
    for blob in blobs:
        if not blob.name.endswith(".json"):
            continue

        chat_id = blob.name.replace(".json", "")
        try:
            recordatorios = _leer_recordatorios_gcs(chat_id)
        except Exception:
            continue

        nuevos_recordatorios = []
        for recordatorio in recordatorios:
            try:
                fecha_obj = datetime.strptime(recordatorio["fecha_hora"], "%Y-%m-%d %H:%M")
                diferencia = (ahora - fecha_obj).total_seconds() / 60

                if -TIEMPO_TOLERANCIA_MINUTOS <= diferencia <= TIEMPO_TOLERANCIA_MINUTOS:
                    await bot.send_message(chat_id=chat_id, text=recordatorio["mensaje"])
                elif diferencia < -TIEMPO_TOLERANCIA_MINUTOS:
                    nuevos_recordatorios.append(recordatorio)
            except Exception:
                continue

        _escribir_recordatorios_gcs(chat_id, nuevos_recordatorios)

async def tarea_periodica_recordatorios(bot, intervalo_segundos=INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS):
    while True:
        print("🔄 Revisando recordatorios pendientes (GCS)...")
        try:
            await revisar_y_lanzar_recordatorios(bot)
        except Exception as e:
            print(f"[ERROR] Al revisar recordatorios: {e}")
        await asyncio.sleep(intervalo_segundos)
