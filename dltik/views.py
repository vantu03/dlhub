from django.http import JsonResponse
from django.shortcuts import render
from .models import Article, User, Upload, PinnedArticle, Page, Favorite, File
from dltik import utils
import json, requests, threading, re
from django.http import StreamingHttpResponse, HttpResponse
from django.template import Template, Context
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from urllib.parse import unquote
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from urllib.parse import quote
from django.utils.http import url_has_allowed_host_and_scheme
from vt_dlhub import DLHub
from requests.utils import cookiejar_from_dict

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
    print(cookiejar_from_dict(request.COOKIES))
    pinned_articles = PinnedArticle.objects.select_related('article')[:5]
    return render(request, 'dltik/home.html', {'pinned_articles': pinned_articles})

def perform(request):
    str_token = request.GET.get('token')
    if str_token:
        decoded = utils.decode_token(str_token)
        if decoded.get('ok'):
            match decoded.get('decoded', {}).get('type'):
                case 0:
                    video_url = decoded.get('decoded', {}).get('code')
                    type1 = decoded.get('decoded', {}).get('type1')
                    if video_url:

                        formats = []
                        threads = []
                        print('dang tai vui long cho')

                        if type1 == 0:
                            dl = DLHub(video_url)
                            info = dl.run(download=False)
                            print(info)
                            info["thumbnail"] = info.get('cover', '')

                        else:

                            info = utils.get_formats(video_url)
                            info["final_url"] = info.get('url', '')

                            formats = [
                                ("Download <i class='bi bi-badge-hd-fill'></i>", 'best', False),
                                ("Download", 'best[height<=720]', False),
                            ]

                            for fmt in info.get('formats', []):
                                if "hd" in fmt['format_id'] and False:
                                    formats["Download "+ fmt['format_id']] = fmt['format_id']
                                print(f"{fmt['format_id']} - {fmt.get('height')}")

                        upload = Upload.objects.create(
                            source_url=video_url,
                            final_url=info.get('final_url', ''),
                            title=info.get('title', ''),
                            thumbnail=info.get('thumbnail', ''),
                        )

                        for i, item in enumerate(info.get("media", []), start=1):
                            if item['type'] == 'video':
                                label = "Download <i class='bi bi-badge-hd-fill'></i>"
                            elif item['type'] == 'music':
                                label = "Download <i class='bi bi-music-note-beamed'></i>"
                            elif item['type'] == 'image':
                                label = f"Ảnh {i}"
                            else:
                                label = "Download"

                            upload.files.create(
                                label=label,
                                url=item["url"],
                                filename=item['filename'],
                                type=item['type'],
                                cookies=item.get('cookies', {})
                            )

                        for label, fmt, save in formats:
                            t = threading.Thread(
                                target=utils.download_format,
                                args=(label, fmt, video_url, upload, save, request)
                            )
                            t.start()
                            threads.append(t)

                        for t in threads:
                            t.join()

                        data = {
                            'title': upload.title,
                            'thumbnail': upload.thumbnail,
                            'urls': [
                                {
                                    'label': f.label,
                                    'url': f.url,
                                    'type': f.type,
                                }
                                for f in upload.files.all()
                            ]
                        }
                        utils.encode_data(data)
                        return JsonResponse({'success': True, 'data': data})


                case 1:
                    video_url = decoded.get('decoded', {}).get('code')

                    real_url = unquote(video_url)
                    file = File.objects.filter(url=real_url).first()

                    if file:
                        file.download_count = file.download_count + 1
                        file.save()
                        print(file.cookies)
                        print(file.url)
                        try:
                            r = requests.get(real_url, headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                                'Accept-Language': 'en-US,en;q=0.9',
                            }, cookies=file.cookies, stream=True, timeout=10)
                            r.raise_for_status()
                        except requests.RequestException:
                            return JsonResponse({'error': 'Không thể tải video từ URL'}, status=400)

                        content_type = r.headers.get('Content-Type', 'application/octet-stream')
                        content_length = r.headers.get('Content-Length')

                        response = StreamingHttpResponse(r.iter_content(8192), content_type=content_type)
                        response['Content-Disposition'] = f'attachment; filename="{file.filename}"'

                        if content_length:
                            response['Content-Length'] = content_length

                        return response

                    else:
                        return JsonResponse({'error': 'Không thể tải video từ URL'}, status=400)


        else:
            return JsonResponse({'error': 'Token lỗi'+ decoded.get('msg', '-1')}, status=400)

    return JsonResponse({'error': 'Thao tác không hợp lệ'+ str_token}, status=400)

