import io
import os  # <-- ¡ESTA ES LA LÍNEA QUE DEBES ASEGURARTE DE AÑADIR!
import re
from datetime import datetime, timezone
import requests
from flask import Flask, jsonify, request, render_template_string, send_file

app = Flask(__name__)

# ==================== CONFIGURACIÓN STRAVA ====================
STR_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID", "").strip()
CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET", "").strip()
REFRESH_TOKEN = os.environ.get("STRAVA_REFRESH_TOKEN", "").strip()
ACCESS_TOKEN = ""

# Conversión segura a entero para evitar el Error 500
try:
    CLIENT_ID = int(STR_CLIENT_ID) if STR_CLIENT_ID else None
    print(f"✅ CLIENT_ID cargado correctamente como número: {CLIENT_ID}")
except ValueError:
    CLIENT_ID = None
    print(f"❌ ERROR: 'STRAVA_CLIENT_ID' contiene caracteres no válidos en Render: '{STR_CLIENT_ID}'")

# Mensajes de diagnóstico limpios en los Logs
if not CLIENT_SECRET:
    print("❌ ERROR: No se encontró la variable STRAVA_CLIENT_SECRET")
if not REFRESH_TOKEN:
    print("❌ ERROR: No se encontró la variable STRAVA_REFRESH_TOKEN")
# ==============================================================

# ==================== TEXTOS ====================
TEXTS = {
    'es': {
        'title': "🚴 Extractor GPX - Eddie",
        'desc': "Descarga GPX de Strava",
        'placeholder': "Pega aquí el enlace de la actividad",
        'btn': "⬇️ Descargar GPX",
        'processing': "Procesando...",
        'success': "✅ ¡Descarga Iniciada!",
        'success_desc': "El archivo GPX se descargó correctamente.<br><strong>Revisa tu carpeta de Descargas.</strong>",
        'error_url': "❌ No se pudo extraer el ID de la actividad.",
        'error_api': "❌ Error al obtener datos de Strava."
    },
    'en': {
        'title': "🚴 GPX Extractor - Eddie",
        'desc': "Download GPX from Strava",
        'placeholder': "Paste the activity link here",
        'btn': "⬇️ Download GPX",
        'processing': "Processing...",
        'success': "✅ Download Started!",
        'success_desc': "The GPX file was downloaded successfully.<br><strong>Check your Downloads folder.</strong>",
        'error_url': "❌ Could not extract the activity ID.",
        'error_api': "❌ Error fetching Strava data."
    }
}

HTML_PAGE = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ t.title }}</title>
    
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#fc4c02">
    <link rel="apple-touch-icon" href="https://img.icons8.com/color/512/gps-device.png">

    <style>
        /* ... tu CSS aquí ... */
    </style>
</head>
<body>
    <div class="card">
        <h1>{{ t.title }}</h1>
        <p>{{ t.desc }}</p>
        <form action="/extract" method="POST" id="form">
            <input type="text" name="strava_url" placeholder="{{ t.placeholder }}" required>
            <button type="submit" id="btn">{{ t.btn }}</button>
        </form>
        <div id="status" class="status-msg"></div>
    </div>

    <footer style="margin-top:40px; color:#555; font-size:0.85rem;">
        © 2026 Eddie Trochez. Built with Python & Flask.
    </footer>

    <script>
        document.getElementById('form').addEventListener('submit', async function(e) {
            e.preventDefault();
            const btn = document.getElementById('btn');
            const statusDiv = document.getElementById('status');
            
            btn.disabled = true;
            btn.textContent = "{{ t.processing }}";
            statusDiv.style.display = "none";

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    body: new FormData(this)
                });

                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    throw new Error(errData.error || `Error ${response.status}`);
                }

                const blob = await response.blob();
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = "activity.gpx";
                
                if (contentDisposition) {
                    filename = contentDisposition.split('filename=')[1]?.replace(/"/g, '') || filename;
                }

                // Descarga automática
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();

                // Mensaje de éxito limpio
                statusDiv.className = "status-msg success";
                statusDiv.innerHTML = `
                    <strong>{{ t.success }}</strong><br>
                    {{ t.success_desc | safe }}
                `;
                statusDiv.style.display = "block";

            } catch (error) {
                statusDiv.className = "status-msg error";
                statusDiv.innerHTML = error.message;
                statusDiv.style.display = "block";
            } finally {
                btn.textContent = "{{ t.btn }}";
                btn.disabled = false;
            }
        });
    </script>
