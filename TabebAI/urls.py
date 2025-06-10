"""
URL configuration for TabebAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path ,include
from django.contrib.auth import views as auth_views
from Doctor.views import LoginDRViwe ,CreateDoctor
from Patients.views import PatientsView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'profile', PatientsView, basename='profile')
from dj_rest_auth.views import PasswordResetConfirmView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('TabebAI/',include('dj_rest_auth.urls')),
    path('TabebAI/Registration/', include('dj_rest_auth.registration.urls')),
    path("TabebAI/password/reset/confirm/<uid>/<token>/",PasswordResetConfirmView.as_view(),name="password_reset_confirm"),  
    path('TabebAI/DR/login/',LoginDRViwe.as_view(),name='DR_login'),
    path("TabebAI/CreateDoctor/",CreateDoctor.as_view()),
    path('TabebAI/overview/', include(router.urls)),   
    ]       
