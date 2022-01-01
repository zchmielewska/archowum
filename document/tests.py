from django.contrib.auth.models import User, Group
from django.test import Client, TestCase

from document import models


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


class TestMainView03(TestCase):
    fixtures = ["03.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        self.client.force_login(user)

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


class TestManageView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/")

        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/manage/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("products")), 0)
        self.assertEqual(len(response.context.get("categories")), 0)


class TestManageView02(TestCase):
    fixtures = ["02.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
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


class TestManageView03(TestCase):
    fixtures = ["03.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/manage/")

        products = response.context.get("products")
        categories = response.context.get("categories")
        self.assertEqual(len(products), 2)
        self.assertEqual(len(categories), 2)
        self.assertEqual(products.first().id, 1)
        self.assertEqual(categories.first().id, 1)


class TestAddProductView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/product/add/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/add/")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/product/add/")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/product/add/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        no_products = models.Product.objects.count()
        self.assertEqual(no_products, 0)

        data = {
            "name": "Produkt testowy",
            "model": "TEST"
        }
        response = self.client.post("/product/add/", data)
        self.assertEqual(response.url, "/manage/")

        no_products = models.Product.objects.count()
        self.assertEqual(no_products, 1)
        self.assertEqual(models.Product.objects.first().name, "Produkt testowy")


class TestEditProductView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/product/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/edit/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/product/edit/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
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


class TestDeleteProductView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/product/delete/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/product/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        products = models.Product.objects
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().model, "TEST")

        response = self.client.post("/product/delete/1")
        self.assertEqual(response.url, "/manage/")

        products = models.Product.objects
        self.assertEqual(products.count(), 0)


class TestAddCategoryView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/category/add/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/add/")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/category/add/")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/category/add/")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        no_categories = models.Category.objects.count()
        self.assertEqual(no_categories, 0)

        response = self.client.post("/category/add/", {"name": "OWU"})
        self.assertEqual(response.url, "/manage/")

        no_categories = models.Category.objects.count()
        self.assertEqual(no_categories, 1)
        self.assertEqual(models.Category.objects.first().name, "OWU")


class TestEditCategoryView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/edit/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/category/edit/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "OWU")

        response = self.client.post("/category/edit/1", {"name": "UFO"})
        self.assertEqual(response.url, "/manage/")

        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "UFO")


class TestDeleteCategoryView01(TestCase):
    fixtures = ["01.json"]

    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/category/delete/1")

        user = User.objects.create(username='testuser')
        self.client.force_login(user)
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 403)

        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)
        response = self.client.get("/category/delete/1")
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        user = User.objects.create(username='testuser')
        manager_group = Group.objects.create(name='manager')
        user.groups.add(manager_group)
        self.client.force_login(user)

        categories = models.Category.objects
        self.assertEqual(categories.count(), 1)
        self.assertEqual(categories.first().name, "OWU")

        response = self.client.post("/category/delete/1")
        self.assertEqual(response.url, "/manage/")

        categories = models.Category.objects
        self.assertEqual(categories.count(), 0)
