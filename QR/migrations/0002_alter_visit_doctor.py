# Generated by Django 5.2.1 on 2025-06-13 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Doctor', '0002_doctorsdb_user'),
        ('QR', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visit',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='Doctor.doctorsdb'),
        ),
    ]
