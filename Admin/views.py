from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  
from django.contrib.auth import authenticate, login
from TabebAI.auth import generate_refresh_token  

class AdminLoginView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"detail": "الرجاء إدخال اسم المستخدم وكلمة المرور"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user or not user.is_superuser:
            return Response({"detail": "غير مصرح"}, status=status.HTTP_403_FORBIDDEN)

        login(request, user)

        refresh_token = generate_refresh_token(user)
        access_token = str(refresh_token.access_token)

        response = Response({
            "user_id": user.id,
            "role": "admin",
            "access": access_token
                            }, status=status.HTTP_200_OK)

        return response
