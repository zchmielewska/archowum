from django.utils import timezone

from document import models


def search(phrase):
    d1 = models.Document.objects.filter(id__icontains=phrase)
    d2 = models.Document.objects.filter(product__name__icontains=phrase)
    d3 = models.Document.objects.filter(product__model__icontains=phrase)
    d4 = models.Document.objects.filter(category__name__icontains=phrase)
    d5 = models.Document.objects.filter(validity_start__icontains=phrase)
    d6 = models.Document.objects.filter(file__icontains=phrase)
    d7 = models.Document.objects.filter(created_by__username__icontains=phrase)
    d8 = models.Document.objects.filter(created_at__icontains=phrase)
    all_documents = d1 | d2 | d3 | d4 | d5 | d6 | d7 | d8
    documents = all_documents.distinct().order_by("-id")
    return documents


def save_historyOld(document1, document2, self):
    now = timezone.now()

    if not document1.product == document2.product:
        models.History.objects.create(
            document=document1,
            element="produkt",
            changed_from=document1.product,
            changed_to=document2.product,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document1.category == document2.category:
        models.History.objects.create(
            document=document1,
            element="kategoria dokumentu",
            changed_from=document1.category,
            changed_to=document2.category,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document1.validity_start == document2.validity_start:
        models.History.objects.create(
            document=document1,
            element="ważny od",
            changed_from=document1.validity_start,
            changed_to=document2.validity_start,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document1.file == document2.file:
        models.History.objects.create(
            document=document1,
            element="plik",
            changed_from=document1.file,
            changed_to=document2.file,
            changed_by=self.request.user,
            changed_at=now,
        )

    return None


def save_history(data1, data2, user):
    now = timezone.now()

    if not data1["product_id"] == data2["product_id"]:
        models.History.objects.create(
            document_id=data1["id"],
            element="produkt",
            changed_from=models.Product.objects.get(id=data1["product_id"]),
            changed_to=models.Product.objects.get(id=data2["product_id"]),
            changed_by=user,
            changed_at=now,
        )

    if not data1["category_id"] == data2["category_id"]:
        models.History.objects.create(
            document_id=data1["id"],
            element="kategoria dokumentu",
            changed_from=models.Category.objects.get(id=data1["category_id"]),
            changed_to=models.Category.objects.get(id=data2["category_id"]),
            changed_by=user,
            changed_at=now,
        )

    if not data1["validity_start"] == data2["validity_start"]:
        models.History.objects.create(
            document_id=data1["id"],
            element="ważny od",
            changed_from=data1["validity_start"],
            changed_to=data2["validity_start"],
            changed_by=user,
            changed_at=now,
        )

    if not data1["file"] == data2["file"]:
        models.History.objects.create(
            document_id=data1["id"],
            element="plik",
            changed_from=data1["file"],
            changed_to=data2["file"],
            changed_by=user,
            changed_at=now,
        )

    return None
