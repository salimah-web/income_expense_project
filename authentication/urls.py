from django.urls import path
from .views import RegisterView,VerifyEmail, LoginAPIView, RegisterSuperuser, EmailToken
from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns=[
    path('register/', RegisterView.as_view(), name= 'register-admin'),
    path('register-admin/', RegisterSuperuser.as_view(), name= 'register'),
    path('verify_email/', VerifyEmail.as_view(), name= 'verify_email'),
    path('verify_email_newtoken/', EmailToken.as_view(), name= 'new-token'),
    path('login/', LoginAPIView.as_view(), name= 'login'),
    path('/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]
