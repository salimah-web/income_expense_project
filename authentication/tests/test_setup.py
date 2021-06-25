from rest_framework.test import APITestCase
from django.urls import reverse

class TestSetUp(APITestCase):
    def setUp(self):
        self.register_url= reverse('register')
        self.login_url=reverse('login')

        self.user_data={
            'email':'sally@gmail.com',
            'username':'salima',
            'password':'gorilla'
        }

        return super().setUp()
    
    def tearDown(self):

        return super().tearDown()