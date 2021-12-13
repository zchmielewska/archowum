from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="nazwa produktu ubezpieczeniowego")
    model = models.CharField(max_length=30, verbose_name="model przepływów pieniężnych")

    def __str__(self):
        return f"{self.name} ({self.model})"


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="nazwa")

    def __str__(self):
        return self.name


class Document(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    validity_start = models.DateField()
    file = models.FileField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user", null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
