from django.contrib.auth.models import User
from django.test import Client, TestCase


class TestMainView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
