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


def save_history(document_old, document_new):
    now = timezone.now()

    if not document_new.product == document_old.product:
        models.History.objects.create(
            document=document_old,
            element="produkt",
            changed_from=document_old.product,
            changed_to=document_new.product,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document_new.category == document_old.category:
        models.History.objects.create(
            document=document_old,
            element="kategoria dokumentu",
            changed_from=document_old.category,
            changed_to=document_new.category,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document_new.validity_start == document_old.validity_start:
        models.History.objects.create(
            document=document_old,
            element="ważny od",
            changed_from=document_old.validity_start,
            changed_to=document_new.validity_start,
            changed_by=self.request.user,
            changed_at=now,
        )

    if not document_new.file == document_old.file:
        models.History.objects.create(
            document=document_old,
            element="plik",
            changed_from=document_old.file,
            changed_to=document_new.file,
            changed_by=self.request.user,
            changed_at=now,
        )

    return None
