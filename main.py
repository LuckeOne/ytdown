
# File: main.py
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import yt_dlp
from PIL import Image
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.urandom(24)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        flash('Por favor ingresa una URL de YouTube válida.', 'error')
        return redirect(url_for('index'))

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        audio_file = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}.mp3")
        thumb_file = os.path.join(DOWNLOAD_FOLDER, f"{info['id']}.jpg")

        # Resize cover art
        img = Image.open(thumb_file)
        img.thumbnail((300, 300))
        buf = BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)

        return render_template('download.html',
                               title=info.get('title'),
                               author=info.get('uploader'),
                               duration=info.get('duration'),
                               audio_file=url_for('serve_file', filename=f"{info['id']}.mp3"),
                               cover_data=buf.getvalue().encode('base64').decode('utf-8'))
    except Exception as e:
        flash(f'Error al descargar: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))