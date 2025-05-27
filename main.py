from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import yt_dlp
from PIL import Image
from io import BytesIO
import base64
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        flash('Por favor ingresa una URL de YouTube válida.', 'error')
        return redirect(url_for('index'))

    try:
        cookie_file = os.environ.get('COOKIE_FILE', 'cookies.txt')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                },
                {
                    'key': 'FFmpegMetadata',
                }
            ],
            'writethumbnail': True,
            'convert-thumbnails': 'jpg',
            'quiet': True,
            'cookiefile': cookie_file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        sanitized_title = sanitize_filename(info['title'])
        audio_file = f"{sanitized_title}.mp3"
        thumb_file = f"{sanitized_title}.jpg"

        if os.path.exists(thumb_file):
            img = Image.open(thumb_file)
            img.thumbnail((300, 300))
            buf = BytesIO()
            img.save(buf, format='JPEG')
            buf.seek(0)
            cover_data = base64.b64encode(buf.read()).decode('utf-8')
        else:
            cover_data = None

        return render_template('download.html',
                               title=info.get('title'),
                               author=info.get('uploader'),
                               duration=info.get('duration'),
                               audio_file=url_for('serve_file', filename=audio_file),
                               cover_data=cover_data)

    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def serve_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        flash(f'Error al servir el archivo: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
