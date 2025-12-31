from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import LabTechDB

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from .models import LabTechDB


class CreatLAPTECH(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    full_name = serializers.CharField()
    gender = serializers.CharField(required=True, error_messages={'required': 'M أو F مطلوب'})
    phone = serializers.CharField()
    region = serializers.CharField()
    lab_name = serializers.CharField()
    
    license_number = serializers.CharField(
        validators=[UniqueValidator(queryset=LabTechDB.objects.all(), message="الرقم النقابي مسجل من قبل")]
    )
    
    national_id = serializers.CharField(
        validators=[UniqueValidator(queryset=LabTechDB.objects.all(), message="تأكد من رقمك الوطني")]
    )

    class Meta:
        model = LabTechDB
        fields = [
            "user", 'full_name', 'gender', 'license_number', 'phone', 
            'national_id', 'region', 'lab_name'
        ]
        extra_kwargs = {
            'license_number': {'write_only': True},
            'national_id': {'write_only': True}
        }

    def validate_national_id(self, value):
        national_str = str(value)
        if len(national_str) != 11 or not national_str.isdigit():
            raise serializers.ValidationError("الرقم الوطني مكون من 11 رقم")
        return national_str

    def validate_license_number(self, value):
        license_str = str(value)
        if len(license_str) != 4 or not license_str.isdigit():
            raise serializers.ValidationError("الرقم النقابي مكون من 4 أرقام")
        return license_str

    def create(self, validated_data):
        username = validated_data.get('license_number')
        password = validated_data.get('national_id')
        username = f"L-{username}"
        password = password

        # ✅ إنشاء المستخدم الجديد
        user = User.objects.create_user(username=username, password=password)
        Token.objects.get_or_create(user=user)

        # ✅ إنشاء السجل وربطه بالمستخدم
        labtech = LabTechDB.objects.create(user=user, **validated_data)
        return labtech



from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User 

from rest_framework import serializers
from .models import LabTechDB  # تأكد من أن هذا هو الموديل الصحيح للمخبري

class LoginLabTech(serializers.Serializer):
    full_name = serializers.CharField()
    national_id = serializers.CharField()
    license_number = serializers.CharField()  # رقم ترخيص المخبري

    def validate(self, data):
        full_name = data.get('full_name')
        national_id = data.get('national_id')
        license_number = data.get('license_number')

        # البحث عن المخبر
        labtech = LabTechDB.objects.filter(
            license_number=license_number,
            national_id=national_id,
            full_name=full_name
        ).first()

        if not labtech:
            raise serializers.ValidationError("يوجد خطأ بالبيانات")

        # ربط المستخدم
        data['LabTech'] = labtech.user
        return data
