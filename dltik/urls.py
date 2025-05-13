from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dlv/', views.dlv, name='dlv'),
    path('gen-token/', views.generate_token_view, name='gen-token'),
    path('proxy-download/', views.proxy_download, name='proxy-download'),
    path('ads.txt/', views.ads, name='ads'),
]

