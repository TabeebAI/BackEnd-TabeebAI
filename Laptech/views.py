from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from .serializers import CreatLAPTECH, LoginLabTech
from rest_framework_simplejwt.tokens import RefreshToken


class CreateLabTech(APIView):
    permission_classes = [IsAdminUser] 

    def post(self, request):
        serializer = CreatLAPTECH(data=request.data, context={'request': request})
        if serializer.is_valid():
            labtech = serializer.save()
            return Response({
                "message": "✅ تم تسجيل المخبري بنجاح",
                "labtech_id": labtech.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginLabTechView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginLabTech(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['LabTech']  

            if not hasattr(user, 'labtech_profile'):
                return Response(
                    {"error": "غير مصرح، هذا الحساب ليس مخبري"}, 
                    status=status.HTTP_403_FORBIDDEN
                )

            role = 'labtech'
            request.session.flush()
            login(request, user)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response(
                {
                    "user_id": user.id,
                    "role": role,
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

        return Response(
            ser.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
