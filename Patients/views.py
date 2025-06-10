from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from .serializers import Createpatients
from rest_framework.permissions import IsAuthenticated
from .models import PatientDB


# Create your views here.
class PatientsView(viewsets.ModelViewSet):
    serializer_class =Createpatients
    permission_classes=[IsAuthenticated] 
    def get_queryset(self):
        return PatientDB.objects.filter(user=self.request.user)
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)
