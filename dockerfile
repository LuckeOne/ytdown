FROM python:3.11-slim

# Instalar dependencias del sistema necesarias, incluido ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usa Flask
EXPOSE 8080

# Comando para correr la aplicación
CMD ["python", "main.py"]
