from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import yt_dlp
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configurar la carpeta de descargas
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint de descarga
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        flash('Por favor ingresa una URL de YouTube válida.', 'error')
        return redirect(url_for('index'))

    try:
        # Obtén ruta del archivo de cookies desde variable de entorno
        cookie_file = os.environ.get('COOKIE_FILE', 'cookies.txt')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),  # Descargar en la carpeta de descargas
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
            # Pasar cookies para vídeos que requieren login/bot check
            'cookiefile': cookie_file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Rutas de archivos generados
        audio_file = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}.mp3")
        thumb_file = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}.jpg")

        # Verificar si el archivo de la carátula existe
        if os.path.exists(thumb_file):
            # Redimensionar carátula
            img = Image.open(thumb_file)
            img.thumbnail((300, 300))
            buf = BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            cover_data = buf.getvalue().encode('base64').decode('utf-8')
        else:
            cover_data = None  # Si no existe la carátula, no mostrarla

        # Renderizar plantilla con datos
        return render_template('download.html',
                               title=info.get('title'),
                               author=info.get('uploader'),
                               duration=info.get('duration'),
                               audio_file=url_for('serve_file', filename=f"{info['id']}.mp3"),
                               cover_data=cover_data)

    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('index'))

# Servir archivos descargados (temporales)
@app.route('/files/<path:filename>')
def serve_file(filename):
    try:
        # Enviar el archivo temporal directamente para su descarga
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        flash(f'Error al servir el archivo: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Para producción recomendada por Railway
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
