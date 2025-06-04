from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:id>/subscribe/', UserViewSet.as_view({'post': 'subscribe', 'delete': 'subscribe'})),
]

