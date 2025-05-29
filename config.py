#config.py

import os
from dotenv import load_dotenv
from google.cloud import storage

# Carga .env con claves privadas
load_dotenv()

# Configuracion de tolerancia
INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS = 600
TIEMPO_TOLERANCIA_MINUTOS = 6

# Cargar Token de telegram y API de openai
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Directorios
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'audios')
RECORDATORIOS_DIR = os.path.join(os.path.dirname(__file__), 'recordatorios_por_usuario')
RUTA_PROMPT_SISTEMA = os.path.join(os.path.dirname(__file__), 'prompt_sistema.txt')

# Crear carpetas necesarias
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(RECORDATORIOS_DIR, exist_ok=True)


# Cargar credenciales desde archivo .json
GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_CLOUD_CREDENTIALS")  # Ruta local al JSON
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Inicializar cliente de Google Cloud Storage
storage_client = storage.Client.from_service_account_json(GOOGLE_CLOUD_CREDENTIALS)
gcs_bucket = storage_client.bucket(GCS_BUCKET_NAME)
