

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import LoginDR ,CreateDR
from rest_framework.permissions import IsAuthenticated ,IsAdminUser



class LoginDRViwe(APIView):
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


class CreateDoctor(APIView):
    permission_classes=[IsAdminUser]

    def post(self,request):

   
        ser = CreateDR(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response ({
                    "Message":"تم تسجيل الطبيب بنجاح "
                },status=status.HTTP_201_CREATED)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST )
    
    