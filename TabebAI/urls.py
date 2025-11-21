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
from Doctor.views import LoginDRView ,CreateDoctor,profilDR
from Patients.views import PatientsView , medical_query_view
from rest_framework.routers import DefaultRouter
from Laptech.views import CreateLabTech , LoginLabTechView

from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'profile', PatientsView, basename='patient/profile')
from dj_rest_auth.views import PasswordResetConfirmView
from QR.views import QrJwt ,QR_Token ,Doctor_Visit,Patient_Visit,patient_test,QR_Test,Qr_Laptech,list_session_laptech,Update_session 
routerDR =DefaultRouter()
routerDR.register(r'profile',profilDR,basename='doctor/profile')
from QR.api import MyNotifications
urlpatterns = [
    path('admin/', admin.site.urls),
    path('TabebAI/',include('dj_rest_auth.urls')),
    path('TabebAI/Registration/', include('dj_rest_auth.registration.urls')),
    path("TabebAI/password/reset/confirm/<uid>/<token>/",PasswordResetConfirmView.as_view(),name="password_reset_confirm"),  
    path('TabebAI/DR/login/',LoginDRView.as_view(),name='DR_login'),
    path("TabebAI/Laptech/login/", LoginLabTechView.as_view()),
    path("TabebAI/CreateDoctor/",CreateDoctor.as_view()),
    path("TabebAI/CreateLaptech/",CreateLabTech.as_view()),
    path('TabebAI/overview/', include(router.urls)),   
    path('TabebAI/DR/OverView/',include(routerDR.urls)),
    path("TabebAI/QRcode/",QrJwt),
    path("visit/token/<str:token>/",QR_Token),
    path('TabebAI/Doctor/visits/',Doctor_Visit),
    path('TabebAI/Patient/visits/',Patient_Visit),
    path('chat/', medical_query_view),
    path('TabebAI/Patient/Tests/',patient_test),
    path('TabebAI/qrcode/tests/',QR_Test),
    path('session/<str:token>/',Qr_Laptech),
    path('list/session/laptech/',list_session_laptech),
    path('update/session/laptech/',Update_session),
    path('my-notifications/', MyNotifications.as_view(), name='my-notifications'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
