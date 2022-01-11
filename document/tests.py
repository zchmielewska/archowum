import os
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from unittest import mock

from document import models


class ExtendedTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def log_user(self):
        user = User.objects.create(username='user123')
        self.client.force_login(user)

    def log_manager(self):
        user = User.objects.create(username='manager456')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)


class TestMainView(ExtendedTestCase):
    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/")

        self.log_user()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context.get("phrase"), None)
        self.assertEqual(len(response.context.get("documents")), 0)
        self.assertEqual(response.context.get("no_documents"), 0)


class TestMainView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        self.log_user()

        response = self.client.get("/")
        self.assertEqual(len(response.context.get("documents")), 5)
        self.assertEqual(response.context.get("no_documents"), 5)
        self.assertEqual(response.context.get("documents").first().id, 5)


class TestMainView02(ExtendedTestCase):
    fixtures = ["02.json"]

    def test_get(self):
        self.log_user()

        response = self.client.get("/")
        self.assertEqual(len(response.context.get("documents")), 10)
        self.assertEqual(response.context.get("no_documents"), 10)
        self.assertEqual(response.context.get("documents").first().id, 12)

        response = self.client.get("/search/?phrase=file1")
        self.assertEqual(response.context.get("phrase"), "file1")
        self.assertEqual(len(response.context.get("documents")), 4)
        self.assertEqual(response.context.get("no_documents"), 4)
        self.assertEqual(response.context.get("documents").first().id, 12)


class TestMainView03(ExtendedTestCase):
    fixtures = ["03.json"]

    def test_get(self):
        self.log_user()

        response = self.client.get("/search/?phrase=alamakota")
        self.assertEqual(response.context.get("no_documents"), 6)
        self.assertEqual(response.context.get("documents").first().id, 6)

        response = self.client.get("/search/?phrase=bartekmapsa")
        self.assertEqual(response.context.get("no_documents"), 6)
        self.assertEqual(response.context.get("documents").first().id, 12)

        response = self.client.get("/search/?phrase=ALA123")
        self.assertEqual(response.context.get("no_documents"), 6)
        self.assertEqual(response.context.get("documents").first().id, 6)

        response = self.client.get("/search/?phrase=swu")
        self.assertEqual(response.context.get("no_documents"), 6)
        self.assertEqual(response.context.get("documents").first().id, 12)

        response = self.client.get("/search/?phrase=01-11")
        self.assertEqual(response.context.get("no_documents"), 1)
        self.assertEqual(response.context.get("documents").first().id, 11)

        response = self.client.get("/search/?phrase=FILE7.PDF")
        self.assertEqual(response.context.get("no_documents"), 1)
        self.assertEqual(response.context.get("documents").first().id, 7)

        response = self.client.get("/search/?phrase=user2")
        self.assertEqual(response.context.get("no_documents"), 2)
        self.assertEqual(response.context.get("documents").first().id, 9)

        response = self.client.get("/search/?phrase=2012-09-04")
        self.assertEqual(response.context.get("no_documents"), 12)
        self.assertEqual(response.context.get("documents").first().id, 12)


class TestManageView(ExtendedTestCase):
    def test_get(self):
        response = self.client.get("/manage/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/manage/")

        self.log_user()
        response = self.client.get("/manage/")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/manage/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("products")), 0)
        self.assertEqual(len(response.context.get("categories")), 0)


class TestManageView02(ExtendedTestCase):
    fixtures = ["02.json"]

    def test_get(self):
        self.log_manager()
        response = self.client.get("/manage/")
        products = response.context.get("products")
        categories = response.context.get("categories")
        product = products[0]
        category = categories[0]
        self.assertEqual(len(products), 1)
        self.assertEqual(len(categories), 1)
        self.assertEqual(product.name, "Produkt testowy")
        self.assertEqual(product.model, "TEST")
        self.assertEqual(category.name, "OWU")


class TestManageView03(ExtendedTestCase):
    fixtures = ["03.json"]

    def test_get(self):
        self.log_manager()
        response = self.client.get("/manage/")
        products = response.context.get("products")
        categories = response.context.get("categories")
        self.assertEqual(len(products), 2)
        self.assertEqual(len(categories), 2)
        self.assertEqual(products.first().id, 1)
        self.assertEqual(categories.first().id, 1)


class TestAddProductView(ExtendedTestCase):
    def test_get(self):
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/add")

        self.log_user()
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/product/add")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()

        no_products = models.Product.objects.count()
        self.assertEqual(no_products, 0)

        response = self.client.get("/manage/")
        products = response.context.get("products")
        self.assertEqual(len(products), 0)

        data = {
            "name": "Produkt testowy",
            "model": "TEST"
        }
        response = self.client.post("/product/add", data)
        self.assertEqual(response.url, "/manage/")

        no_products = models.Product.objects.count()
        self.assertEqual(no_products, 1)
        self.assertEqual(models.Product.objects.first().name, "Produkt testowy")

        response = self.client.get("/manage/")
        products = response.context.get("products")
        self.assertEqual(len(products), 1)


