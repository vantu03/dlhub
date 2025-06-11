from django.urls import path, re_path
from . import views
from django.contrib.sitemaps.views import sitemap
urlpatterns = [
    path('', views.home, name='home'),
    path('perform/', views.perform, name='perform'),
    path('gen-token/', views.generate_token_view, name='gen-token'),
    path('articles/', views.articles, name='articles'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('article/<slug:slug>/', views.article, name='article'),
    path('articles/tag/<str:tag>/', views.articles, name='tagged_articles'),
    path('sitemap.xml', sitemap, {
        'sitemaps': {
            'static': views.StaticViewSitemap,
            'pages': views.PageSitemap,
            'articles': views.ArticleSitemap,
        }
    }, name='sitemap'),
    path("user/login/", views.login, name="login"),
    path("user/logout/", views.logout, name="logout"),
    path("user/register/", views.register, name="register"),
    path('tinymce/upload/', views.tinymce_image_upload, name='tinymce_image_upload'),
    path('tools/', views.tools_dashboard, name='tools_dashboard'),

    path('<path:path>/', views.page_view, name='page_view'),

]

