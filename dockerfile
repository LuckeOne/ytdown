# Usa la imagen oficial de Python (versión 3.10 o la que prefieras)
FROM python:3.10-slim

# Instala ffmpeg y ffprobe
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Crea y define el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (Railway lo sobreescribe con $PORT)
ENV PORT 8080

# Comando de inicio con Gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--workers", "4"]
