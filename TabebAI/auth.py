import datetime
import jwt
from django.conf import settings
from rest_framework.response import Response

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
class RefreshToken:
    def __init__(self, user):
        self.user = user
        self.exp = datetime.datetime.utcnow() + datetime.timedelta(days=7)
        self.token = jwt.encode(
            {"user_id": user.id, "exp": self.exp}, SECRET_KEY, algorithm=ALGORITHM
        )

    @property
    def access_token(self):
        access_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        return jwt.encode(
            {"user_id": self.user.id, "exp": access_exp}, SECRET_KEY, algorithm=ALGORITHM
        )

def generate_refresh_token(user):
    return RefreshToken(user)

def set_auth_cookies(response: Response, refresh_token: RefreshToken):

    response.set_cookie(
        key="refresh",
        value=refresh_token.token,
        httponly=True,       
        secure=False,       
        samesite="Lax",      
        max_age=7*24*60*60,  
        path="/",
    )
    return response

