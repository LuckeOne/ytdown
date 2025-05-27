from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import yt_dlp
from PIL import Image
from io import BytesIO
import base64
import re

app = Flask(__name__)
app.secret_key = os.urandom(24)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        flash('Por favor ingresa una URL de YouTube válida.', 'error')
        return redirect(url_for('index'))

    # Verificar cookies.txt
    cookie_file = os.environ.get('COOKIE_FILE', 'cookies.txt')
    if not os.path.isfile(cookie_file):
        flash(f'No encuentro el archivo de cookies: {cookie_file}', 'error')
        return redirect(url_for('index'))
    with open(cookie_file, 'r', encoding='utf-8') as f:
        header = f.readline()
    if not header.startswith('# Netscape HTTP Cookie File'):
        flash('Tu cookies.txt no está en formato Netscape válido.', 'error')
        return redirect(url_for('index'))

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title).200s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
            'cookiefile': cookie_file
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Sanitizar nombre
        title = sanitize_filename(info['title'])
        audio_file = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")

        # Buscar la miniatura descargada (.jpg o .webp)
        thumb_path = None
        for ext in ('jpg', 'webp'):
            candidate = os.path.join(DOWNLOAD_FOLDER, f"{title}.{ext}")
            if os.path.exists(candidate):
                thumb_path = candidate
                break

        cover_data = None
        if thumb_path:
            img = Image.open(thumb_path)
            img.thumbnail((300, 300))
            buf = BytesIO()
            img.save(buf, format='JPEG')
            cover_data = base64.b64encode(buf.getvalue()).decode('utf-8')

        return render_template('download.html',
                               title=title,
                               author=info.get('uploader'),
                               duration=info.get('duration'),
                               audio_file=url_for('serve_file', filename=f"{title}.mp3"),
                               cover_data=cover_data)

    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def serve_file(filename):
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)
    except Exception as e:
        flash(f'Error al servir el archivo: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
