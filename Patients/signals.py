from  django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PatientDB



@receiver(post_save,sender=User)
def Create_Update_DB_Patients(sender ,created,instance,**kwargs):
    if created:
        PatientDB.objects.create(
            user = instance,
        )
    else:
        if hasattr(instance, 'patient_profile'):
            instance.patient_profile.save()

        
