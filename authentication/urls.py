from django.urls import path
from .views import RegisterView,VerifyEmail, LoginAPIView, RegisterSuperuser, EmailToken, SetNewPassword, PasswordTokencheck, RequestPasswordReset
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns=[
    path('register/', RegisterView.as_view(), name= 'register'),
    path('register-admin/', RegisterSuperuser.as_view(), name= 'register-admin'),
    path('verify_email/', VerifyEmail.as_view(), name= 'verify_email'),
    path('verify_email_newtoken/', EmailToken.as_view(), name= 'new-token'),
    path('login/', LoginAPIView.as_view(), name= 'login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('request-password-reset/', RequestPasswordReset.as_view(), name= 'request-password-reset'),
    path('password-reset/<uidb64>/<token>/', PasswordTokencheck.as_view(), name= 'password-reset'),
    path('set-new-password/', SetNewPassword.as_view(), name= 'set-new-password'),


]
