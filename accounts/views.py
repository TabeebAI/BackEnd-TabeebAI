from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from TabebAI.auth import SECRET_KEY, ALGORITHM, generate_refresh_token
from django.contrib.auth.models import User
import jwt

class RefreshAccessTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.COOKIES.get("refresh")
        if not token:
            return Response({"detail": "Refresh token not found"}, status=401)

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user = User.objects.get(id=payload["user_id"])
            refresh_token = generate_refresh_token(user)
            access_token = str(refresh_token.access_token)
            return Response({"access": access_token})
        except jwt.ExpiredSignatureError:
            return Response({"detail": "Refresh token expired"}, status=401)
        except jwt.InvalidTokenError:
            return Response({"detail": "Invalid token"}, status=401)
