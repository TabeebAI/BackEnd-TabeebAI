from django.db import models
from Patients.models import PatientDB


class VitalSigns(models.Model):

    patient = models.ForeignKey(
        PatientDB,
        on_delete=models.PROTECT,
        related_name="vital_signs",
        null=True,
        blank=True
    )
    heart_rate = models.PositiveIntegerField(
        verbose_name="معدل ضربات القلب (BPM)",
        null=True,
        blank=True
    )

    heart_rate_time = models.DateTimeField(
        verbose_name="وقت قياس نبض القلب",
        null=True,
        blank=True
    )

    systolic_pressure = models.PositiveIntegerField(
        verbose_name="ضغط الدم العالي (SYS)",
        null=True,
        blank=True
    )

    diastolic_pressure = models.PositiveIntegerField(
        verbose_name="ضغط الدم الواطي (DIA)",
        null=True,
        blank=True
    )

    blood_pressure_time = models.DateTimeField(
        verbose_name="وقت قياس ضغط الدم",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "قياسات حيوية"
        verbose_name_plural = "القياسات الحيوية"
        indexes = [
            models.Index(fields=["patient", "heart_rate_time"]),
            models.Index(fields=["patient", "blood_pressure_time"]),
        ]

    def __str__(self):
        return f"Vitals for {self.patient.name if self.patient else 'Unknown'}"
