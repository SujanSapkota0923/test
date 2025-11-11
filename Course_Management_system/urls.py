"""
URL configuration for Course_Management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Expose the app under two prefixes; use distinct namespaces to avoid
    # namespace collisions when reversing URLs.
    path('course/', include(('apps.Course.urls', 'course'), namespace='course')),
    path('', include(('apps.Course.urls', 'dashboard'), namespace='dashboard')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)