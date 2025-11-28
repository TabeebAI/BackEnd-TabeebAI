from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.viewsets import ModelViewSet
from .serializers import Createpatients, MedicalQuerySerializer
from rest_framework.permissions import IsAuthenticated
from .models import PatientDB
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import requests

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


