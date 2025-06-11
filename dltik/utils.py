from urllib.parse import quote
import base64, json, hashlib, hmac, uuid, yt_dlp, time, re
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

_updater_started = False

DELAY_UPDATE = 60

def encode_token(data, ts=None) -> str:
    if ts is None:
        ts = int(time.time()) + 300
    data_str = json.dumps(data, separators=(',', ':'))
    sig = hmac.new(settings.SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
    payload = {"data": data, "ts": ts, "sig": sig}
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

def decode_token(encoded_token):
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_token)
        payload = json.loads(decoded_bytes.decode("utf-8"))

        data = payload['data']
        sig = payload['sig']
        ts = payload.get('ts', -1)

        # Verify chữ ký
        data_str = json.dumps(data, separators=(',', ':'))
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        if sig != expected_sig:
            return {'error': 1, 'msg': 'sig'}

        if ts != -1 and int(time.time()) > ts:
            return {'error': 2, 'msg': 'ts'}

        return {'ok': True, 'decoded': data}

    except Exception as e:
        return {'error': 3, 'msg': str(e)}

def parse_cookie_string(cookie_str):
    cookies = {}
    for pair in cookie_str.split(';'):
        if '=' in pair:
            key, value = pair.strip().split('=', 1)
            cookies[key] = value
    return cookies

def download_format(label, fmt, video_url, upload, save, request):
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
            info = ydl.extract_info(video_url, download=save)
            ext = info.get('ext', 'mp4')

            if save:
                path = f"{settings.BASE_URL}/media/videos/{filename}.{ext}"
            else:
                path = info.get('url', '')

            upload.files.create(label=label, url=path, filename=f"{filename}.{ext}", type='video', cookies=parse_cookie_string(info.get("cookies", '')),)


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
        return info

def encode_data(data):
    new_urls = []

    for item in data.get('urls', []):
        url = item['url']
        label = item['label']
        token = encode_token(
            data={
                "code": quote(url, safe=''),
                "type": 1
            },
            ts=-1
        )
        encoded_url = f"/perform?token={quote(token)}"
        new_urls.append({
            'label': label,
            'url': encoded_url,
            'type': item.get('type', '')
        })

    data['urls'] = new_urls

def is_valid_email(email: str):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def detect_media_type(info):
    if 'formats' in info and any(f.get('vcodec') not in (None, 'none') for f in info['formats']):
        return 'video'
    elif 'images' in info or info.get('media_type') == 'photo':
        return 'photo'
    return 'unknown'