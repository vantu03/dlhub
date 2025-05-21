from django.http import JsonResponse
from django.shortcuts import render
from .models import Article, File, Upload, PinnedArticle
from dltik import utils
import json, time, requests, threading
from django.http import StreamingHttpResponse, HttpResponse
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from urllib.parse import unquote

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
    pinned_articles = PinnedArticle.objects.select_related('article')[:5]
    utils.start_updater_once()
    return render(request, 'dltik/home.html', {'pinned_articles': pinned_articles})

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
                                data = {
                                    'thumbnail': uploaded.thumbnail,
                                    'title': uploaded.title,
                                    'urls': [
                                        {f.label: f.url} for f in uploaded.files.all()
                                    ]
                                }
                                utils.encode_data(data)
                                return JsonResponse({'success': True, 'data': data})

                        formats = {
                            'Download <i class="bi bi-badge-hd-fill"></i>': 'best',
                            'Download': 'best[height<=1080]',
                        }

                        data = {'thumbnail': '', 'title': '', 'urls': []}
                        save = decoded.get('decoded', {}).get('type1') == 0
                        temp_files = {}
                        threads = []
                        data_lock = threading.Lock()

                        for label, fmt in formats.items():
                            t = threading.Thread(target=utils.download_format,
                                                 args=(label, fmt, url, save, temp_files, data_lock, data, request))
                            t.start()
                            threads.append(t)

                        # Chờ các thread tải xong
                        for t in threads:
                            t.join()

                        # Sau khi tất cả hoàn tất thì lưu DB
                        upload = Upload.objects.create(
                            source_url=url,
                            title=data['title'],
                            thumbnail=data['thumbnail'],
                        )
                        for label, url_path in temp_files.items():
                            File.objects.create(upload=upload, label=label, url=url_path)

                        utils.encode_data(data)

                        return JsonResponse({'success': True, 'data': data})

                case 1:
                    video_url = decoded.get('decoded', {}).get('code')
                    filename = decoded.get('decoded', {}).get('filename')

                    try:
                        r = requests.get(unquote(video_url), stream=True, timeout=10)
                        r.raise_for_status()
                    except requests.RequestException:
                        return JsonResponse({'error': 'Không thể tải video từ URL'}, status=400)

                    content_type = r.headers.get('Content-Type', 'application/octet-stream')
                    content_length = r.headers.get('Content-Length')

                    response = StreamingHttpResponse(r.iter_content(8192), content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'

                    if content_length:
                        response['Content-Length'] = content_length

                    return response

        else:
            return JsonResponse({'error': 'Token lỗi'+ decoded.get('msg', '-1')}, status=400)

    return JsonResponse({'error': 'Thao tác không hợp lệ'+ str_token}, status=400)

def articles(request, tag = None):
    articles = Article.objects.filter(is_published=True)
    if tag:
        tag_list = [t.strip() for t in tag.split(',')]
        articles = articles.filter(tags__name__in=tag_list).distinct()

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

class StaticViewSitemap(Sitemap):
    protocol = 'https'
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        return ['home', 'articles', 'contact', 'about']

    def location(self, item):
        return reverse(item)

class ArticleSitemap(Sitemap):
    protocol = 'https'
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.published_at

def robots_txt(request):
    sitemap_url = f"{utils.get_base_url(request)}/sitemap.xml"
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
