from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer

class MyNotifications(APIView):
    def get(self, request):
        notifs = Notification.objects.filter(patient=request.user.patient_profile).order_by('-created_at')
        return Response(NotificationSerializer(notifs, many=True).data)
