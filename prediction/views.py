from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import pandas as pd
import lightgbm as lgb
import os
import traceback
from django.conf import settings
from .models import CHDRiskResult
from django.utils.timezone import now
from Patients.models import PatientDB
from Smart_Watch.models import VitalSigns

from django.utils.timezone import make_aware
from datetime import datetime, time

from Smart_Watch.models import VitalSigns
from prediction.models import CHDRiskResult

MODEL_PATH = os.path.join(settings.BASE_DIR, "prediction", "final_lgb_model.txt")

FEATURE_ORDER = [
    "male",
    "age",
    "education",
    "currentSmoker",
    "cigsPerDay",
    "BPMeds",
    "prevalentStroke",
    "prevalentHyp",
    "diabetes",
    "totChol",
    "sysBP",
    "diaBP",
    "BMI",
    "heartRate",
    "glucose"
]

model = lgb.Booster(model_file=MODEL_PATH)


def get_risk_level(prob: float):
    if prob < 0.15:
        return 0, "خطر منخفض"
    elif prob < 0.30:
        return 1, "خطر متوسط"
    else:
        return 2, "خطر مرتفع"


class PredictCHDView(APIView):

    def post(self, request):
        try:
            patient_id = request.GET.get("patient_id")
            if not patient_id:
                return Response({"detail": "patient_id is required"}, status=400)
            patient = get_object_or_404(PatientDB, id=patient_id)
            last_hr = (
                VitalSigns.objects
                .filter(patient=patient, heart_rate__isnull=False)
                .order_by("-heart_rate_time")
                .first()
            )
            heart_rate = last_hr.heart_rate if last_hr else 70

            last_bp = (
                VitalSigns.objects
                .filter(
                    patient=patient,
                    systolic_pressure__isnull=False,
                    diastolic_pressure__isnull=False
                )
                .order_by("-blood_pressure_time")
                .first()
            )
            sysBP = last_bp.systolic_pressure if last_bp else 120
            diaBP = last_bp.diastolic_pressure if last_bp else 80
            bmi = patient.calculate_bmi()

            data_dict = {
                "male": 1 if patient.gender.lower() == "male" else 0,
                "age": patient.calculate_age(),
                "education": 1,
                "currentSmoker": 0,
                "cigsPerDay": 0,
                "BPMeds": 0,
                "prevalentStroke": 0,
                "prevalentHyp": 1,
                "diabetes": 0,
                "totChol": 200,
                "sysBP": sysBP,
                "diaBP": diaBP,
                "BMI": bmi if bmi else 22.0,
                "heartRate": heart_rate,
                "glucose": 95,
            }

            
            df = pd.DataFrame([data_dict])[FEATURE_ORDER]
            
            for col in ["age", "cigsPerDay", "BPMeds", "prevalentStroke", "prevalentHyp",
                        "diabetes", "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose"]:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            prob = float(model.predict(df)[0])
            risk_level, risk_label = get_risk_level(prob)
            result = CHDRiskResult.objects.create(
                        patient=patient,
                        probability=prob,
                        risk_level=risk_level,
                        risk_label=risk_label
                    )


            return Response({
                    "patient_id": patient.id,
                    "prediction": {
                        "TenYearCHD_Prob": round(prob, 4),
                        "Risk_Level": risk_level,
                        "Risk_Label": risk_label,
                        "predicted_at": result.created_at
                    }
                })

        except Exception:
            traceback.print_exc()
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DailyVitalsChartView(APIView):

    def get(self, request):
        patient_id = request.GET.get("patient_id")
        date_str = request.GET.get("date")  

        if not patient_id or not date_str:
            return Response(
                {"detail": "patient_id and date are required"},
                status=400
            )

        patient = get_object_or_404(PatientDB, id=patient_id)

        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_dt = make_aware(datetime.combine(selected_date, time.min))
        end_dt = make_aware(datetime.combine(selected_date, time.max))

        hr_data = VitalSigns.objects.filter(
            patient=patient,
            heart_rate__isnull=False,
            heart_rate_time__range=(start_dt, end_dt)
        ).order_by("heart_rate_time")

        heart_rate_series = [
            {
                "time_heat_rate":hr.heart_rate_time,      
                "heart_rate": hr.heart_rate
            }
            for hr in hr_data
        ]
        bp_data = VitalSigns.objects.filter(
            patient=patient,
            systolic_pressure__isnull=False,
            diastolic_pressure__isnull=False,
            blood_pressure_time__range=(start_dt, end_dt)
        ).order_by("blood_pressure_time")

        blood_pressure_series = [
            {
                "time_blood_pressure":bp.blood_pressure_time,
                "systolic": bp.systolic_pressure,
                "diastolic": bp.diastolic_pressure
            }
            for bp in bp_data
        ]

        risk_data = CHDRiskResult.objects.filter(
            patient=patient,
            created_at__range=(start_dt, end_dt)
        ).order_by("created_at")

        risk_series = [
            {
                "time": r.created_at,
                "probability": round(r.probability, 4),
                "risk_level": r.risk_level,
                "risk_label": r.risk_label
            }
            for r in risk_data
        ]
        return Response({
            "date": date_str,
            "heart_rate_series": heart_rate_series,
            "blood_pressure_series": blood_pressure_series,
            "risk_series": risk_series
        })
