from django.db import models
from Patients.models import PatientDB
from Doctor.models import DoctorsDB
import datetime
from django.utils import timezone

# Create your models here.

class Visit(models.Model):
    patient=models.ForeignKey(PatientDB,on_delete=models.PROTECT,null=True,blank=True)
    doctor=models.ForeignKey(DoctorsDB,on_delete=models.PROTECT,null=True,blank=True)
    code=models.CharField(max_length=64,unique=True)
    notes=models.TextField(null=True,blank=True)
    recipes=models.TextField(null=True,blank=True)
    created=models.DateTimeField(auto_now_add=True)
    treatment_name=models.CharField(max_length=50,null=False,blank=True)
    is_permanent =models.BooleanField(default=False)
    expires_at= models.DateTimeField(null=True,blank=True)
    def is_active(self):
        if self.is_permanent:
            return True
        return self.expires_at is None or timezone.now() < self.expires_at



