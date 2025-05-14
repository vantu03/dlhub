from urllib.parse import urlparse, urlunparse
import base64, json, hashlib, hmac
import threading
import time
import os
from django.utils import timezone
from django.conf import settings
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