"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.registerUser),
    path('register/', views.registerUser),
    path('loginUser/', views.loginUser),
    path('logoutUser/', views.logoutUser),
    path('uploadVideo/',views.uploadVideo),
    path('likeVideo/',views.likeVideo),
    path('viewVideo/',views.viewVideo),   
    path('reportVideo/',views.reportVideo),
    path('verifyEmail/',views.verifyEmail),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)