import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from document import models

faker = Faker("pl_PL")


class Command(BaseCommand):
    help = "Create fake documents"

    def handle(self, *args, **options):

        for _ in range(2000):
            models.Document.objects.create(
                product=random.choice(models.Product.objects.all()),
                category=random.choice(models.Category.objects.all()),
                validity_start=faker.date(),
                file=faker.file_name(),
                created_by=random.choice(User.objects.all())
            )
