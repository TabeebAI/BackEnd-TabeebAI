from Laptech.models import LabTechDB
from Doctor.models import DoctorsDB
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny ,IsAdminUser
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import SimpleLabTechSerializer ,SimpleDoctorsSerializer
from django.db.models import Q


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "الرجاء إدخال اسم المستخدم وكلمة المرور"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if not user or not user.is_superuser:
            return Response(
                {"detail": "غير مصرح"},
                status=status.HTTP_403_FORBIDDEN
            )

        login(request, user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "user_id": user.id,
                "role": "admin",
                "access": access_token,

            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,       
            samesite="Strict", 
            max_age=7*24*60*60 
        )

        return response

class AdminGetDoctorsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        query = request.query_params.get("q")

        doctors = DoctorsDB.objects.select_related("user")

        if query:
            doctors = doctors.filter(
                Q(full_name__icontains=query) | Q(specialty__icontains=query) | Q(region__icontains=query)
            )

        serializer = SimpleDoctorsSerializer(doctors, many=True)
        return Response({
        "count_doctors": doctors.count(),
        "results": serializer.data})


class AdminGetLabTechsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        query = request.query_params.get("q")
        labtechs = LabTechDB.objects.select_related("user")

        if query:
            labtechs = labtechs.filter(
                lab_name__icontains=query
            ) | labtechs.filter(
                region__icontains=query
            )

        serializer = SimpleLabTechSerializer(labtechs, many=True)
        
        return Response({
            "count_labtechs": labtechs.count(),  
            "results": serializer.data  
        })

class AdminPatientsCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        patients_count = User.objects.filter(
            doctor_profile__isnull=True,
            labtech_profile__isnull=True
        ).count()

        return Response({"total_patients": patients_count})
