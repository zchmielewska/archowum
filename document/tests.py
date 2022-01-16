import datetime
import os
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

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

    def test_post(self):
        self.log_manager()
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
        document = documents.last()
        self.assertEqual(document.product.name, "Produkt testowy")
        self.assertEqual(document.file.name, "owu.pdf")
        document.delete()

    def test_post_add_document_with_duplicated_filename(self):
        open("media/file1.pdf", "x")
        self.log_manager()
        self.assertEqual(models.Document.objects.count(), 5)
        data = {
            "product": "1",
            "category": "1",
            "validity_start": "2022-01-06",
            "file": SimpleUploadedFile("file1.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/add", data)
        self.assertEqual(models.Document.objects.count(), 6)
        document = models.Document.objects.last()
        self.assertNotEqual(document.file.name, "file1.pdf")
        document.delete()
        os.remove("media/file1.pdf")

    def test_post_add_document_with_filename_with_spaces(self):
        self.log_manager()
        self.assertEqual(models.Document.objects.count(), 5)
        data = {
            "product": "1",
            "category": "1",
            "validity_start": "2022-01-06",
            "file": SimpleUploadedFile("file 1.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/add", data)
        self.assertEqual(models.Document.objects.count(), 6)
        document = models.Document.objects.last()
        self.assertEqual(document.file.name, "file_1.pdf")
        document.delete()

    def test_post_add_document_with_duplicated_metadata(self):
        self.log_manager()
        self.assertEqual(models.Document.objects.count(), 5)
        data = {
            "product": "1",
            "category": "1",
            "validity_start": "2022-01-01",
            "file": SimpleUploadedFile("file999.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/add", data)
        self.assertEqual(models.Document.objects.count(), 5)


class TestEditDocumentView03(ExtendedTestCase):
    fixtures = ["03.json"]

    def test_get(self):
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/document/edit/1")

        self.log_user()
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/document/edit/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()
        documents = models.Document.objects
        self.assertEqual(documents.count(), 12)
        document = documents.get(pk=1)
        self.assertEqual(document.product.name, "Produkt alamakota")
        self.assertEqual(models.History.objects.count(), 0)

    def test_post_edit_document01_change_product(self):
        self.log_manager()
        document = models.Document.objects.get(pk=1)
        data = {
            "product": "2",
            "category": document.category.id,
            "validity_start": document.validity_start,
            "file": document.file.name
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
        document.delete()

    def test_post_edit_document02_change_file(self):
        self.log_manager()
        document = models.Document.objects.get(pk=2)
        data = {
            "product": document.product.id,
            "category": document.category.id,
            "validity_start": document.validity_start,
            "file": SimpleUploadedFile("file999.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/edit/2", data)
        document = models.Document.objects.get(pk=2)
        self.assertEqual(document.file.name, "file999.pdf")

        histories = models.History.objects
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.document_id, 2)
        self.assertEqual(history.element, "plik")
        self.assertEqual(history.changed_from, "file2.pdf")
        self.assertEqual(history.changed_to, "file999.pdf")
        document.delete()

    def test_post_edit_document03_no_changes(self):
        self.log_manager()
        document_before_edit = models.Document.objects.get(pk=3)
        data = {
            "product": "1",
            "category": "1",
            "validity_start": "2022-01-03",
            "file": SimpleUploadedFile("file3.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/edit/3", data)
        document_after_edit = models.Document.objects.get(pk=3)
        self.assertEqual(document_before_edit, document_after_edit)
        self.assertEqual(models.History.objects.count(), 0)
        document_after_edit.delete()

    def test_post_edit_document04_change_file_with_duplicated_filename(self):
        self.log_manager()
        open("media/file12.pdf", "x")
        document = models.Document.objects.get(pk=4)
        data = {
            "product": document.product.id,
            "category": document.category.id,
            "validity_start": document.validity_start,
            "file": SimpleUploadedFile("file12.pdf", b"file_content", content_type="pdf")
        }
        self.client.post("/document/edit/4", data)
        document = models.Document.objects.get(pk=4)
        self.assertNotEqual(document.file.name, "file12.pdf")

        histories = models.History.objects
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.document_id, 4)
        self.assertEqual(history.element, "plik")
        self.assertEqual(history.changed_from, "file4.pdf")
        self.assertNotEqual(history.changed_to, "file12.pdf")
        os.remove("media/file12.pdf")
        document.delete()

    def test_post_edit_document05_change_category(self):
        self.log_manager()
        document = models.Document.objects.get(pk=5)
        data = {
            "product": document.product.id,
            "category": "2",
            "validity_start": document.validity_start,
            "file": document.file.name
        }
        response = self.client.post("/document/edit/5", data)
        self.assertEqual(response.url, "/document/5")

        documents = models.Document.objects
        self.assertEqual(documents.count(), 12)
        document = documents.get(pk=5)
        self.assertEqual(document.category.name, "SWU")

        histories = models.History.objects
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.document_id, 5)
        self.assertEqual(history.element, "kategoria dokumentu")
        self.assertEqual(history.changed_from, "OWU")
        self.assertEqual(history.changed_to, "SWU")
        document.delete()

    def test_post_edit_document06_change_valid_from(self):
        self.log_manager()
        document = models.Document.objects.get(pk=6)
        data = {
            "product": document.product.id,
            "category": document.category.id,
            "validity_start": "1989-09-21",
            "file": document.file.name
        }
        response = self.client.post("/document/edit/6", data)
        self.assertEqual(response.url, "/document/6")

        documents = models.Document.objects
        self.assertEqual(documents.count(), 12)
        document = documents.get(pk=6)
        self.assertEqual(document.validity_start, datetime.date(1989, 9, 21))

        histories = models.History.objects
        self.assertEqual(histories.count(), 1)
        history = histories.first()
        self.assertEqual(history.document_id, 6)
        self.assertEqual(history.element, "ważny od")
        self.assertEqual(history.changed_from, "2022-01-06")
        self.assertEqual(history.changed_to, "1989-09-21")
        document.delete()


class TestDeleteDocumentView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/document/delete/1")

        self.log_user()
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 403)

        self.log_manager()
        response = self.client.get("/document/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.log_manager()
        self.assertEqual(models.Document.objects.count(), 5)
        response = self.client.post("/document/delete/1")
        self.assertEqual(response.url, "/")
        self.assertEqual(models.Document.objects.count(), 4)


class TestDocumentDetailView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        self.log_user()
        response = self.client.get("/document/1")
        self.assertEqual(response.status_code, 200)


class TestDownloadDocumentView01(ExtendedTestCase):
    fixtures = ["01.json"]

    def test_get(self):
        self.log_user()
        response = self.client.get("/download/1")
        self.assertEqual(response.status_code, 404)

        open("media/file1.pdf", "x")
        response = self.client.get("/download/1")
        self.assertEqual(response.status_code, 200)
        os.remove("media/file1.pdf")


class TestRegisterView(ExtendedTestCase):
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


class TestLoginView(ExtendedTestCase):
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


class TestLogout(ExtendedTestCase):
    def test_get(self):
        self.log_user()
        response = self.client.get("/logout/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
