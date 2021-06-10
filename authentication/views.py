from django.shortcuts import render
from rest_framework import generics, serializers, status, views
from .serializers import RegisterSerializer, EmailVerificationSerializers, LoginSerializer, RegisterSuperuserSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .util import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.

class RegisterSuperuser(generics.GenericAPIView):
    serializer_class = RegisterSuperuserSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception = True)
        
        serializer.save()

        user_data = serializer.data
        return Response({'message':'check email to verify your account'}, status= status.HTTP_201_CREATED)
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception = True)
        
        serializer.save()

        user_data = serializer.data

        user = User.objects.get(email=user_data['email'])
        token= RefreshToken.for_user(user).access_token
        current_site= get_current_site(request).domain

        relative_link=reverse('verify_email')

        
        absurl= 'http://'+ current_site+relative_link+'?token='+str(token)
        email_body = 'Hi '+ user.username + 'Use the link below to verify your email\n' +  absurl
        data={'email_body':email_body, 'email_subject':'Verify your email', 'to_email':user.email}
        Util.send_email(data)
        
        return Response({'message':'check email to verify your account'}, status= status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializers
    token_param = openapi.Parameter('token', in_=openapi.IN_QUERY, description='description', type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param])
    def get(self, request):
        token= request.GET.get('token')

        try:
            payload= jwt.decode(token, settings.SECRET_KEY)
            user= User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified=True
                user.save()

            return Response({'email':'account successfully activated'}, status= status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation link expired'}, status= status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid token'}, status= status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
