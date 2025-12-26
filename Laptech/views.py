from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from .serializers import CreatLAPTECH, LoginLabTech
from TabebAI.auth import generate_refresh_token, set_auth_cookies


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
                return Response({"error": "غير مصرح، هذا الحساب ليس مخبري"}, status=403)

            role = 'labtech'
            request.session.flush()
            login(request, user)

            refresh_token = generate_refresh_token(user)
            access_token = str(refresh_token.access_token)
            response = Response({
                "user_id": user.id,
                "role": role,
                "access": access_token,          
            }, status=status.HTTP_200_OK)
            set_auth_cookies(response, refresh_token)

            return response
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
