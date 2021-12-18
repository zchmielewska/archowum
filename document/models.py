from django.conf import settings
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=60, verbose_name="nazwa produktu ubezpieczeniowego")
    model = models.CharField(max_length=20, verbose_name="model przepływów pieniężnych")

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        ordering = ["name"]


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="nazwa")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Document(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="produkt")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="kategoria")
    validity_start = models.DateField(verbose_name="ważny od")
    file = models.FileField(verbose_name="plik")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="create_user")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    class Meta:
        unique_together = ("product", "category", "validity_start")


class History(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name="dokument")
    element = models.CharField(max_length=100)
    changed_from = models.CharField(max_length=100)
    changed_to = models.CharField(max_length=100)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="change_user")
    changed_at = models.DateTimeField(auto_now_add=True)
