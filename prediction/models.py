from django.db import models
from Patients.models import PatientDB

class CHDRiskResult(models.Model):
    patient = models.ForeignKey(PatientDB, on_delete=models.CASCADE, related_name="chd_results")
    probability = models.FloatField()
    risk_level = models.IntegerField()
    risk_label = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.id} - {self.risk_label}"
