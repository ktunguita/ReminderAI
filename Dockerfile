# Usa una imagen base de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Instala dependencias del sistema (incluye ffmpeg)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Especifica la variable de entorno (opcional, si no está ya seteada)
ENV PYTHONUNBUFFERED=1

# Establecer zona horaria en el contenedor
ENV TZ=America/Argentina/Buenos_Aires
RUN apt-get update && apt-get install -y tzdata && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# Comando para ejecutar tu bot
CMD ["python", "main.py"]
