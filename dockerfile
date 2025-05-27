FROM python:3.11-slim

# Instala dependencias necesarias incluyendo ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Copia tu código
COPY . /app
WORKDIR /app

# Instala tus dependencias
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
