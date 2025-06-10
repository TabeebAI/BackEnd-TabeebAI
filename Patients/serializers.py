from rest_framework import serializers
from .models import PatientDB

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

