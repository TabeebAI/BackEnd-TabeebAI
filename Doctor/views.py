

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status,viewsets
from .serializers import LoginDR ,CreateDR,profil
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.authtoken.models import Token
from .models import DoctorsDB
class LoginDRViwe(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        ser =LoginDR(data=request.data)
        if ser.is_valid():
            DR=ser.validated_data['DR']
            refresh=RefreshToken.for_user(DR)
            return Response({
                'refresh':str(refresh),
                'access':str(refresh.access_token),
            },status=status.HTTP_200_OK)
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
    
   