def articles(request, tag=None):
    articles = Article.objects.filter(is_published=True)

    if tag:
        tag_list = [t.strip() for t in tag.split(',')]
        articles = articles.filter(tags__name__in=tag_list).distinct()

    # Tìm kiếm theo tiêu đề hoặc tóm tắt
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )

    # Sắp xếp theo thời gian
    sort_order = request.GET.get('sort', 'desc')
    if sort_order == 'asc':
        articles = articles.order_by('published_at')
    else:
        articles = articles.order_by('-published_at')

    # Phân trang
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dltik/articles.html', {
        'page_obj': page_obj,
        'tag': tag,
    })

def article(request, slug):
    article = Article.objects.filter(slug=slug).first()
    if article:
        is_favorited = False

        if request.method == "POST":
            action = request.POST.get("action")
            if action == "toggle_favorite":

                if request.user.is_authenticated:
                    fav, created = Favorite.objects.get_or_create(user=request.user, article=article)
                    if not created:
                        fav.delete()
                else:
                    return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")

            elif action == "send_comment":
                if request.user.is_authenticated and article.allow_comments:
                    content = request.POST.get("content", "").strip()
                    recaptcha_response = request.POST.get("g-recaptcha-response")

                    if content:
                        if not content or len(content) < 300:

                            # Xác minh reCAPTCHA
                            verify_url = 'https://www.google.com/recaptcha/api/siteverify'
                            payload = {
                                'secret': settings.RECAPTCHA_SECRET_KEY,
                                'response': recaptcha_response,
                            }

                            try:
                                r = requests.post(verify_url, data=payload)
                                result = r.json()
                                if result.get("success"):
                                    article.comments.create(user=request.user, content=content)
                                else:
                                    # Có thể log hoặc hiển thị lỗi
                                    print("reCAPTCHA failed", result)
                            except Exception as e:
                                print("reCAPTCHA error:", str(e))
                        return redirect(f"{article.get_absolute_url()}#comments")

        if request.user.is_authenticated:
            is_favorited = Favorite.objects.filter(user=request.user, article=article).exists()

        article.views += 1
        article.save()

        #Lấy bình luận
        if request.user.is_authenticated:
            comments_qs = article.comments.filter(Q(status='approved') | Q(user=request.user)).distinct()
        else:
            comments_qs = article.comments.filter(status='approved')

        comment_count = article.comments.filter(status='approved').count()


        paginator = Paginator(comments_qs, 10)
        page_number = request.GET.get('comment_page')
        comment_page = paginator.get_page(page_number)

        return render(request, 'dltik/article.html',{
            'article': article,
            'is_favorited': is_favorited,
            'comment_page': comment_page,
            'comment_count': comment_count,
            'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY,
        })
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
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /set-theme/",
        "Disallow: /user/logout/",
        "Allow: /",
        f"Sitemap: {settings.BASE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def page_view(request, slug):
    page = Page.objects.filter(slug=slug).first()
    if page:

        match page.format:
            case 'html':
                template = Template(page.content)
                context = Context({
                    'request': request,
                    'user': request.user,
                    'site_name': page.name,
                })
                return HttpResponse(template.render(context))

            case 'text':
                return HttpResponse(page.content, content_type='text/plain')

            case 'json':
                try:
                    parsed = json.loads(page.content)
                    return JsonResponse(parsed)
                except json.JSONDecodeError:
                    return JsonResponse({'error': 'Lỗi json'}, status=400)

            case _:
                return HttpResponse("Unsupported format", status=415)
    else:
        return custom_404_view(request, None)

