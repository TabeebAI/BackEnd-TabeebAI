from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .serializers import LoginDR, CreateDR, profil
from .models import DoctorsDB
from QR.views import IsVisitOwner


@method_decorator(ensure_csrf_cookie, name='dispatch')


class LoginDRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginDR(data=request.data)
        if ser.is_valid():
            user = ser.validated_data['DR'] 

            if hasattr(user, 'doctor_profile'):
                role = 'doctor'
            elif hasattr(user, 'labtech_profile'):
                role = 'labtech'
            else:
                role = 'unknown'

            request.session.flush()
            login(request, user)

            return Response({
                'role': role,
                'user_id': user.id,
                'sessionid': request.session.session_key,
                'csrftoken': request.META.get("CSRF_COOKIE", "")
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
        

            return Response({
                    "Message":"تم تسجيل الطبيب بنجاح ",
                    "id":doctor.id

                },status=status.HTTP_201_CREATED)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST )
    
   
