import uuid, yt_dlp, base64, json, hashlib, time, hmac, os, requests
from urllib.parse import quote
from django.http import JsonResponse
from django.shortcuts import render
from .models import DownloadRecord
from urllib.parse import urlparse, urlunparse
from django.http import StreamingHttpResponse
from django.conf import settings

SECRET_KEY = os.environ.get("SECRET_KEY", "dlhub_super_secret_dev_key")

def ads(request):
    return render(request, 'dltik/ads.txt')

def custom_404_view(request, exception):
    return render(request, 'dltik/404.html', status=404)

def generate_token_view(request):
    try:
        body = json.loads(request.body)
        url = body.get("url")
        type1 = body.get("type1", 0)

        ts = int(time.time())
        data = {"code": url, "type1": type1, "ts": ts}
        data_str = json.dumps(data, separators=(',', ':'))
        sig = hmac.new(SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        payload = {"data": data, "sig": sig}
        token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

        return JsonResponse({"token": token})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def home(request):
    return render(request, 'dltik/home.html')

def strip_query_params(url):
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query="", fragment=""))

def decodeUploadInfo(encoded_token):
    try:
        decoded_bytes = base64.urlsafe_b64decode(encoded_token)
        payload = json.loads(decoded_bytes.decode("utf-8"))

        data = payload['data']
        sig = payload['sig']

        # Verify chữ ký
        data_str = json.dumps(data, separators=(',', ':'))
        expected_sig = hmac.new(SECRET_KEY.encode(), data_str.encode(), hashlib.sha256).hexdigest()
        if sig != expected_sig:
            return {'error': 'Token bị giả mạo'}

        # Kiểm tra hạn dùng 5 phút
        now = int(time.time())
        if abs(now - data.get('ts', 0)) > 300:
            return {'error': 'Token hết hạn'}

        return {'ok': True, 'decoded': data['code'], 'type1': data['type1']}

    except Exception as e:
        return {'error': str(e)}


def dlv(request):
    strToken = request.GET.get('token')
    if strToken:
        decoded = decodeUploadInfo(strToken)
        if not decoded.get('error'):
            match decoded.get('type1'):
                case 0:
                    return downloadTiktok(decoded.get('decoded'))
                case 1:
                    return downloadYoutube(decoded.get('decoded'))
                case 2:
                    return downloadFacebook(decoded.get('decoded'))

    return JsonResponse({'error': 'Thao tác không hợp lệ'}, status=400)

def proxy_download(request):
    video_url = request.GET.get("url")
    r = requests.get(video_url, stream=True)
    response = StreamingHttpResponse(r.iter_content(1024), content_type=r.headers['Content-Type'])
    response['Content-Disposition'] = f'attachment; filename="video.mp4"'
    return response


def downloadTiktok(data):
    url = strip_query_params(data)
    if url:

        fileRecord = DownloadRecord.objects.filter(url=url).first()
        if fileRecord:
            return JsonResponse({'success': True, 'data': {
                'thumbnail': fileRecord.thumbnail,
                'urls': fileRecord.urls,
                'title': fileRecord.title,
            }})

        formats = {
            'HD': 'best',
            '720p': 'best[height<=720]',
        }

        data = {
            'thumbnail': None,
            'title': None,
            'urls': []
        }

        for label, fmt in formats.items():
            try:
                filename = f"dlhub_{uuid.uuid4()}_{label}"
                with yt_dlp.YoutubeDL({
                    'outtmpl': str(settings.BASE_DIR / 'media' / 'videos' / f'{filename}.%(ext)s'),
                    'format': fmt,
                    'quiet': True,
                    'noplaylist': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                }) as ydl:
                    info = ydl.extract_info(url, download=True)
                    ext = info.get('ext', 'mp4')
                    data['thumbnail'] = info['thumbnail']
                    data['title'] = info['title']
                    data['urls'].append({label: f"/media/videos/{filename}.{ext}"})
            except Exception as e:
                print(str(e))

        DownloadRecord.objects.create(
            url=url,
            urls=data['urls'],
            thumbnail=data['thumbnail'],
            title=data['title'],
        )
        return JsonResponse({'success': True, 'data': data})

    return JsonResponse({'error' : 'Thao tác không hợp lệ'}, status=400)

def downloadYoutube(data):
    url = strip_query_params(data)
    if url:

        fileRecord = DownloadRecord.objects.filter(url=url).first()
        if fileRecord:
            return JsonResponse({'success': True, 'data': {
                'thumbnail': fileRecord.thumbnail,
                'urls': fileRecord.urls,
                'title': fileRecord.title,
            }})

        formats = {
            'HD': 'best',
            '720p': 'best[height<=720]',
        }

        data = {
            'thumbnail': None,
            'title': None,
            'urls': []
        }

        for label, fmt in formats.items():
            try:
                with yt_dlp.YoutubeDL({
                    'format': fmt,
                    'quiet': True,
                    'noplaylist': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                }) as ydl:
                    info = ydl.extract_info(url, download=False)
                    ext = info.get('ext', 'mp4')
                    data['thumbnail'] = info['thumbnail']
                    data['title'] = info['title']
                    data['urls'].append({label: f"/proxy-download?url={quote(info['url'], safe='')}"})
            except Exception as e:
                print(str(e))

        DownloadRecord.objects.create(
            url=url,
            urls=data['urls'],
            thumbnail=data['thumbnail'],
            title=data['title'],
        )
        return JsonResponse({'success': True, 'data': data})

    return JsonResponse({'error' : 'Thao tác không hợp lệ'}, status=400)

def downloadFacebook(data):
    url = strip_query_params(data)
    if url:

        fileRecord = DownloadRecord.objects.filter(url=url).first()
        if fileRecord:
            return JsonResponse({'success': True, 'data': {
                'thumbnail': fileRecord.thumbnail,
                'urls': fileRecord.urls,
                'title': fileRecord.title,
            }})

        formats = {
            'HD': 'best',
            '720p': 'best[height<=720]',
        }

        data = {
            'thumbnail': None,
            'title': None,
            'urls': []
        }

        for label, fmt in formats.items():
            try:
                with yt_dlp.YoutubeDL({
                    'format': fmt,
                    'quiet': True,
                    'noplaylist': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept-Language': 'en-US,en;q=0.9',
                    }
                }) as ydl:
                    info = ydl.extract_info(url, download=False)
                    ext = info.get('ext', 'mp4')
                    data['thumbnail'] = info['thumbnail']
                    data['title'] = info['title']
                    data['urls'].append({label: f"/proxy-download?url={quote(info['url'], safe='')}"})
            except Exception as e:
                print(str(e))

        DownloadRecord.objects.create(
            url=url,
            urls=data['urls'],
            thumbnail=data['thumbnail'],
            title=data['title'],
        )
        return JsonResponse({'success': True, 'data': data})

    return JsonResponse({'error' : 'Thao tác không hợp lệ'}, status=400)