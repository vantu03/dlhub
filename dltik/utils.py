from urllib.parse import urlparse, urlunparse
import base64, json, hashlib, hmac
import threading
import time
import os
from django.utils import timezone
from dltik.models import Upload, File

_updater_started = False

SECRET_KEY = os.environ.get("SECRET_KEY", "dlhub_super_secret_dev_key")
DELAY_UPDATE = 1

def encode_token(data, ts=None) -> str:
    if ts is None:
        ts = int(time.time()) + 300
    data_str = json.dumps(data, separators=(',', ':'))
    sig = hmac.new(SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    payload = {"data": data, "ts": ts, "sig": sig}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

def strip_query_params(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))

def decode_token(encoded_token):
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_token)
        payload = json.loads(decoded_bytes.decode("utf-8"))

        data = payload['data']
        sig = payload['sig']
        ts = payload.get('ts', -1)

        # Verify chữ ký
        data_str = json.dumps(data, separators=(',', ':'))
        expected_sig = hmac.new(SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        if sig != expected_sig:
            return {'error': 1, 'msg': 'sig'}

        if ts != -1 and int(time.time()) > ts:
            return {'error': 2, 'msg': 'ts'}

        return {'ok': True, 'decoded': data}

    except Exception as e:
        return {'error': 3, 'msg': str(e)}

import threading, uuid, yt_dlp
from urllib.parse import quote
from django.conf import settings

def download_format(label, fmt, url, save, temp_files, data_lock, data):
    try:
        filename = f"dlhub_{uuid.uuid4()}"
        filepath = str(settings.BASE_DIR / 'media' / 'videos' / f'{filename}')
        with yt_dlp.YoutubeDL({
            'outtmpl': f'{filepath}.%(ext)s',
            'format': fmt,
            'quiet': True,
            'noplaylist': True,
            'continuedl': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept-Language': 'en-US,en;q=0.9',
            }
        }) as ydl:
            print(f"bat dau tai {fmt}")
            info = ydl.extract_info(url, download=save)
            ext = info.get('ext', 'mp4')

            # Thread-safe update
            with data_lock:
                if not data['thumbnail']:
                    data['thumbnail'] = info.get('thumbnail', '')
                if not data['title']:
                    data['title'] = info.get('title', '')

            if save:
                path = f"/media/videos/{filename}.{ext}"
            else:
                token = encode_token(
                    data={"code": quote(info['url'], safe=''), "type": 1, "filename": f"{filename}.{ext}"},
                    ts=-1
                )
                path = f"/perform?token={token}"

            with data_lock:
                data['urls'].append({label: path})
                temp_files[label] = path
        print(f"tai xong {fmt}")

    except Exception as e:
        print(f"[Download Thread Error] {label}: {e}")



def clean_files(timeout_seconds=300):
    print('starting to clean up...')

    now = timezone.now()
    expired_uploads = Upload.objects.filter(created_at__lt=now - timezone.timedelta(seconds=timeout_seconds))
    for upload in expired_uploads:
        upload.delete()

timeClear = time.time()

def start_updater_once():
    global _updater_started
    if _updater_started:
        return

    _updater_started = True

    import time

    def loop():
        global timeClear
        while True:
            try:
                if time.time() > timeClear:
                    timeClear = time.time() + 60
                    clean_files()
            except Exception as e:
                print(f"[Updater Error] {e}")
            time.sleep(DELAY_UPDATE)

    threading.Thread(target=loop, daemon=True).start()