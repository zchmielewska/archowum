from document import models


def search(phrase):
    doc_product_name = models.Document.objects.filter(product__name__icontains=phrase)
    doc_product_model = models.Document.objects.filter(product__model__icontains=phrase)
    doc_category_name = models.Document.objects.filter(category__name__icontains=phrase)
    doc_validity_start = models.Document.objects.filter(validity_start__icontains=phrase)
    doc_file_name = models.Document.objects.filter(file__icontains=phrase)
    doc_created_by = models.Document.objects.filter(created_by__username__icontains=phrase)
    doc_created_at = models.Document.objects.filter(created_at__icontains=phrase)
    all_documents = doc_product_name | doc_product_model | doc_category_name | doc_validity_start | doc_file_name \
                    | doc_created_by | doc_created_at
    documents = all_documents.distinct().order_by("-id")
    return documents
