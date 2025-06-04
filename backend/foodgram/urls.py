from django.contrib import admin
from django.urls import path
from django.urls.conf import re_path, include
from django.conf import settings
from django.conf.urls.static import static

from recipes.short_links import short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^api/', include('users.urls')),
    re_path(r'^api/', include('recipes.urls')),
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
    path('s/<str:short_id>/', short_link_redirect, name='short_link_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
