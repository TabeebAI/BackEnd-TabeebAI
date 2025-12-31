

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class DoctorsDB(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)

    full_name = models.CharField(max_length=30)
    
    GENDER_CHOICES = [
        ('M', 'ذكر'),
        ('F', 'أنثى'),
    ]
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)

    specialty = models.CharField(max_length=50, default='طبيب عام')
    license_number = models.CharField(max_length=20, unique=True)  
    phone = models.CharField(max_length=15)
    national_id = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=30, default="دمشق")
    neighborhood = models.CharField(max_length=40, default="الحميدية")

    def __str__(self):
        return f"Doctor #{self.license_number}"

