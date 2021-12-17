from django.core.management.base import BaseCommand
from faker import Faker

from document import models

faker = Faker("pl_PL")


class Command(BaseCommand):
    help = "Create fake document categories"

    def handle(self, *args, **options):
        for _ in range(10):
            models.Category.objects.create(name=faker.word())
