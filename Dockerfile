FROM python:3.11-slim

# Instala dependencias necesarias
RUN apt update && apt install -y ffmpeg curl

# Crea un directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto (opcional, si usas Flask o FastAPI)
EXPOSE 8080

# Comando de inicio
CMD ["python", "main.py"]
