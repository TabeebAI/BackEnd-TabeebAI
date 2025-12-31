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
from rest_framework.routers import DefaultRouter
from dj_rest_auth.views import PasswordResetConfirmView
from django.conf import settings
from django.conf.urls.static import static


from QR.views import QrJwt ,QR_Token ,Doctor_Visit,Patient_Visit,patient_test,QR_Test,Qr_Laptech,list_session_laptech,Update_session ,QR_Complete,QR_Complete_Token,patient_Review
from QR.api import MyNotifications 
from Laptech.views import CreateLabTech , LoginLabTechView
from Doctor.views import LoginDRView ,CreateDoctor,profilDR
from Patients.views import PatientsView , medical_query_view ,LoginPatientView, PatientRegisterView,PatientSearchDoctorsView ,PatientSearchLabTechView
from prediction.views import PredictCHDView , DailyVitalsChartView
from Smart_Watch.views import HeartRateView ,BloodPressureView
from Admin.views import AdminLoginView
from X_rays.views import predict_mura
from Admin.views import AdminGetDoctorsView, AdminGetLabTechsView,AdminPatientsCountView


router = DefaultRouter()
router.register(r'profile', PatientsView, basename='patient-profile')
routerDR =DefaultRouter()
routerDR.register(r'profile',profilDR,basename='doctor-profile')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('TabebAI/login/', AdminLoginView.as_view()),
    path("TabebAI/login/Patient", LoginPatientView.as_view(), name="login-patient"),
    path('TabebAI/Registration/', PatientRegisterView.as_view()),
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
    path('TabebAI/qrcode/tests/<int:id>',QR_Test),
    path('session/<str:token>/',Qr_Laptech),
    path('list/session/laptech/',list_session_laptech),
    path('update/session/laptech/<int:id>',Update_session),
    path('my-notifications/', MyNotifications.as_view(), name='my-notifications'),
    path('TabebAI/qrcode/visit/copmlete/<int:id>',QR_Complete),
    path('visit/complete/<str:token>/',QR_Complete_Token),
    path('TabebAI/Review/',patient_Review),
    path('predict/', PredictCHDView.as_view(), name='predict-chd'),
    path("watch/heart/<str:address>/",HeartRateView.as_view()),
    path("watch/BP/<str:address>/",BloodPressureView.as_view()),
    path('graph-data/', DailyVitalsChartView.as_view()),
    path("predict_mura/", predict_mura),
    path("TabebAI/admin/doctors/", AdminGetDoctorsView.as_view()),
    path("TabebAI/admin/labtechs/", AdminGetLabTechsView.as_view()),
    path("TabebAI/patient/search-doctors/", PatientSearchDoctorsView.as_view()),
    path("TabebAI/patient/search-labtechs/", PatientSearchLabTechView.as_view()),
    path('TabebAI/admin/patients-count/', AdminPatientsCountView.as_view()),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