def login(request):
    if request.user.is_authenticated:
        next_url = request.GET.get("next", "home")
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}) or len(next_url) > 200:
            next_url = "home"
        return redirect(next_url)
    messages = []
    labels = []

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if not username or not password:
            messages.append({"type": "warning","msg": "Hãy nhập đầy đủ thông tin."})
            if not username:
                labels.append('username')
            if not password:
                labels.append('password')

        else:
            if utils.is_valid_email(username):
                result = User.objects.filter(email=username.strip().lower()).first()
                if result:
                    username = result.username
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)

                next_url = request.GET.get("next", "home")
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}) or len(
                        next_url) > 200:
                    next_url = "home"
                return redirect(next_url)
            else:
                messages.append({"type": "danger", "msg": "Tên đăng nhập/email hoặc mật khẩu không đúng."})

    return render(request, "dltik/login.html", {"messages": messages, "labels": labels})

def logout(request):

    next_url = request.GET.get("next", "home")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}) or len(next_url) > 200:
        next_url = "home"

    if request.method == "POST":
        if request.user.is_authenticated:
            auth_logout(request)
        return redirect(next_url)
    return render(request, "dltik/logout.html", {"next_url": next_url})

def register(request):
    if request.user.is_authenticated:
        next_url = request.GET.get("next", "home")
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}) or len(next_url) > 200:
            next_url = "home"
        return redirect(next_url)

    messages = []
    labels = []

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        recaptcha_response = request.POST.get("g-recaptcha-response")

        # Validate form
        if not all([username, email, password, confirm_password]):
            messages.append({"type": "warning", "msg": "Hãy nhập đầy đủ thông tin."})
            if not username: labels.append("username")
            if not email: labels.append("email")
            if not password: labels.append("password")
            if not confirm_password: labels.append("confirm_password")
        elif not re.fullmatch(r'[a-zA-Z0-9_]{5,20}', username):
            messages.append({"type": "danger", "msg": "Tên đăng nhập phải từ 5–20 ký tự, chỉ chứa chữ, số, gạch dưới."})
            labels.append("username")
        elif not (8 <= len(password) <= 30):
            messages.append({"type": "danger", "msg": "Mật khẩu phải dài từ 8 đến 30 ký tự."})
            labels.append("password")
        elif password != confirm_password:
            messages.append({"type": "danger", "msg": "Mật khẩu không khớp."})
            labels.extend(["password", "confirm_password"])
        elif not utils.is_valid_email(email):
            messages.append({"type": "danger", "msg": "Email không hợp lệ."})
            labels.append("email")
        elif User.objects.filter(username=username).exists():
            messages.append({"type": "danger", "msg": "Tên đăng nhập đã tồn tại."})
            labels.append("username")
        elif User.objects.filter(email=email).exists():
            messages.append({"type": "danger", "msg": "Email đã được sử dụng."})
            labels.append("email")
        else:
            # Verify reCAPTCHA
            recaptcha_data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            recaptcha_result = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=recaptcha_data
            ).json()

            if recaptcha_result.get("success"):
                # Tạo người dùng
                user = User.objects.create_user(username=username, email=email.strip().lower(), password=password)
                auth_login(request, user)
                next_url = request.GET.get("next", "home")
                if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}) or len(next_url) > 200:
                    next_url = "home"
                return redirect(next_url)
            else:
                messages.append({"type": "danger", "msg": "Xác minh reCAPTCHA thất bại. Vui lòng thử lại."})

    return render(request, "dltik/register.html", {
        "messages": messages,
        "labels": labels,
    })
