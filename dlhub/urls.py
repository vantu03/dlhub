from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dltik.urls')),
]

# Gắn custom 404
handler404 = 'dltik.views.custom_404_view'