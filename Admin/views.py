from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken

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
