from rest_framework import serializers
from .models import Visit ,Session

class VisitsDoctor(serializers.ModelSerializer):
    patient_name=serializers.SerializerMethodField()
    class Meta:
        model=Visit
        fields=['id','patient_name','treatment_name','created',"Test_Request","Type_of_Test"]

    def get_patient_name(self,obj):
        return f"{obj.patient.last_name} {obj.patient.first_name}"    
    


class VisitsPatient(serializers.ModelSerializer):
    Doctor_name=serializers.CharField(source='doctor.full_name',read_only=True)
    class Meta:
        model=Visit
        fields=['Doctor_name','expires_at','is_permanent','treatment_name','created','recipes','notes',"Type_of_Test","Test_Request","id"] 
        


class TestPatient(serializers.ModelSerializer):
    Doctor_name=serializers.CharField(source='doctor.full_name',read_only=True)
    class Meta:
        model=Visit
        fields=['Doctor_name',"Type_of_Test","id"] 

class ReviewPatient(serializers.ModelSerializer):
    Doctor_name=serializers.CharField(source='doctor.full_name',read_only=True)
    Specialization=serializers.CharField(source='doctor.specialty',read_only=True)
    class Meta:
        model=Visit
        fields=['Doctor_name',"Specialization","id"] 
class session_laptech(serializers.ModelSerializer):
   
    patient_name = serializers.SerializerMethodField(read_only=True)
    Type_of_Test=serializers.CharField(source='visit.Type_of_Test',read_only=True)
    class Meta:
        model=Session
        fields=['id','Type_of_Test','patient_name']
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    


from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
