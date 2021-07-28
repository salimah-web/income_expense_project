from django.shortcuts import render
from rest_framework import generics, serializers, status, views
from .serializers import RegisterSerializer, EmailVerificationSerializers, SetNewPasswordSerializers, ResetPasswordSerializers, LoginSerializer, RegisterSuperuserSerializer, EmailTokenSerializer
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
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

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
        
        return Response(user_data, status= status.HTTP_201_CREATED)

class EmailToken(generics.GenericAPIView):
    serializer_class= EmailTokenSerializer
    def post(self, request):
        user = request.data['email']
        print(user)
        print(User.objects.filter(email=user).exists())
        if User.objects.filter(email=user).exists():
            userr = User.objects.get(email=user)
            token= RefreshToken.for_user(userr).access_token
            current_site= get_current_site(request).domain
            relative_link=reverse('verify_email')
            absurl= 'http://'+ current_site+relative_link+'?token='+str(token)
            email_body = 'Hi '+ userr.username + 'Use the link below to verify your email\n' +  absurl
            data={'email_body':email_body, 'email_subject':'Verify your email', 'to_email':userr.email}
            Util.send_email(data)
            return Response({'message':'check email to verify your account'}, status= status.HTTP_200_OK)
        else:
            return Response({'message':'You have not registered'}, status= status.HTTP_400_BAD_REQUEST)
            
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializers
    token_param = openapi.Parameter('token', in_=openapi.IN_QUERY, description='description', type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param])
    def get(self, request):
        token= request.GET.get('token')
        #print(token.email)
        try:
            payload= jwt.decode(token, settings.SECRET_KEY)
            user= User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified=True
                user.save()
            return Response({'email':'account successfully activated'}, status= status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation link expired but'}, status= status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid token'}, status= status.HTTP_400_BAD_REQUEST)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestPasswordReset(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializers

    def post(self, request):
        user_email = request.data['email']
        if User.objects.filter(email=user_email).exists():
            user = User.objects.get(email=user_email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token=PasswordResetTokenGenerator().make_token(user)
            current_site= get_current_site(request).domain
            relative_link=reverse('password-reset', kwargs={'uidb64':uidb64, 'token':token})
            absurl= 'http://'+ current_site+ relative_link
            email_body = 'Hi '+ user.username + ' Use the link below to reset your password\n' +  absurl
            data={'email_body':email_body, 'email_subject':'Reset your password', 'to_email':user.email}
            Util.send_email(data)
            return Response({'sucess':'We have sent a link to your mail to reset your password'}, status=status.HTTP_200_OK)

class PasswordTokencheck(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializers
    def get(self, request, uidb64, token):
        id=smart_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(id=id)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error':'Token is not valid, please request another'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message':'valid Creditials','uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

class SetNewPassword(generics.GenericAPIView):
    serializer_class=SetNewPasswordSerializers

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':'password reset complete'}, status=status.HTTP_200_OK)