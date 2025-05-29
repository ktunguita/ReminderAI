# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Especifica la variable de entorno (opcional, si no está ya seteada)
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar tu bot
CMD ["python", "main.py"]
