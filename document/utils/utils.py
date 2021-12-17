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
