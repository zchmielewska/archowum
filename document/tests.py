from django.contrib.auth.models import User
from django.test import Client, TestCase


class TestMainView00(TestCase):
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
        self.assertEqual(response.context.get("phrase"), None)
        self.assertEqual(len(response.context.get("documents")), 0)
        self.assertEqual(response.context.get("no_documents"), 0)


class TestMainView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/")
        self.assertEqual(len(response.context.get("documents")), 5)
        self.assertEqual(response.context.get("no_documents"), 5)
        self.assertEqual(response.context.get("documents").first().id, 5)


class TestMainView02(TestCase):
    fixtures = ["02.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        self.client.force_login(user)

        response = self.client.get("/")
        self.assertEqual(len(response.context.get("documents")), 10)
        self.assertEqual(response.context.get("no_documents"), 10)
        self.assertEqual(response.context.get("documents").first().id, 12)

        response = self.client.get("/search/?phrase=file1")
        self.assertEqual(response.context.get("phrase"), "file1")
        self.assertEqual(len(response.context.get("documents")), 4)
        self.assertEqual(response.context.get("no_documents"), 4)
        self.assertEqual(response.context.get("documents").first().id, 12)
