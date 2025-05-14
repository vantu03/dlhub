from django.http import JsonResponse
from django.shortcuts import render
from .models import Article, File, Upload
from django.db.models import Q
from dltik import utils
from urllib.parse import quote
from django.conf import settings
import uuid, json, yt_dlp, uuid, time, requests, urllib
from django.http import StreamingHttpResponse

def ads(request):
    return render(request, 'dltik/ads.txt')

def custom_404_view(request, exception):
    return render(request, 'dltik/404.html', status=404)

def generate_token_view(request):
    try:
        body = json.loads(request.body)
        url = body.get("url")
        type1 = body.get("type1", 0)

        return JsonResponse({"token": utils.encode_token(data = {'type': 0, "code": url, "type1": type1})})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def home(request):
    utils.start_updater_once()
    return render(request, 'dltik/home.html')

def perform(request):
    str_token = request.GET.get('token')
    if str_token:
        decoded = utils.decode_token(str_token)
        if decoded.get('ok'):
            match decoded.get('decoded', {}).get('type'):
                case 0:
                    url = utils.strip_query_params(decoded.get('decoded', {}).get('code'))
                    if url:
                        # Check nếu đã tồn tại và chưa quá hạn
                        uploaded = Upload.objects.filter(source_url=url).first()
                        if uploaded:
                            if time.time() - uploaded.created_at.timestamp() > 300:
                                uploaded.delete()
                            else:
                                return JsonResponse({'success': True, 'data': {
                                    'thumbnail': uploaded.thumbnail,
                                    'urls': [
                                        {f.label: f.url}
                                        for f in uploaded.files.all()
                                    ],
                                    'title': uploaded.title,
                                }})

                        formats = {
                            'Download <i class="bi bi-badge-hd-fill"></i>': 'best',
                            'Download': 'best[height<=1080]',
                        }

                        data = {
                            'thumbnail': None,
                            'title': None,
                            'urls': []
                        }

                        save = decoded.get('decoded', {}).get('type1') == 0
                        temp_files = {}

                        for label, fmt in formats.items():
                            try:
                                filename = f"dlhub_{uuid.uuid4()}"
                                filepath = str(settings.BASE_DIR / 'media' / 'videos' / f'{filename}')

                                with yt_dlp.YoutubeDL({
                                    'outtmpl': f'{filepath}.%(ext)s',
                                    'format': fmt,
                                    'quiet': True,
                                    'noplaylist': True,
                                    'http_headers': {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                                        'Accept-Language': 'en-US,en;q=0.9',
                                    }
                                }) as ydl:
                                    info = ydl.extract_info(url, download=save)
                                    ext = info.get('ext', 'mp4')
                                    data['thumbnail'] = info['thumbnail']
                                    data['title'] = info['title']

                                    if save:
                                        temp_files[label] = f"/media/videos/{filename}.{ext}"
                                    else:
                                        token = utils.encode_token(
                                            data={"code": quote(info['url'], safe=''), "type": 1, "filename": f"{filename}.{ext}"},
                                            ts=-1
                                        )
                                        temp_files[label] = f"/perform?token={token}"

                                    data['urls'].append({label: temp_files[label]})
                            except Exception as e:
                                print(str(e))

                        upload = Upload.objects.create(
                            source_url=url,
                            title=data['title'],
                            thumbnail=data['thumbnail'],
                        )
                        for label, url in temp_files.items():
                            File.objects.create(
                                upload=upload,
                                label=label,
                                url=url
                            )

                        return JsonResponse({'success': True, 'data': data})

                case 1:
                    video_url = decoded.get('decoded', {}).get('code')
                    filename = decoded.get('decoded', {}).get('filename')

                    r = requests.get(urllib.parse.unquote(video_url), stream=True)
                    response = StreamingHttpResponse(r.iter_content(1024), content_type=r.headers['Content-Type'])
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response

        else:
            return JsonResponse({'error': 'Token lỗi'+ decoded.get('msg', '-1')}, status=400)

    return JsonResponse({'error': 'Thao tác không hợp lệ'+ str_token}, status=400)

def articles(request, tag = None):
    articles = Article.objects.filter(is_published=True)
    if tag:
        articles = articles.filter(Q(tags__icontains=tag)).distinct()
    return render(request, 'dltik/articles.html', {'articles': articles, 'tag': tag})

def article(request, slug):
    article = Article.objects.filter(slug=slug).first()
    if article:
        return render(request, 'dltik/article.html', {'article': article})
    else:
        return custom_404_view(request, None)

def about(request):
    return render(request, 'dltik/about.html')

def contact(request):
    return render(request, 'dltik/contact.html')