class TestEditProductView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        response = self.client.get("/product/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/edit/1")

        self.log_user()
        response = self.client.get("/product/edit/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/product/edit/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        products = models.Product.objects
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().model, "TEST")

        data = {
            "name": "Produkt tostowy",
            "model": "TOST"
        }
        response = self.client.post("/product/edit/1", data)
        self.assertEqual(response.url, "/manage/")

        products = models.Product.objects
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().model, "TOST")


class TestDeleteProductView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/delete/1")

        self.log_user()
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()
        products = models.Product.objects
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().model, "TEST")

        response = self.client.post("/product/delete/1")
        self.assertEqual(response.url, "/manage/")

        products = models.Product.objects
        self.assertEqual(products.count(), 0)


class TestAddCategoryView(ExtendedTestCase):
    def test_get(self):
        response = self.client.get("/category/add")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/add")

        self.log_user()
        response = self.client.get("/category/add")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/category/add")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()
        no_categories = models.Category.objects.count()
        self.assertEqual(no_categories, 0)

        response = self.client.post("/category/add", {"name": "OWU"})
        self.assertEqual(response.url, "/manage/")

        no_categories = models.Category.objects.count()
        self.assertEqual(no_categories, 1)
        self.assertEqual(models.Category.objects.first().name, "OWU")


class TestEditCategoryView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/edit/1")

        self.log_user()
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()
        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "OWU")

        response = self.client.post("/category/edit/1", {"name": "UFO"})
        self.assertEqual(response.url, "/manage/")

        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "UFO")


class TestDeleteCategoryView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/delete/1")

        self.log_user()
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()

        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "OWU")

        response = self.client.post("/category/delete/1")
        self.assertEqual(response.url, "/manage/")

        categories = models.Category.objects
        self.assertEqual(categories.count(), 0)


class TestAddDocumentView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/document/add")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/document/add")

        self.log_user()
        response = self.client.get("/document/add")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/document/add")
        self.assertEqual(response.status_code, 200)

    def post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        documents = models.Document.objects
        self.assertEqual(documents.count(), 5)

        data = {
            "product": "1",
            "category": "1",
            "validity_start": "2022-01-06",
            "file": SimpleUploadedFile("owu.pdf", b"file_content", content_type="pdf")
        }
        response = self.client.post("/document/add", data)
        self.assertEqual(response.url, "/")
        documents = models.Document.objects
        self.assertEqual(documents.count(), 6)
        new_document = documents.get(pk=6)
        self.assertEqual(new_document.product.name, "Produkt testowy")

    @mock.patch.dict(os.environ, {"DEPLOYMENT_TYPE": "LOCAL"})
    def test_post_local(self):
        self.post()

    # def tearDown(self):
    #     new_document = models.Document.objects.get(pk=6)
    #     new_document.delete()

    # @mock.patch.dict(os.environ, {"DEPLOYMENT_TYPE": "AWS"})
    # def test_post_aws(self):
    #     self.post()


#
# def test_post_local(self):
#     self.post()
#
# @mock.patch.dict(os.environ, {"DEPLOYMENT_TYPE": "AWS"})
# def test_post_aws(self):
#     self.post()
class TestEditDocumentView03(TestCase):
    fixtures = ["03.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/document/edit/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        documents = models.Document.objects
        self.assertEqual(documents.count(), 12)
        document = documents.get(pk=1)
        self.assertEqual(document.product.name, "Produkt alamakota")
        histories = models.History.objects
        self.assertEqual(histories.count(), 0)

        data = {
            "product": "2",
            "category": "1",
            "validity_start": "2022-01-01",
            "file": SimpleUploadedFile("file1.pdf", b"file_content", content_type="pdf")
        }

        response = self.client.post("/document/edit/1", data)
        self.assertEqual(response.url, "/document/1")

        documents = models.Document.objects
        self.assertEqual(documents.count(), 12)
        document = documents.get(pk=1)
        self.assertEqual(document.product.name, "Produkt bartekmapsa")

        histories = models.History.objects
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.document_id, 1)
        self.assertEqual(history.element, "produkt")
        self.assertEqual(history.changed_from, str(models.Product.objects.get(pk=1)))
        self.assertEqual(history.changed_to, str(models.Product.objects.get(pk=2)))


class TestDeleteDocumentView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/document/delete/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        documents = models.Document.objects
        self.assertEqual(documents.count(), 5)

        response = self.client.post("/document/delete/1")
        self.assertEqual(response.url, "/")

        documents = models.Document.objects
        self.assertEqual(documents.count(), 4)


class TestDocumentDetailView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/document/1")
        self.assertEqual(response.status_code, 200)


class TestRegisterView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.assertEqual(User.objects.count(), 0)

        data = {
            "username": "test_user",
            "password": "123",
            "password2": "123"
        }
        response = self.client.post("/register/", data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.url, "/")

        response = self.client.post("/register/", data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        data = {
            "username": "test_user2",
            "password": "123",
            "password2": "1234"
        }
        response = self.client.post("/register/", data)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)


class TestLoginView(TestCase):
    def test_get(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post("/login/", {"username": "test", "password": "test"})
        self.assertEqual(response.status_code, 200)

        User.objects.create_user(username="test", password="test")
        response = self.client.post("/login/", {"username": "test", "password": "test"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")


class TestLogout(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

