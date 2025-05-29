# modulo_openai_texto.py

import openai
import json
from datetime import datetime
from config import OPENAI_API_KEY, RUTA_PROMPT_SISTEMA
from openai import OpenAIError, AuthenticationError, APIConnectionError

# Configurar la clave
openai.api_key = OPENAI_API_KEY

# Cliente con la API moderna
client = openai.OpenAI(api_key=OPENAI_API_KEY)

#Definiendo hora actual para referencia:
hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M')

def cargar_prompt_sistema():
    with open(RUTA_PROMPT_SISTEMA, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    
    hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    return contenido.replace("{{hora_actual}}", hora_actual).replace("{{hora_actual[:4]}}", hora_actual[:4])


def interpretar_con_chatgpt(mensaje_usuario: str) -> dict:
    print(f"[DEBUG] Texto recibido por interpretar_con_chatgpt: '{mensaje_usuario}'")
    
    if mensaje_usuario.strip().lower() == "_test_":
        print("✅ Conexión con ChatGPT establecida correctamente (modo prueba, sin tokens).")
        return {
            "es_recordatorio": False,
            "respuesta_texto": "✅ Conexión con ChatGPT establecida correctamente (modo prueba, sin tokens)."
        }

    prompt_sistema = cargar_prompt_sistema()

    try:
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": mensaje_usuario}
            ],
            temperature=0.2
        )
        contenido = respuesta.choices[0].message.content
        print(f"[DEBUG] Respuesta cruda de ChatGPT:\n{contenido}")

        # Intentamos parsear el JSON (aunque venga con espacios u otros caracteres)
        return json.loads(contenido)
    
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return {"es_recordatorio": False, "respuesta_texto": "No pude interpretar tu mensaje correctamente."}
        

    except AuthenticationError:
        return {
            "es_recordatorio": False,
            "respuesta_texto": "❌ Error: clave API inválida o no proporcionada."
        }

    except APIConnectionError:
        return {
            "es_recordatorio": False,
            "respuesta_texto": "❌ Error: no se pudo conectar con OpenAI. ¿Internet está disponible?"
        }

    except OpenAIError as e:
        return {
            "es_recordatorio": False,
            "respuesta_texto": f"❌ Error al conectarse con ChatGPT: {str(e)}"
        }

    except Exception as e:
        return {
            "es_recordatorio": False,
            "respuesta_texto": f"⚠️ Error inesperado: {str(e)}"
        }
