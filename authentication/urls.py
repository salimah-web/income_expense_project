from django.urls import path
from .views import RegisterView,VerifyEmail, LoginAPIView

urlpatterns=[
    path('register/', RegisterView.as_view(), name= 'register'),
    path('verify_email/', VerifyEmail.as_view(), name= 'verify_email'),
    path('login/', LoginAPIView.as_view(), name= 'login'),

]
