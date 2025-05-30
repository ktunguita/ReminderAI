#config.py

import os
from dotenv import load_dotenv
from google.cloud import storage

# Carga .env con claves privadas
load_dotenv()

# Configuracion de tolerancia
INTERVALO_REVISION_RECORDATORIOS_SEGUNDOS = 1800
TIEMPO_TOLERANCIA_MINUTOS = 14

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
GOOGLE_APPLICATION_CREDENTIALS_JSON = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")  # Ruta local al JSON
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Cargar la URL BASE de la app de fly.io
URL_BASE = os.environ.get("WEBHOOK_URL", "https://reminderai-bot-telegram.fly.dev")

# --- Inicializar cliente de Google Cloud Storage ---
# Leer secreto del entorno
google_creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Guardar en archivo temporal si aún no existe
CRED_PATH = "/app/credenciales_gcs.json"
if google_creds_json and not os.path.exists(CRED_PATH):
    with open(CRED_PATH, "w") as f:
        f.write(google_creds_json)

# Crear el cliente de Google Storage
storage_client = storage.Client.from_service_account_json(CRED_PATH)
gcs_bucket = storage_client.bucket(GCS_BUCKET_NAME)
