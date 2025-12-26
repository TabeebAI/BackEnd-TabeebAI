from django.db import models
from Patients.models import PatientDB
from Doctor.models import DoctorsDB
from Laptech.models import LabTechDB
import datetime
from django.utils import timezone


class Visit(models.Model):
    patient = models.ForeignKey(PatientDB, on_delete=models.PROTECT, null=True, blank=True)
    doctor = models.ForeignKey(DoctorsDB, on_delete=models.PROTECT, null=True, blank=True)
    code = models.CharField(max_length=64, unique=True)
    notes = models.TextField(null=True, blank=True)
    recipes = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    treatment_name = models.CharField(max_length=50, null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    session = models.ForeignKey("Session", null=True, blank=True, on_delete=models.CASCADE,related_name="visits_for_this_session" )  # string reference

    def is_active(self):
        if self.is_permanent:
            return True
        return self.expires_at is None or timezone.now() < self.expires_at

    Test_Request = models.BooleanField(default=False)
    Type_of_Test = models.TextField(null=True, blank=True)


class Session(models.Model):
    patient = models.ForeignKey(PatientDB, on_delete=models.PROTECT, null=True, blank=True, related_name="sessions")
    code = models.CharField(max_length=64, unique=True)
    laptech = models.ForeignKey(LabTechDB, on_delete=models.PROTECT, null=True, blank=True)
    visit = models.ForeignKey("Visit", on_delete=models.CASCADE, null=True, blank=True,related_name="sessions_for_this_visit" )  # string reference
    doctor = models.ForeignKey(DoctorsDB, on_delete=models.PROTECT, null=True, blank=True, related_name="sessions")

    file = models.FileField(upload_to="test_results/", null=True, blank=True)
    image = models.ImageField(upload_to="test_results/imgs/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    AnalysisExplanation = models.TextField(null=True, blank=True)




class Notification(models.Model):
    patient =models.ForeignKey(PatientDB,on_delete=models.PROTECT,null=True,blank=True)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    data = models.JSONField(null=True, blank=True) 
    session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.CASCADE)
    visit = models.ForeignKey(Visit, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['patient', 'created_at']),
        ]