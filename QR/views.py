from django.shortcuts import render ,get_object_or_404
import qrcode
import datetime
import jwt

from rest_framework.response import Response

from .models import Visit ,DoctorsDB,PatientDB
from io import BytesIO
from django.conf import settings
from django.http import HttpResponse ,JsonResponse
import uuid


from jwt.exceptions import ExpiredSignatureError , InvalidTokenError
import jwt
from rest_framework.decorators import api_view, permission_classes 
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required

from datetime import date ,timedelta
from django.utils import timezone 
from django.db.models import Q

from .serializers import VisitsDoctor ,VisitsPatient



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
@permission_classes([IsAuthenticated])
def  QR_Token(request,token):
    

    try:
        payload = jwt.decode(token,settings.SECRET_KEY, algorithms=["HS256"])
        visit_id = payload.get("visit_id")
        visit = get_object_or_404(Visit, id=visit_id)


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

        #notes = list(visits.exclude(notes__isnull=True).exclude(notes__exact="").values_list("notes", flat=True))

        #recipes = list(visits.exclude(recipes__isnull=True).exclude(recipes__exact="").values_list("recipes", flat=True))
        active_visit=visits.filter( Q(is_permanent=True)|Q(expires_at__gt=timezone.now()))
        notes=list(active_visit.values_list('notes', flat=True))
        recipes=list(active_visit.values_list('recipes', flat=True))
        treatment_name=list(active_visit.values_list('treatment_name', flat=True))

        return JsonResponse({
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
            },            
            
            "created": visit.created.strftime("%Y-%m-%d %H:%M"),
        })
    except ExpiredSignatureError:
        return JsonResponse({"error": "انتهت صلاحية التوكن"}, status=401)

    except InvalidTokenError:
        return JsonResponse({"error": "توكن غير صالح"}, status=400)
    



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Doctor_Visit(request):
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

    
