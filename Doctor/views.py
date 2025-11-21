

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status,viewsets
from .serializers import LoginDR ,CreateDR,profil
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.authtoken.models import Token
from .models import DoctorsDB
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

class LoginDRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginDR(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['DR']  # هذا الـ User بعد التحقق

            # ===== هنا نحدد الدور =====
            if hasattr(user, 'doctor_profile'):
                role = 'doctor'
            elif hasattr(user, 'labtech_profile'):
                role = 'labtech'
            else:
                role = 'unknown'

            # إنشاء توكنات JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'role': role,         # نضيف الدور هنا
                'user_id': user.id    # يمكن إضافة ID المستخدم
            }, status=status.HTTP_200_OK)

        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

class profilDR(viewsets.ModelViewSet):
    permission_classes= [IsAuthenticated] 
    serializer_class =profil
    def get_queryset(self):
        return DoctorsDB.objects.filter(user=self.request.user)
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs) 
class CreateDoctor(APIView):
    permission_classes=[IsAdminUser]
    def post(self,request):
        ser = CreateDR(data=request.data, context={'request': request})
        if ser.is_valid():
            
            doctor =ser.save()
            token=Token.objects.get(user=doctor.user)
        

            return Response({
                    "Message":"تم تسجيل الطبيب بنجاح ",
                    "token":token.key,
                    "id":doctor.id

                },status=status.HTTP_201_CREATED)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST )
    
   
