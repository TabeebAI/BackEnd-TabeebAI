# Generated by Django 5.2.1 on 2025-06-11 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorsDB',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=30)),
                ('gender', models.CharField(choices=[('M', 'ذكر'), ('F', 'انثى')], max_length=6)),
                ('specialty', models.CharField(default='طبيب عام', max_length=50)),
                ('license_number', models.CharField(unique=True)),
                ('phone', models.CharField(max_length=15)),
                ('national_id', models.CharField(max_length=20, unique=True)),
                ('region', models.CharField(default='دمشق', max_length=30)),
                ('neighborhood', models.CharField(default='الحميدية', max_length=40)),
            ],
        ),
    ]
