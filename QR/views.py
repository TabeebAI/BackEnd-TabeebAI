from django.shortcuts import render ,get_object_or_404
import qrcode
import datetime
import jwt
import os
from rest_framework.response import Response

from QR.utils import notify_user

from .models import Visit ,DoctorsDB,PatientDB,Session,LabTechDB , Notification
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse ,JsonResponse ,StreamingHttpResponse, HttpResponseForbidden
import uuid


from jwt.exceptions import ExpiredSignatureError , InvalidTokenError
import jwt
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required

from datetime import date ,timedelta
from django.utils import timezone 
from django.db.models import Q

from .serializers import VisitsDoctor ,VisitsPatient , TestPatient,session_laptech

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import BasePermission


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import json
import time


from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user

class IsVisitOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'doctor_profile'):
            if obj.laptech is not None: 
                return False 
            return obj.doctor == request.user.doctor_profile
        elif hasattr(request.user, 'labtech_profile'):
            if obj.doctor is not None: 
                return False 
            return obj.laptech == request.user.labtech_profile
        return False
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def QrJwt(request,code=None):
    patient=request.user.patient_profile
    generated_code = str(uuid.uuid4()).replace("-", "")[:8]  
    visit = Visit.objects.create(code=generated_code,patient=patient)
    payload={
        "visit_id":visit.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
    }
    token=jwt.encode(payload,settings.SECRET_KEY,algorithm="HS256")
    qr_data=f"http://127.0.0.1:8000/visit/token/{token}/"

    img =qrcode.make(qr_data)
    buffer=BytesIO()
    img.save(buffer,format="PNG")
    buffer.seek(0)
    return HttpResponse (buffer.getvalue(),content_type="image/png")

@api_view(['GET','POST'])
@permission_classes([IsVisitOwner])
def QR_Token(request,token):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])
        visit_id = payload.get("visit_id")
        visit = get_object_or_404(Visit, id=visit_id)
        if hasattr(request.user, 'labtech_profile'):
            return Response({"error": "هذا المكان مخصص للأطباء فقط"}, status=403)


        if request.method == 'POST':
            visit.doctor = request.user.doctor_profile
            visit.notes = request.data.get('notes')
            visit.recipes = request.data.get('recipes')
            visit.treatment_name=request.data.get('treatment_name')

            visit.is_permanent = request.data.get("is_permanent",'true').lower() == 'true'

            if not visit.is_permanent:
                duration_days=int(request.data.get("duration_days",0))
                if duration_days>0:
                    visit.expires_at= timezone.now()+ timedelta(days=duration_days)

            visit.Test_Request =request.data.get("Test_Request",'false').lower()=='true'
            if visit.Test_Request:
                visit.Type_of_Test=request.data.get("Type_of_Test")

            visit.save()        
            return JsonResponse({"success": "تم حفظ البيانات بنجاح."})
        
        
        
        birth_date = visit.patient.birth_date
        today = date.today()
        if birth_date:
            delta = today - birth_date
            years = delta.days // 365
            days = delta.days % 365
        else :
            years="غير محدد"  
            days="غير محدد" 

        visits = Visit.objects.filter(patient=visit.patient)
        active_visit=visits.filter( Q(is_permanent=True)|Q(expires_at__gt=timezone.now()))
        notes=list(active_visit.values_list('notes', flat=True))
        recipes=list(active_visit.values_list('recipes', flat=True))
        treatment_name=list(active_visit.values_list('treatment_name', flat=True))

        return JsonResponse(
            {

            "patient": {
            "first_name": visit.patient.first_name,
            "last_name": visit.patient.last_name,
            "gender": visit.patient.gender,
            "blood_type":visit.patient.blood_type,
            "age": {
                "years": years,
                "days": days
                    },

            "weight":visit.patient.weight,
            "height":visit.patient.height,
            "treatment_name":treatment_name,
            "notes":notes,
            "recipes":recipes,
            "id":visit_id,
            },            
            "created": visit.created.strftime("%Y-%m-%d %H:%M"),
        })
    except ExpiredSignatureError:
        return JsonResponse({"error": "انتهت صلاحية التوكن"}, status=401)

    except InvalidTokenError:
        return JsonResponse({"error": "توكن غير صالح"}, status=400)
    



