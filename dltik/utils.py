from urllib.parse import urlparse, urlunparse, quote
import base64, json, hashlib, hmac, threading, uuid, yt_dlp, os, time
from django.utils import timezone
from dltik.models import Upload
from django.conf import settings

_updater_started = False

SECRET_KEY = os.environ.get("SECRET_KEY", "dlhub_super_secret_dev_key")
DELAY_UPDATE = 60

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

def download_format(label, fmt, url, save, temp_files, data_lock, data, request):
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
            info = ydl.extract_info(url, download=save)
            ext = info.get('ext', 'mp4')

            # Thread-safe update
            with data_lock:
                if not data['thumbnail']:
                    data['thumbnail'] = info.get('thumbnail', '')
                if not data['title']:
                    data['title'] = info.get('title', '')

            if save:
                path = f"{get_base_url(request)}/media/videos/{filename}.{ext}"
            else:
                path = info['url']

            with data_lock:
                data['urls'].append({label: path})
                temp_files[label] = path

    except Exception as e:
        print(f"[Download Thread Error] {label}: {e}")

def get_formats(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'continuedl': False,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])

        # Trả ra thông tin định dạng có ích cho client
        result = []
        for f in formats:
            result.append({
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'resolution': f.get('height'),
                'note': f.get('format_note'),
                'filesize': f.get('filesize') or f.get('filesize_approx'),
                'url': f.get('url'),  # link trực tiếp nếu cần preview
            })
        return result
def get_base_url(request) -> str:
    scheme = 'https' if request.is_secure() else 'http'
    host = request.get_host()
    return f"{scheme}://{host}"

def encode_data(data):
    new_urls = []

    for item in data['urls']:
        for label, url in item.items():
            path = urlparse(url).path
            filename = path.split('/')[-1]

            token = encode_token(
                data={
                    "code": quote(url, safe=''),
                    "type": 1,
                    "filename": filename
                },
                ts=-1
            )
            encoded_url = f"/perform?token={quote(token)}"
            new_urls.append({label: encoded_url})

    data['urls'] = new_urls

def clean_expired_data(timeout_seconds=300):
    print('[Cleanup] Bắt đầu dọn dữ liệu quá hạn...')
    # Xóa bản ghi Upload cũ
    now = timezone.now()

    # Xóa file dlhub_ cũ
    media_path = os.path.join(settings.BASE_DIR, 'media', 'videos')
    if not os.path.exists(media_path):
        return
    now_ts = time.time()
    for filename in os.listdir(media_path):
        if filename.startswith('dlhub_'):
            full_path = os.path.join(media_path, filename)
            try:
                if os.path.isfile(full_path):
                    created = os.path.getctime(full_path)
                    if now_ts - created > timeout_seconds:
                        os.remove(full_path)
                        print(f"Deleted: {full_path}")
            except Exception as e:
                print(f"Error deleting {full_path}: {e}")

def start_updater_once():
    global _updater_started
    if _updater_started:
        return

    _updater_started = True

    import time

    def loop():
        while True:
            try:
                from django.db import connection

                connection.close_if_unusable_or_obsolete()
                clean_expired_data()
            except Exception as e:
                print(f"[Updater Error] {e}")
            time.sleep(DELAY_UPDATE)

    threading.Thread(target=loop, daemon=True).start()

