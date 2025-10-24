from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FilmViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'films', FilmViewSet, basename='film')
router.register(r'comments', CommentViewSet, basename='comment')


urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
]