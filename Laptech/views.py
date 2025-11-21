from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .serializers import CreatLAPTECH , LoginLabTech 
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken



class CreateLabTech(APIView):
    permission_classes = [IsAdminUser]  # فقط الأدمن يمكنه الإضافة

    def post(self, request):
        serializer = CreatLAPTECH(data=request.data, context={'request': request})
        if serializer.is_valid():
            labtech = serializer.save()

            # إنشاء token أو الحصول عليه إذا كان موجودًا مسبقًا
            token, _ = Token.objects.get_or_create(user=labtech.user)

            return Response({
                "message": "✅ تم تسجيل المخبري بنجاح",
                "token": token.key,
                "labtech_id": labtech.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginLabTechView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginLabTech(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['LabTech']  # الـ User بعد التحقق من البيانات

            # ===== التحقق من الدور =====
            if not hasattr(user, 'labtech_profile'):
                return Response({"error": "غير مصرح، هذا الحساب ليس مخبري"}, status=403)

            role = 'labtech'

            # إنشاء توكنات JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role,
                'user_id': user.id
            }, status=200)

        return Response(ser.errors, status=400)




