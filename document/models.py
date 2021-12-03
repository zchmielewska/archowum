from django.db import models


class Product(models.Model):
    model = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True)


class Category(models.Model):
    name = models.CharField(max_length=100)


class Document(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    validity_start = models.DateField()
    file = models.FileField()
