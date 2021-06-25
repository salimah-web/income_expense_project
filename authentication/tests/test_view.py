from .test_setup import TestSetUp
from ..models import User
class TestView(TestSetUp):
    def test_user_cannot_register(self):
        res=self.client.post(self.register_url)
        self.assertEqual(res.status_code, 400)

    def test_user_can_register(self):
        res=self.client.post(self.register_url, self.user_data, format="json")
        
        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.status_code, 201)

    def test_login_with_unverified_email(self):
        self.client.post(self.register_url, self.user_data, format="json")
        res=self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(res.status_code, 401)
        

    def test_login_with_verified_email(self):
        res=self.client.post(self.register_url, self.user_data, format="json")
        email=res.data['email']
        user = User.objects.get(email=email)
        user.is_verified=True
        user.save()
        response=self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, 200)