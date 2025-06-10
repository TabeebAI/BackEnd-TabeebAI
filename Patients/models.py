from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def patient_photo_path(instance, filename):
    user_id = instance.user.id if hasattr(instance, 'user') and instance.user else 'unknown'
    return f'patient_photos/user_{user_id}/{filename}'

class PatientDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    username=models.CharField(max_length=20)
    
    last_name=models.CharField(max_length=20)
    first_name=models.CharField(max_length=20)
    fathers_name=models.CharField(max_length=20)
    mothers_name=models.CharField(max_length=20)
    BLOOD_TYPE=[
        ('A+','A+'),
        ('A-','A-'),
        ('AB+','AB+'),
        ('AB-','AB-'),
        ('B+','B+'),
        ('B-','B-'),
        ('O+','O+'),
        ('O-','O-'),
    ]
    blood_type=models.CharField(max_length=3,choices=BLOOD_TYPE,blank=True,
                                null=True,
                                help_text="اختر فصيلة الدم")
    birth_date =models.DateField(null=True,blank=True)
    email=models.EmailField()
    def save(self, *args, **kwargs):
        if self.user:
            if not self.username:
                self.username = self.user.username
            if not self.email:
                self.email = self.user.email
        super().save(*args, **kwargs)

    weight=models.CharField(max_length=3)
    height=models.CharField(max_length=3)
    phone=models.CharField(max_length=15)
    gender =models.CharField(max_length=8,choices=[
        ('male','ذكر'),
        ('female','انثى')
    ])
    photo =models.ImageField(
        upload_to=patient_photo_path,blank=True 
        , null= True    
    )
    def __str__ (self):
        return f"{self.first_name}{self.last_name}"
    

