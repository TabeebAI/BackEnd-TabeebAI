from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from .models import PatientDB
from Laptech.models import LabTechDB
from Doctor.models import DoctorsDB

class Createpatients(serializers.ModelSerializer):

    class Meta:
        model=PatientDB
        fields=[
            'id','username',
            'last_name','first_name','mothers_name','fathers_name',
            'blood_type','birth_date','weight','height','phone',
            'gender','photo','email'
        ]
        extra_kwargs={
            'weight':{'required': False},
            'height':{'required': False},
            'phone':{'required': False, 'allow_blank': True},
            'photo':{'required': False},
            'gender':{'required': False},
            'birth_date':{'required': False},
            'blood_type':{'required': False},
            'fathers_name':{'required': False, 'allow_blank': True},
            'mothers_name':{'required': False, 'allow_blank': True},            
            'first_name':{'required': False, 'allow_blank': True},
            'last_name':{'required': False, 'allow_blank': True},
                            }
   
    def update(self,instance,validated_data):
        readonly_fields=[
        'last_name','first_name','mothers_name','fathers_name',
        'blood_type','birth_date','gender'
            ]

        for field in readonly_fields:
            if field in validated_data:
                current_value = getattr (instance, field)
                if current_value not in [None, '' ] :
                    validated_data.pop(field)
        
        return super().update(instance, validated_data)




class MedicalQuerySerializer(serializers.Serializer):
    question = serializers.CharField(required=True) 
    image = serializers.ImageField(required=False)
    audio = serializers.FileField(required=False)



class LoginPatientSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username", "")
        email = attrs.get("email", "")
        password = attrs.get("password")

        if not password:
            raise serializers.ValidationError("Password is required.")

        user = None

        if username:
            user = authenticate(username=username, password=password)
        elif email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                raise serializers.ValidationError("User with this email does not exist.")
        else:
            raise serializers.ValidationError("Either username or email must be provided.")

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if hasattr(user, 'doctor_profile') or hasattr(user, 'labtech_profile'):
            raise serializers.ValidationError("This account is not a patient account.")

        attrs['user'] = user
        return attrs





class PatientRegisterSerializer(RegisterSerializer):

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        })
        return data



class SimpleDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorsDB
        fields = [
            "full_name",
            "specialty",
            "region",
            "neighborhood",
        ]
class SimpleLabTechSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTechDB
        fields = [ 
        "region", "lab_name"]
