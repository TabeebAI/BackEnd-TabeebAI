# Generated by Django 5.2.1 on 2025-06-13 07:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Patients', '0001_initial'),
        ('QR', '0002_alter_visit_doctor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Patients.patientdb'),
        ),
    ]
