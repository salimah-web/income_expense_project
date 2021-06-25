from enum import unique
from django.db import models
from django.db.models import fields
from drf_yasg.utils import param_list_to_odict
from rest_framework import serializers, validators
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes, smart_str, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

class RegisterSuperuserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, write_only= True)
    class Meta:
        model = User
        fields=['email','username','password']

    def validate(self, attrs):
        email = attrs.get('email','')
        username= attrs.get('username','')
        return attrs
    def create(self, validated_data):
        return User.objects.create_superuser(**validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, write_only= True)
    #email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields=['email','username','password']

    def validate(self, attrs):
        email = attrs.get('email','')
        username= attrs.get('username','')
        
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailTokenSerializer(serializers.Serializer):
    email=serializers.EmailField(max_length=255)

class EmailVerificationSerializers(serializers.ModelSerializer):
    token = serializers.CharField(max_length= 555)
    class Meta:
        model = User
        fields = ['token']

class LoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length= 68, write_only= True)
    username=serializers.CharField(max_length=255, read_only= True)
    tokens = serializers.CharField(max_length= 1000, read_only= True)

    class Meta:
        model = User
        fields= ['email', 'password','username','tokens']


    def validate(self, attrs):
        email = attrs.get('email','')
        password =  attrs.get('password','')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')

        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email':user.email,
            'username':user.username,
            'tokens': user.tokens
        }

class ResetPasswordSerializers(serializers.Serializer):
    email= serializers.EmailField(min_length=1)

    class Meta:
        fields= ['email']      

class SetNewPasswordSerializers(serializers.Serializer):
    password= serializers.CharField(min_length=4, write_only=True)
    token= serializers.CharField(min_length=1, write_only=True)
    uidb64= serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields= ['password','token','uidb64']      

    def validate(self, attrs):
        try:
            password=attrs.get('password','')
            token=attrs.get('token','')
            uidb64=attrs.get('uidb64','')

            id = force_str(urlsafe_base64_decode(uidb64))
            user= User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(password)
            user.save()

        except Exception as errors:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(attrs)