</body>
</html>
"""

# ==================== FUNCIONES AUXILIARES ====================

def refresh_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token'
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code == 200:
            global ACCESS_TOKEN
            ACCESS_TOKEN = r.json()['access_token']
            return True
    except:
        pass
    return False

def extract_activity_id(text):
    text = text.strip()
    
    # Enlace normal
    match = re.search(r'activities/(\d+)', text)
    if match: 
        return match.group(1)
    
    # ID directo
    match = re.search(r'(\d{8,})', text)
    if match: 
        return match.group(1)
    
    # Short link (importante para móvil)
    short_match = re.search(r'https?://strava\.app\.link/([a-zA-Z0-9]+)', text)
    if short_match:
        try:
            r = requests.head(short_match.group(0), allow_redirects=True, timeout=10)
            final_url = r.url
            match = re.search(r'activities/(\d+)', final_url)
            if match:
                return match.group(1)
        except:
            pass
    return None

def get_activity_streams(activity_id):
    if not ACCESS_TOKEN:
        refresh_access_token()
    
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    params = {'keys': 'time,latlng,altitude', 'key_by_type': 'true'}
    
    response = requests.get(url, headers=headers, params=params, timeout=15)
    
    if response.status_code == 401:
        if refresh_access_token():
            headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
            response = requests.get(url, headers=headers, params=params, timeout=15)

    return response.json() if response.status_code == 200 else None

def streams_to_gpx(activity_id, streams):
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    gpx = f'''<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Eddie Strava GPX" xmlns="http://topografix.com">
  <metadata>
    <name>Activity {activity_id}</name>
    <time>{now}</time>
  </metadata>
  <trk>
    <name>Activity {activity_id}</name>
    <trkseg>'''
    
    if 'latlng' in streams and streams['latlng']['data']:
        latlng = streams['latlng']['data']
        times = streams.get('time', {}).get('data', [])
        altitudes = streams.get('altitude', {}).get('data', [])
        
        for i, (lat, lon) in enumerate(latlng):
            time_str = ""
            if i < len(times):
                ts = datetime.fromtimestamp(times[i], tz=timezone.utc).isoformat().replace('+00:00', 'Z')
                time_str = f'<time>{ts}</time>'
            alt = altitudes[i] if i < len(altitudes) else 0
            gpx += f'\n      <trkpt lat="{lat}" lon="{lon}"><ele>{alt}</ele>{time_str}</trkpt>'
    
    gpx += '''
    </trkseg>
  </trk>
</gpx>'''
    return gpx.encode('utf-8')

# ==================== RUTAS ====================

from flask import send_from_directory

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/')
def home():
    lang = request.accept_languages.best_match(['es', 'en']) or 'es'
    return render_template_string(HTML_PAGE, t=TEXTS[lang], lang=lang)

@app.route('/extract', methods=['POST'])
def extract():
    input_text = request.form.get('strava_url', '').strip()
    lang = request.accept_languages.best_match(['es', 'en']) or 'es'
    
    activity_id = extract_activity_id(input_text)
    if not activity_id:
        return jsonify({'error': TEXTS[lang]['error_url']}), 400
    
    streams = get_activity_streams(activity_id)
    if not streams:
        return jsonify({'error': TEXTS[lang]['error_api']}), 500
    
    gpx_data = streams_to_gpx(activity_id, streams)
    filename = f"activity_{activity_id}.gpx"
    
    return send_file(
        io.BytesIO(gpx_data),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
