from django.urls import path
from . import views

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
]

