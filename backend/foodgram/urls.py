from django.contrib import admin
from django.urls import path
from django.urls.conf import re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/', include('djoser.urls')),
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
]
