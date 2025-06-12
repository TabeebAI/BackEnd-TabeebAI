

from rest_framework import serializers
from .models import DoctorsDB
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
class LoginDR(serializers.Serializer):
        full_name=serializers.CharField()
        national_id=serializers.CharField()
        license_number=serializers.CharField()
        def validate(self,data):
                full_name=data.get('full_name')
                national_id=data.get('national_id')
                license_number=data.get('license_number')
                DR = DoctorsDB.objects.filter(license_number=license_number,national_id=national_id,full_name=full_name).first()
                if not DR:
                        raise serializers.ValidationError("يوجد خطأ بالبيانات ")
                data['DR']=DR.user
                return data
    
class CreateDR(serializers.ModelSerializer):
        user = serializers.PrimaryKeyRelatedField(read_only=True)
        full_name=serializers.CharField()
        gender=serializers.CharField(required=True,error_messages={
              'required' : 'M \ F'   
        })
        specialty=serializers.CharField()
        phone=serializers.CharField()
        region=serializers.CharField()
        neighborhood=serializers.CharField()
        license_number=serializers.CharField(
                validators=[
                        UniqueValidator(
                                queryset=DoctorsDB.objects.all(),
                                message="الرقم النقابي مسجل من قبل"
                                
                        )
                ]            
        )
        national_id =serializers.CharField(
                validators=[
                        UniqueValidator(
                                queryset= DoctorsDB.objects.all(),
                                message="تأكد من رقمك الوطني "
                        )
                ]
        )
        class Meta:
                model = DoctorsDB
                fields=["user",
                'full_name' , 'gender' , 'specialty','license_number',
                'phone','national_id','region','neighborhood'
                ]   
                extra_kwargs={
                        'license_number':{'write_only': True},
                        'national_id':{'write_only':True}
                }     

        def validate_national_id(self,value):
                national_str =str(value)
                if len(national_str) != 11 or not national_str.isdigit() :
                        raise serializers.ValidationError({
                                'national_id':'الرقم الوطني مكون من 11 الرقم'
                        })   
 
                return national_str  
        
        def validate_license_number(self,value):
               
                license_str=str(value)
                if len(license_str) != 4 or not license_str.isdigit():
                        raise serializers.ValidationError({
                                "license_number":"الرقم النقابي مكون من 4 ارقام"
                        })

                return license_str
        
        def create(self, validated_data):
                request = self.context.get('request')
                username = validated_data.get('license_number')
                password = validated_data.get('national_id')

                user = User.objects.create_user(username=username, password=password)
                Token.objects.create(user=user)
                doctor = DoctorsDB.objects.create(user=user, **validated_data)
                return doctor


class profil(serializers.ModelSerializer):
        
        class Meta:
                model =DoctorsDB
                fields=['id','full_name','gender','specialty','license_number','phone',
                        'national_id','region','neighborhood']
        def update(seld,instance,validated_data):
                readonlu_field=['full_name','gender','license_number','national_id']
                for field in readonlu_field:
                        if field in validated_data:
                                validated_data.pop(field)
                return super().update(instance,validated_data)
