from django.contrib.auth import login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny ,IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token

from .serializers import LoginDR ,profil, CreateDR
from TabebAI.auth import generate_refresh_token, set_auth_cookies
from rest_framework import viewsets
from .models import DoctorsDB

@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginDRView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginDR(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["DR"]

        if hasattr(user, "doctor_profile"):
            role = "doctor"
        elif hasattr(user, "labtech_profile"):
            role = "labtech"
        else:
            role = "unknown"

        request.session.flush()
        login(request, user)

        refresh_token = generate_refresh_token(user)
        access_token = str(refresh_token.access_token)

        response = Response(
            {
                "user_id": user.id,
                "role": role,
                "access": access_token, 
                "sessionid": request.session.session_key,
                "csrftoken": request.META.get("CSRF_COOKIE", ""),
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, refresh_token)

        return response
          
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
    
   
