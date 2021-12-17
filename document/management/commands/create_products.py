from django.core.management.base import BaseCommand
from faker import Faker

from document import models

faker = Faker("pl_PL")


class Command(BaseCommand):
    help = "Create fake products"

    def handle(self, *args, **options):
        for _ in range(1000):
            models.Product.objects.create(name=faker.text(max_nb_chars=60), model=faker.text(max_nb_chars=20))
