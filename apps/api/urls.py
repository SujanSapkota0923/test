from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import CourseViewSet, UserViewSet, AcademicLevelViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'users', UserViewSet, basename='user')
router.register(r'classes', AcademicLevelViewSet, basename='academic-level')

urlpatterns = [
    path('', include(router.urls)),
    # Simple token auth endpoint (returns token for username/password)
    path('token-auth/', obtain_auth_token, name='api-token-auth'),
]
