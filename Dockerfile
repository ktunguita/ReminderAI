# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala dependencias del sistema necesarias (incluye tzdata y ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Establece la zona horaria (Argentina)
ENV TZ=America/Argentina/Buenos_Aires
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Instala dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Evita el buffering en logs
ENV PYTHONUNBUFFERED=1

# Comando para ejecutar el bot
CMD ["python", "main.py"]