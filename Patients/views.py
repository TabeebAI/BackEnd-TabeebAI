from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from .serializers import Createpatients, MedicalQuerySerializer ,LoginPatientSerializer,PatientRegisterSerializer ,SimpleDoctorsSerializer , SimpleLabTechSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import PatientDB
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests
from rest_framework.views import APIView
from django.contrib.auth import login
from dj_rest_auth.registration.views import RegisterView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q


from Laptech.models import LabTechDB
from Doctor.models import DoctorsDB



class PatientsView(viewsets.ModelViewSet):
    serializer_class =Createpatients
    permission_classes=[IsAuthenticated] 
    def get_queryset(self):
        return PatientDB.objects.filter(user=self.request.user)
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


    def create(self, request, *args, **kwargs):
        try:
            patient = PatientDB.objects.get(user=request.user)
            serializer = self.get_serializer(patient, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except PatientDB.DoesNotExist:
            return super().create(request, *args, **kwargs)



N8N_WEBHOOK_URL = "http://localhost:5678/webhook/muhammad"

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 

def medical_query_view(request):
    serializer = MedicalQuerySerializer(data=request.data)
    if serializer.is_valid():
        json_data = {
            "question": serializer.validated_data.get('question', '')
        }

        try:
            response = requests.post(N8N_WEBHOOK_URL, json=json_data)  # إرسال بصيغة JSON
            if 'application/json' in response.headers.get('Content-Type', ''):
                n8n_response = response.json()
            else:
                n8n_response = response.text
        except Exception as e:
            return Response({"error": f"Failed to send to n8n: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"status": "success", "n8n_response": n8n_response}, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginPatientView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginPatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "user_id": user.id,
                "role": "patient",
                "access": access_token,

            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,      
            samesite="Strict", 
            max_age=7*24*60*60 
        )

        return response


class PatientRegisterView(RegisterView):
    serializer_class = PatientRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(request)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "user_id": user.id,
                "role": "patient",
                "access": access_token,

            },
            status=status.HTTP_201_CREATED
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,       
            samesite="Strict", 
            max_age=7 * 24 * 60 * 60
        )

        return response


class PatientSearchDoctorsView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip() 
        if query:
            doctors = DoctorsDB.objects.filter(full_name__icontains=query) | DoctorsDB.objects.filter(specialty__icontains=query
            )| DoctorsDB.objects.filter(region__icontains=query
            )
        else:
            doctors = DoctorsDB.objects.none()  
        serializer = SimpleDoctorsSerializer(doctors, many=True)
        return Response(serializer.data)


class PatientSearchLabTechView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()  

        if query:
            labtechs = LabTechDB.objects.filter(
                lab_name__icontains=query
            ) | LabTechDB.objects.filter(region__icontains=query
            )
        else:
            labtechs = LabTechDB.objects.none()
        serializer = SimpleLabTechSerializer(labtechs, many=True)
        return Response(serializer.data)
