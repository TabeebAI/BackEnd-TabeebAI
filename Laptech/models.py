
from django.db import models
from django.contrib.auth.models import User

class LabTechDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='labtech_profile')
    
    full_name = models.CharField(max_length=30)
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    license_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=30, default="دمشق")
    lab_name = models.CharField(max_length=50, default="غير محدد")

    def __str__(self):
        return f"LabTech #{self.license_number}"
