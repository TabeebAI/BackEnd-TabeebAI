# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from Laptech.models import LabTechDB
from Doctor.models import DoctorsDB


class SimpleLabTechSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTechDB
        fields = ["id", "full_name", "region", "lab_name"]

class SimpleDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorsDB
        fields = ["id", "full_name", "region", "specialty" , "neighborhood"]
