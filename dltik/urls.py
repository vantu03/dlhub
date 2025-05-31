from django.urls import path
from . import views
from django.contrib.sitemaps.views import sitemap
urlpatterns = [
    path('', views.home, name='home'),
    path('perform/', views.perform, name='perform'),
    path('gen-token/', views.generate_token_view, name='gen-token'),
    path('ads.txt/', views.ads, name='ads'),
    path('articles/', views.articles, name='articles'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('article/<slug:slug>/', views.article, name='article'),
    path('articles/tag/<str:tag>/', views.articles, name='tagged_articles'),
    path('sitemap.xml', sitemap, {'sitemaps': {'static': views.StaticViewSitemap, 'articles': views.ArticleSitemap, }}, name='sitemap'),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path('pages/<slug:slug>/', views.page_view, name='page_view'),
    path("user/login/", views.login, name="login"),
    path("user/logout/", views.logout, name="logout"),
    path("user/register/", views.register, name="register"),
    path('tinymce/upload/', views.tinymce_image_upload, name='tinymce_image_upload'),
]