@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsVisitOwner])
def Doctor_Visit(request):
    if not hasattr(request.user, 'doctor_profile') :
            return Response({"error": "هذا المكان مخصص للاطباء فقط"}, status=403)
    doctor = DoctorsDB.objects.filter(user=request.user).first()
    if not doctor:
        return Response({"error": "هذا الحساب ليس دكتورًا مسجلاً."}, status=404)  
    Visits=Visit.objects.filter(doctor=doctor).order_by('created')
    serializer =VisitsDoctor(Visits,many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Patient_Visit(request):
    patient=PatientDB.objects.filter(user=request.user).first()
    if not patient:
        return Response({"error":"المريض ليس مسجل دخول "},status=404)
    active_visits =Visit.objects.filter(patient=patient).filter(Q(is_permanent=True)|Q(expires_at__gt=timezone.now())).order_by('created')
    serializer =VisitsPatient(active_visits,many=True)
    
    return Response(serializer.data)


@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def patient_test(request):
    patient=PatientDB.objects.filter(user=request.user).first()
    if not patient:
        return Response({"error":"المريض ليس مسجل دخول "},status=404)
    active_visits = ( Visit.objects.filter(patient=patient, Test_Request=True)
    .filter(Q(is_permanent=True) | Q(expires_at__gt=timezone.now())).order_by('created')
    )
    serializer =TestPatient(active_visits,many=True)
    return Response(serializer.data)
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def QR_Test(request):
    patient=request.user.patient_profile
    generated_code = str(uuid.uuid4()).replace("-", "")[:8]
    visit_id = request.GET.get("visit_id")

    if not visit_id:
        return Response({"error": "لم يتم تحديد رقم الزيارة"}, status=400)
    visit = get_object_or_404(Visit, id=visit_id, patient=patient)
    session = Session.objects.create(code=generated_code,patient=patient, visit=visit  )
    payload={
        "session_id" : session.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
    }
    token =jwt.encode(payload,settings.SECRET_KEY,algorithm="HS256")
    qr_data = f"http://127.0.0.1:8000/session/{token}/"
    img = qrcode.make(qr_data)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")



@api_view(['GET','POST'])
@permission_classes([IsVisitOwner])

def Qr_Laptech(request, token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        Session_id = payload.get("session_id")
        session = get_object_or_404(Session, id=Session_id)
        if not hasattr(request.user, 'labtech_profile') :
            return Response({"error": "هذا المكان مخصص للمخبريين فقط"}, status=403)
        if request.method == 'POST':

            session.laptech = request.user.labtech_profile
            uploaded = request.FILES.get("file") or request.FILES.get("image")
            if not uploaded:
                return Response({"error": "لم يتم رفع أي ملف"}, status=400)

            ext = os.path.splitext(uploaded.name)[1].lower()

            if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                file_type = "image"

            elif ext == ".pdf":
                file_type = "pdf"

            else:
                return Response({"error": "صيغة الملف غير مدعومة"}, status=400)
            session.file = uploaded 
            session.uploaded_by = request.user
            session.uploaded_at = timezone.now()
            session.AnalysisExplanation = request.data.get("Analysis_Explanation")
            session.save()
            patient_user = session.visit.patient
            Notification.objects.create(
                patient=patient_user,
                title="نتيجة تحليل جديدة",
                body=f"تم رفع نتيجة التحليل الخاص بك بواسطة {session.laptech.full_name}",
                session=session,
                visit=session.visit
            )   
            notify_user(patient_user.id, f"تم رفع نتيجة التحليل الخاص بك لجلسة رقم {session.id}")
            return JsonResponse({"success": "تم حفظ البيانات بنجاح."})

        session = get_object_or_404(Session, id=Session_id)
        visit = getattr(session, "visit", None)
        if not visit:
            return Response({"error": "لا توجد زيارة مرتبطة بهذه الجلسة"}, status=404)        
        return Response({
            "patient": {
            "first_name": visit.patient.first_name,
            "last_name": visit.patient.last_name
            },
            "doctor": {
                "doctor_name": getattr(visit.doctor, "full_name", "غير محدد")
            },
            "test_type": visit.Type_of_Test
            })
    except jwt.ExpiredSignatureError:
        return Response({"error": "انتهت صلاحية QR"}, status=401)
    except jwt.InvalidTokenError:
        return Response({"error": "QR غير صالح"}, status=400)




        


@api_view(['GET'])
@permission_classes([IsVisitOwner])
def list_session_laptech(request):
    laptech= LabTechDB.objects.filter(user=request.user).first()
    if not hasattr(request.user ,'labtech_profile'):
        return Response('error:هذا المكان مخصص فقط للمخبريين',status=404)
    active_session=(Session.objects.filter(laptech=laptech))
    serializer=session_laptech(active_session,many=True)
    return Response(serializer.data)

@api_view(['GET','POST'])
@permission_classes([IsVisitOwner])
def Update_session(request):

    if not hasattr(request.user, 'labtech_profile'):
        return Response({'error': 'هذا المكان مخصص فقط للمخبريين'}, status=403)

    session_id = request.data.get('session_id') or request.query_params.get('session_id')
    if not session_id:
        return Response({"error": "يرجى توفير session_id"}, status=400)

    session = get_object_or_404(Session, id=session_id)
    
    current_visit = session.visit 
    if not current_visit:
         return Response({"error": "لا توجد زيارة مرتبطة بهذه الجلسة"}, status=404)

    if request.method == 'POST':
        session.laptech = request.user.labtech_profile
        uploaded = request.FILES.get("file") or request.FILES.get("image")
        if not uploaded:
            return Response({"error": "لم يتم رفع أي ملف"}, status=400)

        ext = os.path.splitext(uploaded.name)[1].lower()
        if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            file_type = "image"
        elif ext == ".pdf":
            file_type = "pdf"
        else:
            return Response({"error": "صيغة الملف غير مدعومة"}, status=400)

        session.file = uploaded
        session.uploaded_by = request.user
        session.uploaded_at = timezone.now()
        session.AnalysisExplanation = request.data.get("Analysis_Explanation")
        
        session.save()
        patient_user = current_visit.patient
        Notification.objects.create(
        patient=patient_user,
        title="نتيجة تحليل جديدة",
        body=f"تم رفع نتيجة التحليل الخاص بك بواسطة {session.laptech.full_name}",
        session=session,
        visit=current_visit
        )   
        notify_user(patient_user.id, f"تم رفع نتيجة التحليل الخاص بك لجلسة رقم {session.id}")

        return JsonResponse({"success": "تم حفظ البيانات بنجاح وإرسال الإشعار."})

    return Response({
        "patient": {
            "first_name": current_visit.patient.first_name,
            "last_name": current_visit.patient.last_name
        },
        "doctor": {
            "doctor_name": getattr(current_visit.doctor, "full_name", "غير محدد")
        },
        "test_type": getattr(current_visit, "Type_of_Test", "غير محدد"),
        "uploaded": session.file.url if session.file else None
    })


