import requests
from django.http import JsonResponse
from django.views import View
from django.utils import timezone  
from .models import VitalSigns
from Patients.models import PatientDB

FASTAPI_BASE_URL = "http://127.0.0.1:8001"

class HeartRateView(View):

    def get(self, request, address):
        patient_id = request.GET.get("patient_id")
        if not patient_id:
            return JsonResponse({"error": "patient_id is required"}, status=400)

        try:
            patient = PatientDB.objects.get(id=patient_id)
            response = requests.get(f"{FASTAPI_BASE_URL}/hr/{address}", timeout=35)
            response.raise_for_status()
            data = response.json()

            latest_data = data.get("latest_data", {})
            hr_value = latest_data.get("hr")

            if hr_value:
                VitalSigns.objects.create(
                    patient=patient,
                    heart_rate=hr_value,
                    heart_rate_time=timezone.now() 
                )
                data["db_status"] = "Heart Rate saved successfully"
            else:
                data["db_status"] = "No valid HR data received"

            return JsonResponse(data)

        except PatientDB.DoesNotExist:
            return JsonResponse({"error": "Patient not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class BloodPressureView(View):

    def get(self, request, address):
        patient_id = request.GET.get("patient_id")
        if not patient_id:
            return JsonResponse({"error": "patient_id is required"}, status=400)

        try:
            patient = PatientDB.objects.get(id=patient_id)
            response = requests.get(f"{FASTAPI_BASE_URL}/bp/{address}", timeout=40)
            response.raise_for_status()
            data = response.json()

            latest_data = data.get("latest_data", {})
            sys = latest_data.get("systolic")
            dia = latest_data.get("diastolic")

            if sys and dia:
                VitalSigns.objects.create(
                    patient=patient,
                    systolic_pressure=sys,
                    diastolic_pressure=dia,
                    blood_pressure_time=timezone.now() 
                )
                data["db_status"] = "Blood Pressure saved successfully"
            else:
                data["db_status"] = "No valid BP data received"

            return JsonResponse(data)

        except PatientDB.DoesNotExist:
            return JsonResponse({"error": "Patient not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)