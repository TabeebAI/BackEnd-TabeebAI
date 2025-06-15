from rest_framework import serializers
from .models import Visit

class VisitsDoctor(serializers.ModelSerializer):
    patient_name=serializers.SerializerMethodField()
    class Meta:
        model=Visit
        fields=['id','patient_name','treatment_name','created']

    def get_patient_name(self,obj):
        return f"{obj.patient.last_name} {obj.patient.first_name}"    
    


class VisitsPatient(serializers.ModelSerializer):
    Doctor_name=serializers.CharField(source='doctor.full_name',read_only=True)
    class Meta:
        model=Visit
        fields=['Doctor_name','expires_at','is_permanent','treatment_name','created','recipes','notes'] 
        
           