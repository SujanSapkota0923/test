from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CourseViewSet, AcademicLevelViewSet, UserViewSet,StreamViewSet, LiveClassViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'users', UserViewSet, basename='user')
router.register(r'classes', AcademicLevelViewSet, basename='academic-level')
router.register(r'streams', StreamViewSet, basename='stream')
router.register(r'liveclasses', LiveClassViewSet, basename='liveclass')

urlpatterns = [
    path('', include(router.urls)),
    path('token-auth/', obtain_auth_token, name='api-token-auth'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # JWT login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # JWT token refresh
] 
